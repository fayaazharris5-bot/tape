# -*- coding: utf-8 -*-
"""Second batch for the 'Named systems & frameworks' section.

Allocation systems, two contested pattern frameworks and one session
play. Same rule as batch one: these are glossary ENTRIES describing named
systems, never rule sets for the library.

Reuses add_systems.py's term serialiser rather than duplicating it.
Idempotent — skips any term already present.

    py -3 add_systems2.py
"""
import io, re, sys
from add_systems import term_js

SRC = 'index.html'

TERMS = [
 dict(t="60/40 portfolio", lvl=1,
   d="The conventional balanced allocation: sixty per cent equities for growth, forty per cent bonds to cushion the falls.",
   e="Less a strategy than the default benchmark everything else gets measured against. Its weak point is the assumption that the two legs fall at different times — 2022 was the reminder that they can drop together.",
   rel=["Diversification","Rebalancing","Correlation risk","Buy and hold"]),
 dict(t="Permanent portfolio", lvl=2,
   d="Harry Browne and Terry Coxon's equal split across stocks, bonds, gold and cash — one quarter each, rebalanced when the weights drift far enough.",
   e="First set out in Inflation-Proofing Your Investments (1981). The design assigns one asset to each economic condition: growth, deflation, inflation and recession, so something should be working whatever arrives.",
   rel=["Diversification","Rebalancing","Regime change","Risk parity"]),
 dict(t="All Weather portfolio", lvl=3,
   d="Ray Dalio's risk-balanced allocation: weight assets so each contributes a similar share of portfolio risk rather than a similar share of capital.",
   e="Because bonds are less volatile than equities, equalising risk means holding far more of them by value — which is why the institutional versions use leverage to lift the bond leg's contribution.",
   rel=["Risk parity","Volatility","Diversification","Leverage"]),
 dict(t="Value averaging", lvl=2,
   d="Michael Edleson's contribution rule: set a target path for the portfolio's value and invest whatever is needed each period to land on it, buying more after falls and less after rises.",
   e="From a 1988 article and the book that followed. It is the disciplined cousin of dollar cost averaging — and it can demand contributions far larger than planned in a sustained decline, which is when cash is scarcest.",
   rel=["Dollar cost averaging","Rebalancing","Sequence risk","Capital allocation"]),
 dict(t="Dogs of the Dow", lvl=2,
   d="Buy the ten highest dividend-yielding Dow components at the start of each year, hold, and repeat annually.",
   e="Popularised by Michael O'Higgins' Beating the Dow (1991), which claimed a large margin over the index across the preceding two decades — his own backtest, over a period he chose, published after the fact.",
   rel=["Dividend yield","Value factor","Data snooping","Rebalancing"]),
 dict(t="London breakout", lvl=2,
   d="An FX session play: mark the range of the quiet Asian hours, then trade the break of it as London opens and volume arrives.",
   e="The mechanism is real — liquidity genuinely steps up at the London open, and a range built in thin hours is easy to leave. Whether the break holds is the part the setup does not tell you.",
   rel=["Asian range","FX session overlap","Breakout","False breakout"]),
 dict(t="Wolfe wave", lvl=3, warn=True,
   d="Bill Wolfe's five-point formation, where a line drawn through two of the points projects a target the fifth point is expected to run to.",
   e="The pattern is identified by eye and its points can be relabelled as price develops, so the projection line moves with them.",
   rel=["Elliott Wave","Harmonic patterns","Pattern subjectivity","Falsifiability"]),
 dict(t="Three-drive pattern", lvl=3, warn=True,
   d="Three symmetrical pushes in the same direction, each with a specified retracement between them, treated as exhaustion at the third.",
   e="From the harmonic family, and it inherits the family's problem: the required symmetry is enforced with a tolerance, and a wide enough tolerance will find the shape almost anywhere.",
   rel=["Harmonic patterns","ABCD pattern","Pattern subjectivity","Overfitting"]),
]


def find_last_push_end(s):
    """Insert after the final D.push( ... ); in the data block."""
    last = s.rfind('\nD.push(')
    if last < 0:
        return -1
    end = s.find('\n);\n', last)
    return end + len('\n);\n') if end > 0 else -1


def main():
    s = io.open(SRC, encoding='utf-8').read()
    todo = [t for t in TERMS if ('{t:"%s",c:"sys"' % t['t'].replace('"', '\\"')) not in s]
    if not todo:
        print('all present — nothing to do')
        return 0
    at = find_last_push_end(s)
    if at < 0:
        print('could not find a D.push block to append after')
        return 1
    push = 'D.push(\n  ' + ',\n  '.join(term_js(t) for t in todo) + '\n);\n'
    s = s[:at] + push + s[at:]
    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d terms: %s' % (len(todo), ', '.join(t['t'] for t in todo)))
    print('NOTE: EXPECT_TERMS moves — comment it, then run regen_whitelist.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
