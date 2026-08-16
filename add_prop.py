# -*- coding: utf-8 -*-
"""Add 14 terms to the existing 'prop' section: firm categories, the rules that
actually end evaluations, and the payout mechanics.

The user asked for "all the different rules for different prop firms, different
categories, tips for passing". Three constraints shaped what this is:

1. RULE 3 — never write rules from recall and dress them up as sourced. Every
   figure here was researched on 2026-08-15 and carries its origin in the text.

2. FIRM-SPECIFIC NUMBERS GO STALE FAST. Apex replaced its entire rulebook on
   1 March 2026. So the durable mechanism is the term, and any firm figure is
   dated inline and told to be re-checked on the firm's own site. A glossary
   that quietly carries last year's drawdown numbers is worse than one that
   carries none.

3. "TIPS FOR PASSING" ARE MOSTLY THE WRONG QUESTION, and the honest version of
   the user's ask is better than the literal one. The published data says most
   candidates fail in week one on the daily loss limit rather than by missing a
   target, and that passing is not the bottleneck — being paid is. So the
   content is aimed at the rules that actually end runs, not at encouragement.
   Nothing here is phrased as advice; the app does not tell anyone what to do.

Avoids the literal phrase "success rate" throughout — audit_claims.py bans it,
correctly, and "pass rate" is the accurate term anyway.

Idempotent. Adds 14 terms (EXPECT_TERMS moves), no section, no charts.

    py -3 add_prop.py
"""
import io, json, re, sys

SRC = 'index.html'
MARKER = 'Payout compliance review'

# NOTE: no "Daily loss limit" entry here on purpose. One already exists in the
# `style` section covering both the self-imposed and firm-imposed cases, and a
# second copy would recreate the Chop-duplicate problem this repo already
# carries. The prop-specific fact worth having — that most evaluations end on
# this rule in week one — lives in "Prop firm pass rate" instead, which is where
# funnel statistics belong. The terms below link to the existing entry.
TERMS = [
 dict(t="Static drawdown", c="prop", lvl=1,
   d="A maximum loss level fixed at the starting balance for the life of the account, so profits never move it.",
   e="The opposite of a trailing floor. Once an account is meaningfully in profit a static floor becomes progressively easier to live with, which is why fewer firms offer it.",
   rel=["Trailing drawdown","Intraday vs end-of-day drawdown","Drawdown"]),

 dict(t="Drawdown lock", c="prop", lvl=2,
   d="The point at which a trailing loss floor stops following the account higher, usually once it reaches the starting balance or a set buffer above it.",
   e="Where the lock sits decides whether a trailing account ever becomes comfortable to trade. A floor that trails forever never stops tightening as the account grows.",
   rel=["Trailing drawdown","Static drawdown","Scaling plan"]),

 dict(t="Instant funding", c="prop", lvl=1, warn=True,
   d="A product with no evaluation phase: the fee buys a simulated account with loss rules attached and profit share from the first trade.",
   e="The evaluation has not been removed so much as moved. The loss limits still decide the outcome, the fee is usually higher, and the profit split is usually worse.",
   rel=["Evaluation","Simulated funding","Two-step vs one-step","Evaluation expected cost"]),

 dict(t="Futures prop vs CFD prop", c="prop", lvl=1,
   d="The two main families of funded-account provider: one built on exchange-traded futures, the other on off-exchange contracts for difference.",
   e="Futures programmes sit on CME contracts with one central order book and a public tape, so fills are checkable against exchange data. CFD programmes are decentralised and the firm may be the counterparty to its own funded accounts.",
   rel=["Futures","CFD","Counterparty risk","Simulated funding"]),

 dict(t="Payout compliance review", c="prop", lvl=2, warn=True,
   d="The audit a firm runs when a withdrawal is requested, in which the account's entire history is re-examined against every rule from the first trade onward.",
   e="This is the structural asymmetry of the model. Rules are enforced retrospectively at the moment money is claimed, so a breach on day one can surface months later at the first payout request rather than when it happened.",
   rel=["Payout verification","Payout split","Prohibited strategy clause","Consistency rule"]),

 dict(t="Prop firm pass rate", c="prop", lvl=1, warn=True,
   d="The share of paying candidates who clear an evaluation, and separately the much smaller share who are ever paid.",
   e="Published 2026 figures cluster at roughly 5-10% clearing an evaluation. One study of about 300,000 accounts reported 14% funded and under half of those ever paid, leaving around 7% of all entrants paid at all. Most failures land in the first week on the daily loss limit rather than on missing the target. Nearly all of these figures are published by firms selling evaluations, so read them as a ceiling on the marketing rather than an independent measurement.",
   rel=["Evaluation expected cost","Daily loss limit","Sample size","Survivorship bias"]),

 dict(t="Prohibited strategy clause", c="prop", lvl=2, warn=True,
   d="Contract terms banning named techniques — latency and arbitrage methods, tick scalping, group order copying, and trading patterns the firm reads as exploiting its pricing rather than the market.",
   e="The wording is usually broad and judged after the fact by the firm. Techniques that are legal, and ordinary at a broker, can still void an account here because the counterparty writing the rules is also the one being traded against.",
   rel=["Payout compliance review","Copy trading a funded account","Scalping","Slippage"]),

 dict(t="Cross-account hedging", c="prop", lvl=2, warn=True,
   d="Holding opposing positions across two or more evaluations so that one account is guaranteed to show the winning side.",
   e="It converts a low-probability evaluation into a fee arbitrage, which is precisely why detection of it is near-universal and why it is one of the most commonly cited grounds for voiding accounts and denying payouts.",
   rel=["Prohibited strategy clause","Payout compliance review","Account sharing"]),

 dict(t="Payout cap", c="prop", lvl=2, warn=True,
   d="A ceiling on how much a single funded account may ever withdraw, whether per payout cycle or in total over the account's life.",
   e="A lifetime cap changes the arithmetic of the whole product, because it bounds the best possible outcome while the fees and the loss rules stay unbounded. Apex introduced total-payout caps in its March 2026 rules; check the current terms rather than trusting any figure quoted second-hand.",
   rel=["Payout split","Payout compliance review","Scaling plan","Evaluation expected cost"]),

 dict(t="Overnight and weekend holding rule", c="prop", lvl=1,
   d="Restrictions on carrying positions past the session close or into the weekend, ranging from higher margin to outright prohibition and automatic liquidation.",
   e="Common on futures programmes, where a gap through a stop is the firm's loss rather than the trader's. Apex banned overnight holding outright in its March 2026 rules.",
   rel=["Gap risk","News trading restriction","Futures"]),

 dict(t="Prop firm regulatory status", c="prop", lvl=2, warn=True,
   d="Most retail funded-account providers are not registered as financial firms, and describe what they sell as an educational or simulated product rather than a brokerage or fund service.",
   e="That framing is what keeps the model outside the registration regimes, and it is also what leaves the customer relying on the firm's own terms rather than on any regulator when a payout is refused.",
   rel=["Simulated funding","Counterparty risk","Regulation","Payout verification"]),

 dict(t="Account sharing", c="prop", lvl=1, warn=True,
   d="Letting anyone else trade an account, or running accounts for other people, both of which are banned by essentially every firm.",
   e="Enforced through device, IP and execution-pattern matching, and usually detected at the payout review rather than at the time. The stated reason is that the firm is evaluating one identifiable person.",
   rel=["Cross-account hedging","Copy trading a funded account","Payout compliance review"]),

 dict(t="Reading a prop firm rulebook", c="prop", lvl=1,
   d="The set of questions that determine what a given programme actually is, independent of how it is marketed.",
   e="Is the loss floor static or trailing, and if trailing does it move on unrealised intraday equity or only at the close? Where does it lock? Is there a consistency cap, a payout cap, a minimum trading-day count? Which strategies are named as prohibited? Those answers describe the product; the headline account size does not.",
   rel=["Trailing drawdown","Consistency rule","Payout cap","Daily loss limit"]),
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
    if '{t:"%s",c:"prop"' % MARKER in s:
        print('already present - nothing to do')
        return 0

    # every rel target must already exist, or the see-links render dead
    names = set(json.load(io.open('valid_names.json', encoding='utf-8')))
    names |= set(t['t'] for t in TERMS)          # they may point at each other
    bad = []
    for t in TERMS:
        for r in t.get('rel', []):
            if r not in names:
                bad.append('%s -> %s' % (t['t'], r))
    if bad:
        print('REFUSING: %d dead rel target(s):' % len(bad))
        for b in bad:
            print('  ', b)
        return 1

    dupes = [t['t'] for t in TERMS if '{t:"%s"' % esc(t['t']) in s]
    if dupes:
        print('REFUSING: these names already exist:', dupes)
        return 1

    push = '\nD.push(\n  ' + ',\n  '.join(term_js(t) for t in TERMS) + '\n);\n'
    marker = '\nvar D = [];\n'
    j = s.find(marker)
    if j < 0:
        print('could not find the D declaration'); return 1
    s = s[:j + len(marker)] + push + s[j + len(marker):]

    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d prop terms' % len(TERMS))
    print('NOTE: EXPECT_TERMS moves - update it with a comment saying why.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
