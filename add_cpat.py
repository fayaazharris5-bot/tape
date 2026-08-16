# -*- coding: utf-8 -*-
"""Chart the candlestick patterns — 3 of 25 had a picture.

A candlestick pattern is a SHAPE. An entry describing one without showing
it is close to useless as a reference, and this section was the largest
visual gap in the corpus.

Every chart here is checked against the pattern's own defining property
before anything is written — body/wick ratios, containment, engulfment,
run direction. The hanging-man lesson: a caption claiming a shape must be
backed by data that actually has it, so the geometry is asserted rather
than eyeballed. The script refuses to write if any check fails.

Reuses the existing engine. Idempotent. Adds grid figures, so
EXPECT_CHARTS moves.

    py -3 add_cpat.py
"""
import io, re, sys
from add_viz2 import find_object_end, esc_js

SRC = 'index.html'

O, H, L, C = 0, 1, 2, 3


def body(c):  return abs(c[C] - c[O])
def upper(c): return c[H] - max(c[O], c[C])
def lower(c): return min(c[O], c[C]) - c[L]


# name: (candles, index-of-interest, box label+colour, caption, check)
SPECS = {
"Long-legged doji": (
 [[96,99,95,98],[98,101,97,100],[100,106,94,100.2],[100.2,102,98,99],[99,101,97,98]], 2,
 ("long-legged doji","s"),
 "Open and close in nearly the same place, with long wicks both ways. It records a bar "
 "that went a long way in both directions and settled where it started.",
 lambda d: body(d[2]) < 0.5 and upper(d[2]) > 4 and lower(d[2]) > 4),

"Dragonfly doji": (
 [[104,105,101,102],[102,103,99,100],[100,100.3,92,100],[100,103,99,102],[102,105,101,104]], 2,
 ("dragonfly doji","u"),
 "A long lower wick with open and close together at the top, and almost no upper wick.",
 lambda d: body(d[2]) < 0.4 and lower(d[2]) > 6 and upper(d[2]) < 1),

"Gravestone doji": (
 [[96,99,95,98],[98,101,97,100],[100,108,99.8,100],[100,101,97,98],[98,99,95,96]], 2,
 ("gravestone doji","d"),
 "The mirror: a long upper wick with open and close together at the bottom.",
 lambda d: body(d[2]) < 0.4 and upper(d[2]) > 6 and lower(d[2]) < 1),

"Marubozu": (
 [[96,97,95,96.5],[96.5,97,95.5,96],[96,104.2,95.9,104],[104,106,103,105],[105,107,104,106]], 2,
 ("marubozu","u"),
 "A full body with effectively no wicks — the bar opened at one extreme and closed at "
 "the other.",
 lambda d: body(d[2]) > 6 and upper(d[2]) < 0.5 and lower(d[2]) < 0.5),

"Inverted hammer": (
 [[106,107,103,104],[104,105,100,101],[101,102,98,99],[99,106,98.5,100],[100,103,99,102]], 3,
 ("inverted hammer","u"),
 "A long upper wick after a decline, with the close back near the low. Same shape as a "
 "shooting star — that one arrives after an advance instead.",
 lambda d: upper(d[3]) > 4 and body(d[3]) < 2 and d[0][C] > d[2][C]),

"Bullish engulfing": (
 [[104,105,101,102],[102,103,99,100],[99.5,106,99,105.5],[105.5,107,104,106],[106,108,105,107]], 2,
 ("bullish engulfing","u"),
 "An up candle whose body covers the previous down candle's body entirely.",
 lambda d: d[2][C] > d[1][O] and d[2][O] < d[1][C] and d[2][C] > d[2][O]),

"Harami": (
 [[104,105,95,96],[97,99,96.5,98],[98,100,97,99],[99,101,98,100],[100,102,99,101]], 1,
 ("harami","a"),
 "A small body sitting entirely inside the previous, much larger one. The name is the "
 "Japanese word for pregnant.",
 lambda d: max(d[1][O],d[1][C]) < max(d[0][O],d[0][C]) and min(d[1][O],d[1][C]) > min(d[0][O],d[0][C])),

"Inside bar": (
 [[96,106,94,104],[103,105,97,99],[99,101,97,100],[100,103,99,102],[102,104,101,103]], 1,
 ("inside bar","a"),
 "The whole range — not just the body — sits inside the previous bar's high and low.",
 lambda d: d[1][H] < d[0][H] and d[1][L] > d[0][L]),

"Outside bar": (
 [[99,102,98,100],[97,105,95,104],[104,106,103,105],[105,107,104,106],[106,108,105,107]], 1,
 ("outside bar","a"),
 "The reverse: this bar's range covers the previous bar's entirely, taking out both "
 "sides of it.",
 lambda d: d[1][H] > d[0][H] and d[1][L] < d[0][L]),

"Morning star": (
 [[106,107,101,102],[101,102,97,98],[97.5,98.5,96,97.8],[98,104,97.5,103],[103,106,102,105]], 2,
 ("the star","u"),
 "A decline, a small indecisive body beneath it, then a strong close back into the "
 "first candle's range. Three bars, read together.",
 lambda d: body(d[2]) < 2 and d[1][C] < d[1][O] and d[3][C] > d[3][O] and d[3][C] > (d[1][O]+d[1][C])/2),

"Evening star": (
 [[96,101,95,100],[100,104,99,103],[103.5,105,102.5,103.8],[103,98,97,98]][:3] +
 [[103,104,97,98],[98,99,95,96]], 2,
 ("the star","d"),
 "The mirror: an advance, a small body above it, then a strong close back down into the "
 "first candle's range.",
 lambda d: body(d[2]) < 2 and d[1][C] > d[1][O] and d[3][C] < d[3][O] and d[3][C] < (d[1][O]+d[1][C])/2),

"Three white soldiers": (
 [[95,96,94,95.5],[95.5,99,95,98.5],[98.5,102,98,101.5],[101.5,105,101,104.5],[104.5,106,104,105]], 3,
 ("three in a row","u"),
 "Three consecutive up candles, each opening within the last body and closing near its "
 "own high.",
 lambda d: all(d[i][C] > d[i][O] for i in (1,2,3)) and d[1][C] < d[2][C] < d[3][C]),

"Three black crows": (
 [[105,106,104,105.5],[105.5,106,101,101.5],[101.5,102,97.5,98],[98,98.5,94,94.5],[94.5,96,93,95]], 3,
 ("three in a row","d"),
 "Three consecutive down candles, each closing near its own low.",
 lambda d: all(d[i][C] < d[i][O] for i in (1,2,3)) and d[1][C] > d[2][C] > d[3][C]),

"Tweezer top / bottom": (
 [[96,99,95,98],[98,104.9,97,104],[104,104.9,100,101],[101,102,98,99],[99,100,96,97]], 2,
 ("matching highs","d"),
 "Two bars reaching the same extreme. The match is the observation — and how exact it "
 "has to be is a tolerance you have to set.",
 lambda d: abs(d[1][H] - d[2][H]) < 0.05),

"Piercing line": (
 [[106,107,101,102],[101,102,96,97],[95.5,101,95,100.5],[100.5,103,100,102],[102,105,101,104]], 2,
 ("piercing line","u"),
 "A down candle, then an up candle opening below its low and closing back above its "
 "midpoint — more than half the fall retaken.",
 lambda d: d[2][O] < d[1][L] and d[2][C] > (d[1][O]+d[1][C])/2 and d[2][C] < d[1][O]),

"Dark cloud cover": (
 [[96,101,95,100],[100,105,99,104],[105.5,106,99,100.5],[100.5,101,97,98],[98,99,95,96]], 2,
 ("dark cloud cover","d"),
 "The mirror: an up candle, then a down candle opening above its high and closing back "
 "below its midpoint.",
 lambda d: d[2][O] > d[1][H] and d[2][C] < (d[1][O]+d[1][C])/2 and d[2][C] > d[1][O]),

"Spinning top": (
 [[96,99,95,98],[98,101,97,100],[100,103,97,100.4],[100.4,102,98,99],[99,101,97,98]], 2,
 ("spinning top","s"),
 "A small body with wicks on both sides — the bar moved either way and finished near "
 "where it began.",
 lambda d: body(d[2]) < 1 and upper(d[2]) > 1.5 and lower(d[2]) > 1.5),

"Pin bar": (
 [[104,105,101,102],[102,103,99,100],[100,101,93,99.5],[99.5,102,99,101],[101,103,100,102]], 2,
 ("pin bar","u"),
 "One dominant wick with the body pushed to the far end — the bar went somewhere and "
 "was rejected out of it.",
 lambda d: lower(d[2]) > 5 and body(d[2]) < 1.5),
}


def spec_js(candles, idx, box):
    d = ','.join('[%s]' % ','.join(str(v) for v in c) for c in candles)
    label, colour = box
    lo = min(candles[idx][L], candles[idx][H])
    hi = max(candles[idx][L], candles[idx][H])
    return ('{k:"c",d:[%s],bx:[{i0:%d,i1:%d,p0:%s,p1:%s,t:"%s",c:"%s"}]}'
            % (d, idx, idx, lo, hi, label, colour))


def main():
    s = io.open(SRC, encoding='utf-8').read()
    # verify every pattern before touching the file
    bad = [n for n, (d, i, b, cap, chk) in SPECS.items() if not chk(d)]
    if bad:
        print('PATTERN CHECK FAILED — refusing to write:')
        for n in bad:
            print('   ', n)
        return 1
    print('all %d patterns satisfy their defining property' % len(SPECS))

    added, skipped, missing = [], [], []
    for name, (d, idx, box, cap, _chk) in SPECS.items():
        m = re.search(r'\{t:"' + re.escape(name) + r'",c:"[a-z0-9]+"', s)
        if not m:
            missing.append(name); continue
        end = find_object_end(s, m.start())
        if end < 0:
            missing.append(name + ' (unbalanced)'); continue
        if ',v:{' in s[m.start():end]:
            skipped.append(name); continue
        ins = ',v:' + spec_js(d, idx, box) + ',cap:"' + esc_js(cap) + '"'
        s = s[:end] + ins + s[end:]
        added.append(name)

    if added:
        io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added:   %d' % len(added))
    print('skipped: %d  %s' % (len(skipped), ', '.join(skipped)))
    print('missing: %d  %s' % (len(missing), ', '.join(missing)))
    print('NOTE: each adds one grid figure — update EXPECT_CHARTS.')
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
