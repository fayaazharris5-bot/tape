# -*- coding: utf-8 -*-
"""Chart the bearish counterparts, and the pairs that had no chart at all.

The corpus had a systematic tilt: hammer was charted and shooting star
and hanging man were not; engulfing was charted and bearish engulfing was
not; spring was charted and upthrust was not. Several classic pairs —
double top/bottom, head and shoulders and its inverse, bull and bear
flag — had no chart on either side.

A reader who only ever sees the bullish illustration learns the shape in
one direction. These add the other side, drawn to the same standard.

Hanging man deliberately uses the SAME candle shape as hammer: the
distinction is the context it arrives in, and the chart should show that
rather than describe it.

Reuses the existing engine. Idempotent. Adds grid figures, so
EXPECT_CHARTS moves.

    py -3 add_bear.py
"""
import io, re, sys
from add_viz2 import find_object_end, esc_js

SRC = 'index.html'

# name: (chart spec, caption)
CHARTS = {
"Shooting star": (
 '{k:"c",d:[[96,99,95,98],[98,101,97,100],[100,103,99,102],[102,104,101,103],'
 '[103,110,102.5,104],[104,105,100,101],[101,102,97,98],[98,99,95,96]],'
 'bx:[{i0:4,i1:4,p0:102.5,p1:110,t:"shooting star",c:"d"}]}',
 "A long upper wick with the close back down near the open, after an advance. It "
 "records buyers being pushed back within the bar — nothing more than that."),

"Hanging man": (
 '{k:"c",d:[[96,99,95,98],[98,101,97,100],[100,103,99,102],[102,105,101,104],'
 '[104,105,98,104.5],[104.5,105,101,102],[102,103,99,100],[100,101,96,97]],'
 'bx:[{i0:4,i1:4,p0:98,p1:105,t:"hanging man",c:"d"}]}',
 "The same candle shape as a hammer. The only difference is that this one arrived "
 "after an advance rather than a decline — the context is the entire distinction."),

"Bearish engulfing": (
 '{k:"c",d:[[96,99,95,98],[98,101,97,100],[100,103,99,102],[102,104,101,103.5],'
 '[104,105,99,99.5],[99.5,100,96,97],[97,98,94,95],[95,96,92,93]],'
 'bx:[{i0:4,i1:4,p0:99,p1:105,t:"bearish engulfing",c:"d"}]}',
 "A down candle whose body covers the prior up candle's. The mirror of the bullish "
 "case, and it describes two bars that have already closed."),

"Upthrust": (
 '{k:"c",d:[[100,102,99,101],[101,103,100,102],[102,104.9,101,104],[104,104.9,102,103],'
 '[103,108,102.5,103.5],[103.5,104,100,101],[101,102,98,99],[99,100,96,97]],'
 'hl:[{p:104.9,t:"range high",c:"a"}]}',
 "A poke above the range top that closes back inside — the mirror of a spring, and "
 "the same ambiguity: it is indistinguishable from a breakout until the close."),

"Double top": (
 '{k:"c",d:[[96,99,95,98],[98,104.8,97,104],[104,104.9,101,102],[102,103,99,100],'
 '[100,104.8,99,104],[104,104.9,100,101],[101,102,97,98],[98,99,94,95]],'
 'hl:[{p:104.9,t:"two highs, same level",c:"a"},{p:99,t:"neckline",c:"d",la:true,below:true}]}',
 "Two attempts at the same level and a close below the low between them. Where you "
 "draw the neckline decides when this counts as complete."),

"Double bottom": (
 '{k:"c",d:[[104,105,101,102],[102,103,95.2,96],[96,99,95.1,98],[98,101,97,100],'
 '[100,101,95.2,96],[96,99,95.1,98],[98,102,97,101],[101,104,100,103]],'
 'hl:[{p:95.1,t:"two lows, same level",c:"a",la:true,below:true},{p:101,t:"neckline",c:"u"}]}',
 "The mirror image: two tests of one level and a close above the high between them."),

"Head and shoulders": (
 '{k:"c",d:[[96,101,95,100],[100,101,97,98],[98,106,97,105],[105,106,99,100],'
 '[100,104,99,103],[103,104,98,99],[99,100,95,96],[96,97,92,93]],'
 'hl:[{p:98.5,t:"neckline",c:"d",la:true,below:true}]}',
 "A high, a higher high, then a lower high — with a close below the line under them. "
 "The pattern is three swings; the neckline is a drawing choice."),

"Inverse head and shoulders": (
 '{k:"c",d:[[104,105,99,100],[100,103,99,102],[102,103,94,95],[95,101,94,100],'
 '[100,101,96,97],[97,102,96,101],[101,105,100,104],[104,108,103,107]]}',
 "The same three-swing structure upside down: a low, a lower low, then a higher low."),

"Bull flag": (
 '{k:"c",d:[[95,103,94,102],[102,104,101,103],[103,103.5,101,101.5],[101.5,102.5,100.5,101],'
 '[101,102,100,100.5],[100.5,104,100,103.5],[103.5,107,103,106],[106,109,105,108]],'
 'bx:[{i0:2,i1:4,p0:100,p1:103.5,t:"the flag",c:"a"}]}',
 "A sharp advance, then a tight drift against it on smaller ranges. The drift being "
 "orderly is the whole observation."),

"Bear flag": (
 '{k:"c",d:[[105,106,97,98],[98,99,96,97],[97,99,96.5,98.5],[98.5,99.5,97.5,99],'
 '[99,100,98,99.5],[99.5,100,96,96.5],[96.5,97,93,94],[94,95,91,92]],'
 'bx:[{i0:2,i1:4,p0:96.5,p1:100,t:"the flag",c:"a"}]}',
 "The mirror: a sharp decline, then a shallow orderly drift back up against it."),
}


def main():
    s = io.open(SRC, encoding='utf-8').read()
    added, skipped, missing = [], [], []
    for name, (spec, cap) in CHARTS.items():
        m = re.search(r'\{t:"' + re.escape(name) + r'",c:"[a-z0-9]+"', s)
        if not m:
            missing.append(name)
            continue
        end = find_object_end(s, m.start())
        if end < 0:
            missing.append(name + ' (unbalanced)')
            continue
        if ',v:{' in s[m.start():end]:
            skipped.append(name)
            continue
        ins = ',v:' + spec + ',cap:"' + esc_js(cap) + '"'
        s = s[:end] + ins + s[end:]
        added.append(name)

    if added:
        io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added:   %d  %s' % (len(added), ', '.join(added)))
    print('skipped: %d  %s' % (len(skipped), ', '.join(skipped)))
    print('missing: %d  %s' % (len(missing), ', '.join(missing)))
    print('NOTE: each adds one grid figure — update EXPECT_CHARTS.')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
