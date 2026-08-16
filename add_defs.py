# -*- coding: utf-8 -*-
"""Fill genuine definition gaps found by probing the corpus.

Candidates were checked against existing entries first, and several were
dropped as already covered: Time in force already documents GTC, IOC and
FOK; Kelly criterion and Kelly fraction in practice cover fractional
Kelly; Funding rate covers the funding interval.

What remains are concepts a retail trader meets constantly and the
glossary had no entry for — several of them load-bearing for this
project's own argument (ergodicity and path dependence are why an
expected value can be positive while the trader still goes broke).

Idempotent. Adds terms, so EXPECT_TERMS moves; existing sections, so
SECTIONS does not.

    py -3 add_defs.py
"""
import io, re, sys

SRC = 'index.html'

TERMS = [
 # --- statistics and risk: the ones this project's argument rests on
 dict(t="Ergodicity", c="stat", lvl=3, warn=True,
   d="Whether the average across many people equals the average for one person over time. In trading it does not.",
   e="Six traders each risking everything once: the group's average return can be positive while every individual eventually hits zero. The ensemble average is not your average."),
 dict(t="Path dependence", c="stat", lvl=2,
   d="When the order of returns changes the outcome, not just their set.",
   e="+50% then -50% leaves you at 75. -50% then +50% also leaves you at 75 — but add a withdrawal, or a margin call at the bottom, and the two orders stop being equivalent."),
 dict(t="Variance drain", c="risk", lvl=2,
   d="The gap between the average return and the compounded return, which widens as volatility rises.",
   e="Alternating +10% and -10% averages zero and compounds to a loss of about 1% per pair. Volatility costs you even when the arithmetic mean says it should not."),
 dict(t="Type I / Type II error", c="stat", lvl=2,
   d="A false positive — concluding an edge exists when it does not — versus a false negative, missing a real one.",
   e="Loosening a test to catch more real edges necessarily admits more false ones. Which error you would rather make is a decision, not a statistic."),
 dict(t="Cointegration", c="stat", lvl=3,
   d="Two series that individually wander but whose spread stays bounded, so the gap between them tends to close.",
   e="The statistical basis pairs trading rests on. Correlation says two things moved together; cointegration says the distance between them is anchored."),
 dict(t="Half-life", c="stat", lvl=3,
   d="How long a deviation from the mean takes to decay by half — a way to put a number on how quickly reversion happens.",
   e="A spread with a five-day half-life and a holding period of one day is being exited before the thing you were betting on has happened."),
 dict(t="Information ratio", c="perf", lvl=3,
   d="Excess return over a benchmark divided by the volatility of that excess — a Sharpe ratio measured against something other than cash.",
   e="Answers whether the active decisions added anything, rather than whether the market went up while you were in it."),
 # --- crypto: the metrics that get quoted at you
 dict(t="Fully diluted valuation", c="cry", lvl=2, warn=True,
   d="Token price multiplied by the TOTAL eventual supply, including everything not yet issued.",
   e="A token can look small by market cap and enormous by FDV. The gap between the two is future selling that has not arrived yet."),
 dict(t="Circulating supply", c="cry", lvl=2,
   d="The tokens actually issued and tradeable now, as against the total that will eventually exist.",
   e="The denominator in market cap, and the number most easily presented favourably. Compare it with the unlock schedule rather than reading it alone."),
 dict(t="Liquidation price", c="cry", lvl=1,
   d="The price at which a leveraged position no longer has enough collateral and gets force-closed.",
   e="Shown by the venue before you open. It moves as you add or remove margin, and it is the single number that decides whether a position survives a wick."),
 dict(t="Sandwich attack", c="cry", lvl=3, warn=True,
   d="A bot placing an order in front of yours and another behind it, profiting from the price move your own trade causes.",
   e="A specific form of MEV that a public transaction queue makes possible. Large orders on thin pools are the usual target."),
 dict(t="Priority fee", c="cry", lvl=2,
   d="An extra payment to have a transaction included sooner when blockspace is contested.",
   e="Rises exactly when everyone wants the same thing at once, which is when getting filled matters most — a cost that peaks with urgency."),
 # --- execution plumbing
 dict(t="Maker / taker", c="exec", lvl=1,
   d="Fee tiers that charge differently depending on whether your order added liquidity or removed it.",
   e="Resting a limit order usually earns the maker rate; crossing the spread pays the taker rate. On a high-turnover strategy the difference dominates."),
 dict(t="Post-only order", c="exec", lvl=2,
   d="An order that cancels rather than execute if it would cross the spread, guaranteeing it adds liquidity.",
   e="Used to stay on the maker fee tier. The trade-off is that it sometimes does not get placed at all."),
 dict(t="NBBO", c="exec", lvl=3,
   d="National Best Bid and Offer — the best prices available across all US venues, which brokers must consider when routing.",
   e="A single displayed quote assembled from many venues. Whether you actually receive it depends on where your order was routed."),
 dict(t="Last look", c="exec", lvl=3, warn=True,
   d="A practice where a liquidity provider may reject a trade after seeing it, within a brief window.",
   e="Common in FX. It means a quoted price is an invitation rather than a commitment, and rejections cluster when the market is moving."),
 dict(t="Hidden order", c="exec", lvl=3,
   d="An order resting at a venue without appearing in the visible book.",
   e="Why displayed depth understates real interest, and why a level can absorb far more than the book suggested."),
 # --- process
 dict(t="Pre-mortem", c="psy", lvl=2,
   d="Imagining the trade or plan has already failed and writing down why, before committing to it.",
   e="Run before entry rather than after the loss, when the reasons are still describable without needing to defend anything."),
 dict(t="Decision journal", c="ops", lvl=2,
   d="A record of what you decided and expected at the time, written before the outcome is known.",
   e="Separates decision quality from result. Memory rewrites the reasoning to fit what happened; a contemporaneous note cannot."),
 dict(t="Outside view", c="psy", lvl=2,
   d="Judging a plan by what happened to everyone else who tried something similar, rather than by the details of your own case.",
   e="The base rate for retail day trading is the outside view. The conviction that your situation is different is the inside view."),
 # --- products
 dict(t="Spread bet", c="deriv", lvl=2,
   d="A leveraged bet on price movement per point, structured as a wager rather than a purchase of the underlying.",
   e="A UK and Ireland product with its own tax treatment. You never own the instrument, and the provider is your counterparty."),
 dict(t="ETN", c="deriv", lvl=3, warn=True,
   d="An exchange-traded NOTE — an unsecured debt obligation of the issuer that tracks an index, rather than a fund holding assets.",
   e="Looks like an ETF on a screen. If the issuer fails, there is no basket of holdings to fall back on, only a claim against them."),
]


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def term_js(x):
    p = ['{t:"%s",c:"%s"' % (esc(x['t']), x['c'])]
    if x.get('lvl'):
        p.append(',lvl:%d' % x['lvl'])
    p.append(',d:"%s"' % esc(x['d']))
    p.append(',e:"%s"' % esc(x['e']))
    if x.get('warn'):
        p.append(',warn:true')
    p.append('}')
    return ''.join(p)


def main():
    s = io.open(SRC, encoding='utf-8').read()
    todo = [t for t in TERMS
            if ('{t:"%s",c:"%s"' % (esc(t['t']), t['c'])) not in s]
    if not todo:
        print('all present'); return 0
    last = s.rfind('\nD.push(')
    end = s.find('\n);\n', last)
    if last < 0 or end < 0:
        print('no D.push block found'); return 1
    at = end + len('\n);\n')
    s = s[:at] + 'D.push(\n  ' + ',\n  '.join(term_js(t) for t in todo) + '\n);\n' + s[at:]
    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d terms:' % len(todo))
    for t in todo:
        print('   %-26s %s' % (t['t'], t['c']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
