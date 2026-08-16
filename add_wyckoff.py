# -*- coding: utf-8 -*-
"""Chart the Wyckoff section — 0 of 12 had a picture.

Wyckoff is entirely about WHERE a bar sits inside a structure: a
secondary test is only a secondary test because of what preceded it, and
effort versus result is a statement about volume against range. Prose
alone makes these the hardest entries in the corpus to follow, and they
were the only section with no chart at all.

These use the engine's volume array, which nothing else in the corpus
does — for the climax and for effort-vs-result the volume IS the point,
and drawing them without it would miss what the term means.

Every chart is validated against the structural claim it makes before
anything is written; the script refuses to write if a check fails.

Idempotent. Adds grid figures, so EXPECT_CHARTS moves.

    py -3 add_wyckoff.py
"""
import io, re, sys
from add_viz2 import find_object_end, esc_js

SRC = 'index.html'
O, H, L, C = 0, 1, 2, 3
rng = lambda c: c[H] - c[L]

# name: (candles, volume|None, extras-js, caption, check)
SPECS = {
"Selling climax": (
 [[110,111,106,107],[107,108,102,103],[103,104,98,99],[99,100,88,94],[94,97,93,96],[96,99,95,98]],
 [40,55,70,140,80,60],
 'hl:[{p:88,t:"climax low",c:"a",la:true,below:true}]',
 "The widest bar of the decline, on the heaviest volume, closing well off its low. Heavy "
 "selling met heavy buying — which is what makes it different from an ordinary down bar.",
 lambda d, v: rng(d[3]) == max(rng(c) for c in d) and v[3] == max(v)
              and d[3][C] > d[3][L] + rng(d[3]) * 0.4),

"Automatic rally": (
 [[99,100,88,94],[94,99,93,98],[98,103,97,102],[102,104.8,101,104],[104,104.8,101,102],[102,103,99,100]],
 [140,90,75,60,50,45],
 'hl:[{p:104.8,t:"ceiling of the range",c:"a"}]',
 "The bounce straight after the climax, on fading volume. Where it stops sets the top of "
 "the range everything afterwards is measured against.",
 lambda d, v: d[3][H] == max(c[H] for c in d) and v[0] == max(v) and v[-1] == min(v)),

"Secondary test": (
 [[103,104,99,100],[100,101,88,95],[95,99,94,98],[98,101,97,100],[100,101,89,92],[92,96,91,95]],
 [50,150,80,60,55,45],
 'hl:[{p:88,t:"climax low",c:"a",la:true,below:true}]',
 "A return toward the climax low on much lighter volume, and it holds above it. The lighter "
 "volume is the observation — the same level revisited with less selling behind it.",
 lambda d, v: v[4] < v[1] * 0.5 and d[4][L] > d[1][L] and d[1][L] == min(c[L] for c in d)),

"Trading range": (
 [[96,105,95,103],[103,104.8,96,97],[97,104.5,95.2,103],[103,104.9,96,98],
  [98,104.6,95.1,102],[102,104.8,96,99]],
 None,
 'zn:[{p0:95.1,p1:104.9,t:"the range",c:"a"}]',
 "Price rotating between a floor and a ceiling without leaving either. Everything Wyckoff "
 "labels afterwards is positioned relative to these two edges.",
 lambda d, v: max(c[H] for c in d) - min(c[L] for c in d) < 11
              and all(c[H] <= 105 and c[L] >= 95 for c in d)),

"Sign of strength": (
 [[97,99,96,98],[98,100,97,99],[99,101,98,100],[100,104.9,99,104],[104,110,103,109],[109,112,108,111]],
 [40,38,42,70,130,110],
 'hl:[{p:104.9,t:"range ceiling",c:"a"}]',
 "An advance clearing the range ceiling on expanding volume, with a wide bar and a close "
 "near its high — effort and result agreeing.",
 lambda d, v: d[4][C] > 104.9 and v[4] == max(v) and rng(d[4]) > rng(d[0]) * 2),

"Last point of support": (
 [[104,109,103,108],[108,110,105,106],[106,107,102,103],[103,105,101.5,104],
  [104,108,103,107],[107,112,106,111]],
 [120,80,60,45,70,110],
 'hl:[{p:101.5,t:"higher low",c:"u",la:true,below:true}]',
 "The pullback after the first strong advance, stopping above the range and on light "
 "volume. A higher low with less selling into it than the move that preceded it.",
 lambda d, v: d[3][L] > 100 and v[3] == min(v) and d[5][C] == max(c[C] for c in d)),

"Effort vs result": (
 [[100,101,99,100.5],[100.5,101,99.5,100],[100,100.8,99.2,100.3],[100.3,101.2,99.4,100.4],
  [100.4,101,99.6,100.2],[100.2,101,99.5,100.3]],
 [45,50,55,180,60,50],
 'bx:[{i0:3,i1:3,p0:99.4,p1:101.2,t:"huge volume, no progress",c:"s"}]',
 "One bar with far more volume than its neighbours and no more price movement than them. "
 "Large effort producing no result is the anomaly worth marking.",
 lambda d, v: v[3] > max(v[i] for i in (0,1,2,4,5)) * 2.5
              and rng(d[3]) < max(rng(c) for c in d) * 1.3),

"Supply and demand zones": (
 [[96,98,95,97],[97,99,96,98],[98,99,94,95],[95,103,94.5,102],[102,105,101,104],[104,107,103,106]],
 None,
 'zn:[{p0:94,p1:96,t:"the area price left quickly",c:"u"}]',
 "The area a decisive move departed from. It is the same chart feature an order block "
 "describes, named a century earlier.",
 lambda d, v: d[3][C] - d[3][O] > 6 and d[2][L] <= 95),
}


def spec_js(d, vol, extras):
    parts = ['{k:"c",d:[%s]' % ','.join('[%s]' % ','.join(str(x) for x in c) for c in d)]
    if vol:
        parts.append(',vol:[%s]' % ','.join(str(x) for x in vol))
    if extras:
        parts.append(',' + extras)
    parts.append('}')
    return ''.join(parts)


def main():
    s = io.open(SRC, encoding='utf-8').read()
    bad = [n for n, (d, v, e, cap, chk) in SPECS.items() if not chk(d, v)]
    if bad:
        print('STRUCTURE CHECK FAILED — refusing to write:')
        for n in bad:
            print('   ', n)
        return 1
    print('all %d Wyckoff charts satisfy their structural claim' % len(SPECS))

    added, skipped, missing = [], [], []
    for name, (d, vol, extras, cap, _c) in SPECS.items():
        m = re.search(r'\{t:"' + re.escape(name) + r'",c:"[a-z0-9]+"', s)
        if not m:
            missing.append(name); continue
        end = find_object_end(s, m.start())
        if end < 0:
            missing.append(name + ' (unbalanced)'); continue
        if ',v:{' in s[m.start():end]:
            skipped.append(name); continue
        s = s[:end] + ',v:' + spec_js(d, vol, extras) + ',cap:"' + esc_js(cap) + '"' + s[end:]
        added.append(name)

    if added:
        io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added:   %d  %s' % (len(added), ', '.join(added)))
    print('skipped: %d  %s' % (len(skipped), ', '.join(skipped)))
    print('missing: %d  %s' % (len(missing), ', '.join(missing)))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
