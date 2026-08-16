# -*- coding: utf-8 -*-
"""Add the well-known prop firms by name, plus a landscape entry for the rest.

Researched 2026-08-15. Not written from recall — rule 3.

STRUCTURE DECISION: five named entries, not fifteen. The named ones are the
reference points people actually meet and search for, and each carries a
genuine structural difference worth a term. Everything else goes in one
landscape entry, because a glossary carrying fifteen firm profiles becomes
fifteen things to re-verify every time the sector rewrites its terms — which
it does constantly. Apex replaced its whole rulebook in March 2026 and FTMO
bought a broker in the same window.

Every figure is dated inline and told to be re-checked against the firm's own
site. None of these entries recommend anything, and none is written in
review-site voice; each states what the firm is, what is structurally
distinctive about it, and what the caveat is.

SOURCING CAVEAT, recorded in the bodies: nearly all published prop-firm data
comes from the firms themselves or from affiliate sites paid per referral.
Payout totals in particular are self-reported and not independently audited.

Idempotent. Adds 6 terms (EXPECT_TERMS moves), no section, no charts.

    py -3 add_firms.py
"""
import io, json, sys

SRC = 'index.html'

TERMS = [
 dict(t="FTMO", c="prop", lvl=1, warn=True,
   d="The largest forex and CFD funded-account provider, operating since 2015 on a two-phase evaluation.",
   e="The sector's reference point, and the firm with the longest self-reported payout record. It acquired the broker OANDA and re-entered the US market over 2025-26, which makes it unusual here: most competitors are not attached to a regulated brokerage at all.",
   rel=["Two-step vs one-step","Payout split","Scaling plan","Prop firm regulatory status"]),

 dict(t="Topstep", c="prop", lvl=1, warn=True,
   d="The longest-running futures funded-account provider, built on a monthly subscription rather than a one-off evaluation fee.",
   e="The subscription model changes the arithmetic: the cost accrues monthly for as long as an evaluation takes, so a slow pass can cost more than a fast failure. It uses an end-of-day trailing drawdown and moved onto its own mandatory platform over 2025-26.",
   rel=["Evaluation expected cost","Intraday vs end-of-day drawdown","Reset fee","Futures"]),

 dict(t="Apex Trader Funding", c="prop", lvl=1, warn=True,
   d="The highest-volume futures funded-account provider by self-reported payouts, known for frequent and substantial rule changes.",
   e="It advertises a first-attempt pass rate well above the sector's usual figures, which is worth reading alongside the fact that it also replaced its entire rulebook on 1 March 2026 — adding an overnight holding ban and total payout caps. Anything quoted about this firm ages unusually fast.",
   rel=["Payout cap","Overnight and weekend holding rule","Consistency rule","Prop firm pass rate"]),

 dict(t="FundedNext", c="prop", lvl=2,
   d="A large forex and CFD provider that grew rapidly after 2022, offering several evaluation models side by side.",
   e="Notable mainly for scale and for the number of parallel account types it runs. Where a firm offers many models at once, the differences between them are where the actual terms live rather than in the shared marketing.",
   rel=["Two-step vs one-step","Instant funding","Reading a prop firm rulebook"]),

 dict(t="The5ers", c="prop", lvl=2,
   d="One of the longer-running forex funded-account providers, using multi-tier scaling programmes.",
   e="Its length of operation is the relevant fact. In a sector where most firms are only a few years old and several have closed abruptly, having traded through more than one cycle is one of the few observable signals available.",
   rel=["Scaling plan","Payout verification","Prop firm regulatory status"]),

 dict(t="Prop firm landscape", c="prop", lvl=1, warn=True,
   d="The wider field of funded-account providers beyond the handful of well-known names, and how to place an unfamiliar one.",
   e="Futures names include Take Profit Trader, MyFundedFutures, Tradeify, Bulenox, TickTickTrader and Earn2Trade; forex and CFD names include Funding Pips, FXIFY, The Funded Trader and Alpha Capital Group. New firms appear constantly and some disappear just as fast.",
   rel=["Prop firm regulatory status","Payout verification","Reading a prop firm rulebook","Prop firm pass rate"]),
]


def esc(x):
    return x.replace('\\', '\\\\').replace('"', '\\"')


def term_js(x):
    p = ['{t:"%s"' % esc(x['t']), ',c:"%s"' % esc(x['c'])]
    if x.get('lvl'):
        p.append(',lvl:%d' % x['lvl'])
    p.append(',d:"%s"' % esc(x['d']))
    p.append(',e:"%s"' % esc(x['e']))
    if x.get('rel'):
        p.append(',rel:[%s]' % ','.join('"%s"' % esc(r) for r in x['rel']))
    if x.get('warn'):
        p.append(',warn:true')
    p.append('}')
    return ''.join(p)


def main():
    s = io.open(SRC, encoding='utf-8').read()
    dupes = [t['t'] for t in TERMS if '{t:"%s"' % esc(t['t']) in s]
    if dupes:
        print('already present:', dupes)
        return 0

    names = set(json.load(io.open('valid_names.json', encoding='utf-8')))
    names |= set(t['t'] for t in TERMS)
    bad = ['%s -> %s' % (t['t'], r)
           for t in TERMS for r in t.get('rel', []) if r not in names]
    if bad:
        print('REFUSING: dead rel target(s):')
        for b in bad:
            print('  ', b)
        return 1

    push = '\nD.push(\n  ' + ',\n  '.join(term_js(t) for t in TERMS) + '\n);\n'
    marker = '\nvar D = [];\n'
    j = s.find(marker)
    if j < 0:
        print('could not find the D declaration'); return 1
    s = s[:j + len(marker)] + push + s[j + len(marker):]

    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d terms' % len(TERMS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
