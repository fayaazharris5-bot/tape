# -*- coding: utf-8 -*-
"""Add a Lucid Trading entry to the prop section.

The user asked for it by name after the prop-firm batch. Naming a specific firm
in a glossary is a precedent worth being deliberate about, so:

- There IS precedent. The sys section names Wyckoff, Connors, Darvas and the
  Orochi framework, each with its documented origin and what is actually
  established about it. The prop entries already name FTMO, Topstep and Apex.
  The house style for a named thing is: dated, sourced, no recommendation.

- Firm terms change fast, so every figure is dated inline and told to be
  re-checked. Apex rewrote its whole rulebook in March 2026; LucidFlex itself
  only launched in late November 2025.

- The entry is NOT a recommendation and is not written in review-site voice.
  Its most useful content is that Lucid is the concrete case of the end-of-day
  drawdown mechanic the glossary already describes abstractly, and that its
  funded accounts are simulated like the rest of the sector.

Researched 2026-08-15. Sourcing caveat recorded in the body itself: effectively
all available material is affiliate review sites paid to refer traders.

Idempotent. Adds 1 term (EXPECT_TERMS moves), no section, no charts.

    py -3 add_lucid.py
"""
import io, json, sys

SRC = 'index.html'

TERMS = [
 dict(t="Lucid Trading", c="prop", lvl=1, warn=True,
   d="A futures funded-account provider whose distinguishing rule is an end-of-day trailing drawdown: the loss floor updates at the close rather than on intraday equity.",
   e="That one mechanic is the substantive difference from most competitors, because an intraday floor can be moved by an unrealised spike the trader never banks. Account paths, fees and splits as advertised in 2026 are in the full entry; treat any figure as perishable and check the firm's own terms."),
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
    if '{t:"Lucid Trading"' in s:
        print('already present - nothing to do')
        return 0

    names = set(json.load(io.open('valid_names.json', encoding='utf-8')))
    names |= set(t['t'] for t in TERMS)
    bad = ['%s -> %s' % (t['t'], r)
           for t in TERMS for r in t.get('rel', []) if r not in names]
    if bad:
        print('REFUSING: dead rel target(s):', bad)
        return 1

    push = '\nD.push(\n  ' + ',\n  '.join(term_js(t) for t in TERMS) + '\n);\n'
    marker = '\nvar D = [];\n'
    j = s.find(marker)
    if j < 0:
        print('could not find the D declaration'); return 1
    s = s[:j + len(marker)] + push + s[j + len(marker):]

    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('added %d term(s)' % len(TERMS))
    return 0


if __name__ == '__main__':
    sys.exit(main())
