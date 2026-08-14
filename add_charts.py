# -*- coding: utf-8 -*-
"""Give the three structural terms that had no chart at all both charts.

Break of structure, Change of character and False breakout are among the
most-referenced terms in the price-action vocabulary and shipped with no
visual. Each gets a primary chart plus the counter-case, on the same
principle as add_viz2.py: the version that worked and the version that
looks identical and does not.

These DO add figures to the grid, so EXPECT_CHARTS in test.js moves.
That is an intended content change and is commented there.

Reuses the existing engine. Idempotent.

    py -3 add_charts.py
"""
import io, re, sys
from add_viz2 import find_object_end, esc_js   # same parser, one definition

SRC = 'index.html'

# {name: (primary spec, primary caption, counter spec, counter caption)}
CHARTS = {
"Break of structure": (
 '{k:"c",d:[[96,99,95,98],[98,100,97,99],[99,101,98,100],[100,102,99,101],'
 '[101,102.5,99.5,100],[100,101,98.5,99.5],[99.5,104,99,103],[103,105,102,104]],'
 'hl:[{p:102,t:"prior swing high",c:"a"}]}',
 "A close beyond the prior swing high, not a wick through it. Fix how many bars either "
 "side make a swing before any of this is a rule.",
 '{k:"c",d:[[96,99,95,98],[98,100,97,99],[99,101,98,100],[100,102,99,101],'
 '[101,102.5,99.5,100],[100,101,98.5,99.5],[99.5,103.5,99,101.5],[101.5,102,99,99.5]],'
 'hl:[{p:102,t:"prior swing high",c:"a"}]}',
 "The same high exceeded by the same amount intrabar, with the close back underneath. "
 "Whether that counts is a rule you set in advance, or one you set afterwards."),

"Change of character": (
 '{k:"c",d:[[104,106,103,105],[105,107,104,106],[106,108,105,107],[107,108,105.5,106],'
 '[106,107,104,104.5],[104.5,105,102,102.5],[102.5,103,100,100.5],[100.5,101,99,99.5]],'
 'hl:[{p:104,t:"low that was holding",c:"a"}]}',
 "The first close below a low that had been holding. It is the earliest structural "
 "signal, which is also why it is the one most often wrong.",
 '{k:"c",d:[[96,99,95,98],[98,101,97,100],[100,103,99,102],[102,103,100,101],'
 '[101,102,98,98.5],[98.5,101,98,100.5],[100.5,104,100,103],[103,106,102,105]],'
 'hl:[{p:99,t:"low that was holding",c:"a"}]}',
 "The same first close below the same low — and the uptrend carried on. At some "
 "timeframe a strong trend produces these continuously."),

"False breakout": (
 '{k:"c",d:[[98,100,97,99],[99,101,98,100],[100,102,99,101],[101,103,100,102],'
 '[102,105,101.5,103],[103,104.2,100,100.5],[100.5,101,97,98],[98,99,95,96]],'
 'hl:[{p:104,t:"level",c:"a"}]}',
 "Through the level intrabar, closed back inside, then away in the other direction.",
 '{k:"c",d:[[98,100,97,99],[99,101,98,100],[100,102,99,101],[101,103,100,102],'
 '[102,105,101.5,104.5],[104.5,107,104,106],[106,109,105,108],[108,111,107,110]],'
 'hl:[{p:104,t:"level",c:"a"}]}',
 "The same level, broken by the same amount — and it held. The difference between the "
 "two only exists after the close."),
}


def main():
    s = io.open(SRC, encoding='utf-8').read()
    added, skipped, missing = [], [], []
    for name, (v, cap, v2, cap2) in CHARTS.items():
        m = re.search(r'\{t:"' + re.escape(name) + r'",c:"[a-z0-9]+"', s)
        if not m:
            missing.append(name)
            continue
        end = find_object_end(s, m.start())
        if end < 0:
            missing.append(name + ' (unbalanced)')
            continue
        if 'viz2:' in s[m.start():end]:
            skipped.append(name)
            continue
        ins = (',v:' + v + ',cap:"' + esc_js(cap) + '"'
               ',viz2:[{v:' + v2 + ',cap:"' + esc_js(cap2) + '"}]')
        s = s[:end] + ins + s[end:]
        added.append(name)

    if added:
        io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added:   %d  %s' % (len(added), ', '.join(added)))
    print('skipped: %d  %s' % (len(skipped), ', '.join(skipped)))
    print('missing: %d  %s' % (len(missing), ', '.join(missing)))
    print('NOTE: each added term contributes one grid figure — update EXPECT_CHARTS.')
    return 1 if missing else 0


sys.exit(main())
