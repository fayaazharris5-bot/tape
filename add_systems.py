# -*- coding: utf-8 -*-
"""Add a 'Named systems & frameworks' section and its terms.

The user asked to "add all the strategies from the internet". They cannot
go in the strategy LIBRARY — rule 3, and test group 18 fails if they do.
A named system belongs in the glossary the same way Wyckoff, Elliott and
the ICT vocabulary already do: named, dated, credited to its documented
originator, with what is and is not established stated plainly.

These entries describe frameworks. They are NOT tradeable rule sets and
must never be phrased as instructions.

Idempotent. Adds one section (EXPECT_SECTIONS moves) and 7 terms
(EXPECT_TERMS moves); no charts, so EXPECT_CHARTS is unchanged.

    py -3 add_systems.py
"""
import io, re, sys

SRC = 'index.html'
SECTION = ('sys', 'Named systems & frameworks',
           'Systems that come with a name attached. Each is listed with its documented '
           'origin and what has actually been established about it — which, for most of '
           'them, is less than the name suggests.')

TERMS = [
 dict(t="Orochi framework", lvl=3, warn=True,
   d="A contemporary paid framework built on auction market theory, TPO and volume profile, Elliott Wave, VWAP and order flow.",
   e="Sold by subscription. Its marketing claims the framework is immune to the alpha decay that affects strategies — a claim with no way to be wrong, which is the problem with it.",
   rel=["Auction market theory","Market profile","Elliott Wave","Falsifiability"]),
 dict(t="Turtle system", lvl=2,
   d="Richard Dennis and William Eckhardt's 1980s trend-following experiment: enter on a 20-day Donchian channel breakout, exit on a 10-day breakout the other way.",
   e="Taught to a recruited group to settle whether trading was teachable. The rules were later published in full, which is unusual and makes it one of the few systems anyone can test exactly as written.",
   rel=["Donchian Channel","Trend following","Breakout","Live decay"]),
 dict(t="Connors RSI-2", lvl=2,
   d="Larry Connors' mean-reversion rule: a 2-period RSI at an extreme while price is above a long moving average, exiting on a move back through a shorter average.",
   e="Published in Street Smarts (1996, with Linda Raschke) and Short Term Trading Strategies That Work (2008). Widely quoted with high win rates attached — the figure people repeat, and the one that matters least.",
   rel=["RSI","Mean reversion","Win rate","Expectancy"]),
 dict(t="Darvas box", lvl=2,
   d="Nicolas Darvas's 1950s method: draw a box around a consolidation, buy a breakout above it, and trail the stop under each new box as the price steps up.",
   e="From How I Made $2,000,000 in the Stock Market — the sum is the book's own claim, not an audited figure. Darvas was a touring ballroom dancer trading by telegram, which is the part of the story that gets retold.",
   rel=["Consolidation","Breakout","Survivor track record","Trailing stop"]),
 dict(t="Dual momentum", lvl=2,
   d="Gary Antonacci's rule combining relative momentum — hold whichever asset has outperformed — with absolute momentum, which moves to cash when the trend itself is negative.",
   e="From Dual Momentum Investing (2014). The absolute-momentum half is the one doing the defensive work; it is what takes the position off during sustained declines.",
   rel=["Momentum factor","Cross-sectional momentum","Trend following","Regime change"]),
 dict(t="Pairs trading", lvl=3,
   d="Trading the spread between two historically related instruments: short the stretched one, long the lagging one, and profit if the relationship reverts.",
   e="Documented academically by Gatev, Goetzmann and Rouwenhorst (Review of Financial Studies, 2006) over 1962-2002 data. Being market-neutral is the appeal — the bet is on the relationship, not direction.",
   rel=["Statistical arbitrage","Mean reversion","Correlation risk","Basis risk"]),
 dict(t="Statistical arbitrage", lvl=3,
   d="Running many small, weakly-predictive positions at once so that the average behaves better than any single one of them.",
   e="Institutional by construction: it needs breadth, cheap execution and infrastructure that retail does not have. The edge per trade is far smaller than the transaction costs a retail account pays.",
   rel=["Pairs trading","Law of large numbers","Colocation","Cost drag"]),
]


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def term_js(x):
    """Key order matters: t, then c, then alt if any — never between."""
    parts = ['{t:"%s",c:"sys"' % esc(x['t'])]
    if x.get('lvl'):
        parts.append(',lvl:%d' % x['lvl'])
    parts.append(',d:"%s"' % esc(x['d']))
    parts.append(',e:"%s"' % esc(x['e']))
    if x.get('rel'):
        parts.append(',rel:[%s]' % ','.join('"%s"' % esc(r) for r in x['rel']))
    if x.get('warn'):
        parts.append(',warn:true')
    parts.append('}')
    return ''.join(parts)


def main():
    s = io.open(SRC, encoding='utf-8').read()
    if '"sys"' in s and 'Named systems & frameworks' in s:
        print('already present — nothing to do')
        return 0

    # 1. the section, appended after the last CAT.push entry
    anchor = '["mgmt","Trade management & exits"'
    i = s.find(anchor)
    if i < 0:
        print('could not find the CAT anchor'); return 1
    end = s.find('\n', i)
    sec = '\n["%s","%s","%s"],' % (SECTION[0], esc(SECTION[1]), esc(SECTION[2]))
    # the mgmt line is last, so it has no trailing comma before ");"
    line = s[i:end]
    newline = line.rstrip()
    if not newline.endswith(','):
        newline += ','
    s = s[:i] + newline + sec.rstrip(',') + s[end:]

    # 2. the terms, as their own D.push at the end of the data block
    push = '\nD.push(\n  ' + ',\n  '.join(term_js(t) for t in TERMS) + '\n);\n'
    marker = '\nvar D = [];\n'
    j = s.find(marker)
    if j < 0:
        print('could not find the D declaration'); return 1
    s = s[:j + len(marker)] + push + s[j + len(marker):]

    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added section %s and %d terms' % (SECTION[0], len(TERMS)))
    print('NOTE: EXPECT_TERMS and EXPECT_SECTIONS both move — comment them.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
