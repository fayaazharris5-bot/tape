# -*- coding: utf-8 -*-
"""Add second charts (viz2) to the structural terms.

Each one draws the COUNTER-CASE: the chart that looks the same as the
first right up until it resolves the other way. That is what every one of
these entries' "Where people get fooled:" paragraph already claims in
prose, and a reader who only ever sees the working example learns the
pattern as a signal rather than as a description.

viz2 renders in the detail panel only, never in the grid, so the grid
chart count is unchanged and no test constant moves.

Reuses the existing engine's spec format — no second renderer.
Idempotent: a term that already has viz2 is skipped.

    py -3 add_viz2.py
"""
import io, re, sys

SRC = 'index.html'

# {name: (chart-spec-literal, caption)}
VIZ2 = {
"Liquidity sweep": (
 '{k:"c",d:[[96,98,95,97],[97,100,96.5,99],[99,101,98,100.5],[100.5,103,100,102],'
 '[102,104,101.5,103.5],[103.5,106,103,105.5],[105.5,108,105,107.5],[107.5,110,107,109]],'
 'hl:[{p:104,t:"prior high",c:"a"}]}',
 "The same poke through the same high — but this one closed above it and kept going. "
 "Up to that close the two charts are the same picture."),

"Order block": (
 '{k:"c",d:[[100,101,97,98],[98,103,97.5,102],[102,106,101,105],[105,107,103,104],'
 '[104,105,99,100],[100,101,96,97],[97,98,93,94],[94,95,91,92]],'
 'bx:[{i0:0,i1:0,p0:97,p1:101,t:"order block",c:"a"}]}',
 "Price returned to the last down candle before the rally and went straight through it. "
 "Same zone, drawn by the same rule."),

"Fair value gap": (
 '{k:"c",d:[[96,98,95,97],[97,104,96.8,103],[103.5,106,103.2,105],[105,107,104,106],'
 '[106,109,105.5,108],[108,111,107.5,110],[110,112,109,111],[111,114,110,113]],'
 'zn:[{p0:98,p1:103.2,t:"never filled",c:"s"}]}',
 "A three-candle gap price left behind and never came back to. Gaps are everywhere; "
 "filling them is not a rule."),

"Spring": (
 '{k:"c",d:[[100,101,98,99],[99,100,97,98],[98,99,95.2,96],[96,97,95.1,95.5],'
 '[95.5,96,92,93],[93,94,90,91],[91,92,88,89],[89,90,86,87]],'
 'hl:[{p:95.1,t:"range floor",c:"a",la:true,below:true}]}',
 "The same dip through the same floor, with no reclaim. A spring and a breakdown are "
 "identical until the close that follows."),

"Engulfing": (
 '{k:"c",d:[[104,105,101,102],[101.5,106,101,105.5],[105.5,106,103,104],[104,104.5,101,101.5],'
 '[101.5,102,98,99],[99,100,96,97],[97,98,95,96],[96,97,94,95]],'
 'bx:[{i0:1,i1:1,p0:101,p1:106,t:"bullish engulfing",c:"u"}]}',
 "A textbook bullish engulfing that resolved downward. The pattern describes two bars "
 "that have already happened."),

"Hammer": (
 '{k:"c",d:[[104,105,101,102],[102,103,96,102.5],[102.5,103,100,101],[101,102,98,99],'
 '[99,100,95,96],[96,97,93,94],[94,95,91,92],[92,93,90,91]],'
 'bx:[{i0:1,i1:1,p0:96,p1:103,t:"hammer",c:"u"}]}',
 "Same long lower wick, same close back near the high — and the low gave way three "
 "bars later."),

"Breakout": (
 '{k:"c",d:[[98,100,97,99],[99,101,98,100],[100,102,99,101],[101,103,100,102],'
 '[102,105,101.5,103],[103,104.2,100,100.5],[100.5,101,97,98],[98,99,95,96]],'
 'hl:[{p:104,t:"level",c:"a"}]}',
 "The same level, broken by the same amount, closing back inside. Nothing about the "
 "level changed — only what came after it."),

"Drawdown": (
 '{k:"e",base:0,s:[{v:[100,92,78,64,50,58,70,84,100],c:"d",t:"−50%, then +100% to get back"}]}',
 "A 50% fall needs a 100% rise to return to the same place. The two legs look the same "
 "size on the chart and are not the same size in percent."),

"Premium / discount": (
 '{k:"c",d:[[96,99,95,98],[98,101,97.5,100],[100,103,99,102],[102,105,101,104],'
 '[104,107,103,106],[106,109,105,108],[108,111,107,110],[110,113,109,112]],'
 'hl:[{p:100,t:"equilibrium of the first leg",c:"a"}]}',
 "In a strong trend price can spend the whole move above equilibrium. Waiting for "
 "discount would have meant no trade at all."),
}


def esc_js(t):
    return t.replace('\\', '\\\\').replace('"', '\\"')


def find_object_end(s, start):
    """Index of the brace closing the object that opens at s[start]=='{',
    ignoring braces inside JS string literals."""
    depth, i, in_str, quote = 0, start, False, ''
    while i < len(s):
        ch = s[i]
        if in_str:
            if ch == '\\':
                i += 2
                continue
            if ch == quote:
                in_str = False
        elif ch in '"\'':
            in_str, quote = True, ch
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return -1


def main():
    s = io.open(SRC, encoding='utf-8').read()
    added, skipped, missing = [], [], []
    for name, (spec, cap) in VIZ2.items():
        m = re.search(r'\{t:"' + re.escape(name) + r'",c:"[a-z0-9]+"', s)
        if not m:
            missing.append(name)
            continue
        end = find_object_end(s, m.start())
        if end < 0:
            missing.append(name + ' (unbalanced)')
            continue
        body = s[m.start():end]
        if 'viz2:' in body:
            skipped.append(name)
            continue
        ins = ',viz2:[{v:' + spec + ',cap:"' + esc_js(cap) + '"}]'
        s = s[:end] + ins + s[end:]
        added.append(name)

    if added:
        io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added:   %d  %s' % (len(added), ', '.join(added)))
    print('skipped: %d  %s' % (len(skipped), ', '.join(skipped)))
    print('missing: %d  %s' % (len(missing), ', '.join(missing)))
    return 1 if missing else 0


sys.exit(main())
