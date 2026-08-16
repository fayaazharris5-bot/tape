# -*- coding: utf-8 -*-
"""Surface every checkable factual claim in the corpus for review.

1039 entries cannot be fact-checked by reading them all. What CAN be done
is extract the assertions that are falsifiable — dates, named people,
publications, institutions, hard figures — so the risky ones get verified
instead of trusted. Prose opinion is not extractable; a year attached to a
person is.

Reports rather than fails: it is a review tool, not a gate. Nothing here
can tell whether a claim is TRUE, only that it is the kind of claim that
could be wrong.

    py -3 audit_facts.py              # grouped summary
    py -3 audit_facts.py --list       # every claim with its term
"""
import io, re, sys, collections

SRC = 'index.html'
unesc = lambda t: (t.replace('\\n', ' ').replace('\\"', '"')
                    .replace('\\u2014', '—').replace('\\\\', '\\'))

s = io.open(SRC, encoding='utf-8').read()

# Long-form bodies…
bodies = [(unesc(m.group(1)), unesc(m.group(2)))
          for m in re.finditer(r'"((?:[^"\\]|\\.)*)":\{[\s\n]*long:"((?:[^"\\]|\\.)*)"', s)]

# …and the term objects' own d:, e: and cap: fields. Scanning only the long
# bodies missed half the dated claims — of four "Street Smarts" references,
# two sat in example fields and were invisible to this audit.
_starts = list(re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s))
for _i, _m in enumerate(_starts):
    _end = _starts[_i + 1].start() if _i + 1 < len(_starts) else _m.start() + 3000
    _chunk = s[_m.start():_end]
    _name = unesc(_m.group(1))
    for _f in ('d', 'e', 'cap'):
        _fm = re.search(r',%s:"((?:[^"\\]|\\.)*)"' % _f, _chunk)
        if _fm:
            bodies.append((_name + ' [' + _f + ']', unesc(_fm.group(1))))

PATTERNS = [
    ('year',        r'\b(1[89]\d{2}|20[0-2]\d)\b'),
    ('attribution', r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z'\-]+){0,2})"
                    r"(?:'s)?\s+(?:developed|created|introduced|published|described|"
                    r"documented|showed|named|devised|popularised|formalised)"),
    ('credited-to', r'(?:developed|created|introduced|published|devised|popularised|'
                    r'documented|named|described)\s+by\s+([A-Z][A-Za-z.\-]+'
                    r"(?:\s+[A-Z][A-Za-z.'\-]+){0,3})"),
    ('institution', r'\b(Federal Reserve|NBER|CBOT|CME|NYSE|FINRA|ASIC|SEC|CFTC|RBA|'
                    r'Journal of Finance|Review of Financial Studies|Bank of England)\b'),
    ('hard-figure', r'(\$[\d,]+(?:\.\d+)?(?:\s?(?:million|billion|trillion))?)'),
    ('percentage',  r'(\d+(?:\.\d+)?\s?per cent)'),
]

found = collections.defaultdict(list)
for name, body in bodies:
    for label, rx in PATTERNS:
        for m in re.finditer(rx, body):
            val = m.group(1).strip()
            found[label].append((name, val))

def contradictions():
    """Same named work or person given two different years in two entries.

    This is how the Street Smarts error surfaced: one entry said 1995 and
    another said 1996, so the corpus disagreed with itself. A single wrong
    date is hard to spot; two entries disagreeing is mechanically findable.
    """
    WORKS = [
        'Street Smarts', 'New Concepts in Technical Trading Systems',
        'Profits in the Stock Market', 'Beating the Dow',
        'Inflation-Proofing Your Investments', 'Dual Momentum Investing',
        'The Variation of Certain Speculative Prices', 'The Trading Game',
        'New Key to Stock Market Profits',
    ]
    out = {}
    for work in WORKS:
        years = set()
        where = []
        for name, b in bodies:
            for m in re.finditer(re.escape(work) + r'[^.]{0,60}', b):
                for y in re.findall(r'\b(1[89]\d{2}|20[0-2]\d)\b', m.group(0)):
                    years.add(y)
                    where.append((name, y))
        if len(years) > 1:
            out[work] = where
    return out


show_all = '--list' in sys.argv
print('bodies scanned: %d\n' % len(bodies))

clash = contradictions()
print('works given inconsistent years: %d' % len(clash))
for work, where in clash.items():
    print('  %s' % work)
    for n, y in where:
        print('      %-34s %s' % (n[:34], y))
print()
for label, _rx in PATTERNS:
    items = found[label]
    uniq = collections.Counter(v for _n, v in items)
    print('%-12s %d claims, %d distinct' % (label, len(items), len(uniq)))
    if show_all:
        for n, v in sorted(items):
            print('    %-34s %s' % (n[:34], v))
    else:
        for v, c in uniq.most_common(12):
            who = [n for n, x in items if x == v][:2]
            print('    %-28s x%-3d %s' % (v[:28], c, ', '.join(who)[:52]))
    print()
