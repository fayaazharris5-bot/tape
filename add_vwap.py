# -*- coding: utf-8 -*-
"""Terms from the VWAP / value-development material the user supplied.

Source: a slide carousel by emir (@44emirr, the Orochi framework author)
on VWAP and value development, supplied by the user — which makes it a
named file source under rule 3. It is still framework material rather
than a rule set, so it lands in the glossary, not the library.

Fact-checked before writing (see the bodies):
  - VWAP as an institutional execution benchmark from the mid-1980s:
    correct; formalised academically by Berkowitz, Logue & Noser,
    Journal of Finance, 1988.
  - 68.3 / 95.5 / 99.7 for one, two and three standard deviations:
    correct for a normal distribution.
  - Applying those percentages to PRICE: not correct. Returns are not
    normally distributed — Mandelbrot (1963), confirmed Fama (1965) —
    and daily excess kurtosis runs far above the zero a normal implies.
    The slides acknowledge the hand-wave in an aside; the entries say it
    plainly instead.

    py -3 add_vwap.py
"""
import io, re, sys

SRC = 'index.html'

TERMS = [
 dict(t="Value development", c="flow", lvl=2,
   d="How the area price spends most of its time shifts across a session, week or month — the running record of where business is actually being done.",
   e="Tracked with VWAPs or profiles across several timeframes at once, to see whether value is migrating up, down or holding still."),
 dict(t="VWAP standard deviation bands", c="flow", lvl=3, warn=True,
   d="Bands plotted a number of standard deviations either side of a VWAP, used to mark how far price has stretched from the volume-weighted average.",
   e="Widely read as '68% of activity sits inside the first band'. That figure comes from the normal distribution, and returns are not normally distributed."),
 dict(t="Poor high / poor low", c="flow", lvl=3,
   d="An auction extreme left flat — several bars finishing at the same price with no tapering — suggesting the move ran out of time rather than out of buyers.",
   e="Contrasted with an extreme that tapers to a point, which is read as the auction being finished there."),
 dict(t="Single print", c="flow", lvl=3,
   d="A price level touched in only one time period of a profile, marking a stretch that price moved through without two-way trade.",
   e="The profile equivalent of a gap or imbalance — the same feature the fair value gap describes, drawn a different way."),
 dict(t="TPO", c="flow", lvl=2,
   d="Time Price Opportunity — a profile built by marking which prices traded in each time period, so the shape shows where time was spent rather than where volume went.",
   e="From Steidlmayer's market profile work at the CBOT. A volume profile answers a different question: where size traded, not where time accumulated."),
 dict(t="Cumulative volume delta", c="flow", lvl=3,
   d="A running total of aggressive buying minus aggressive selling, tracking which side has been crossing the spread to get filled.",
   e="Read for disagreement: price making a high while the running total does not is the usual setup people point to, and it resolves both ways."),
 dict(t="Normal distribution", c="stat", lvl=2, warn=True,
   d="The bell curve — the distribution where about 68, 95 and 99.7 per cent of observations fall within one, two and three standard deviations of the mean.",
   e="Underpins most standard-deviation tools on a chart. Financial returns do not follow it: the tails are much fatter, so extremes arrive far more often than it implies."),
]


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def term_js(x):
    parts = ['{t:"%s",c:"%s"' % (esc(x['t']), x['c'])]
    if x.get('lvl'):
        parts.append(',lvl:%d' % x['lvl'])
    parts.append(',d:"%s"' % esc(x['d']))
    parts.append(',e:"%s"' % esc(x['e']))
    if x.get('warn'):
        parts.append(',warn:true')
    parts.append('}')
    return ''.join(parts)


def main():
    s = io.open(SRC, encoding='utf-8').read()
    todo = [t for t in TERMS
            if ('{t:"%s",c:"%s"' % (esc(t['t']), t['c'])) not in s]
    if not todo:
        print('all present — nothing to do')
        return 0
    last = s.rfind('\nD.push(')
    end = s.find('\n);\n', last)
    if last < 0 or end < 0:
        print('could not find a D.push block'); return 1
    at = end + len('\n);\n')
    push = 'D.push(\n  ' + ',\n  '.join(term_js(t) for t in todo) + '\n);\n'
    s = s[:at] + push + s[at:]
    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d terms: %s' % (len(todo), ', '.join(t['t'] for t in todo)))
    print('NOTE: EXPECT_TERMS moves; sections are existing, so SECTIONS does not.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
