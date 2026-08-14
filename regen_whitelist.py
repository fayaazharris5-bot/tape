# -*- coding: utf-8 -*-
"""Regenerate valid_names.json from the terms actually in index.html.

Was a copy-paste snippet in HANDOFF.md, which is a bad home for it: the
pattern is full of backslashes and gets mangled the moment anyone runs it
through a shell one-liner. It is a file now.

Run after ANY content or dedupe change — writer briefs validate their
see-links against this file, so a stale whitelist rejects good entries and
accepts dead links.

    py -3 regen_whitelist.py
"""
import io, re, json, sys

SRC, OUT = 'index.html', 'valid_names.json'

s = io.open(SRC, encoding='utf-8').read()
names = sorted(set(
    m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)
))
if not names:
    print('no terms matched — has the term-object shape changed?')
    sys.exit(1)

unesc = lambda n: n.replace('\\"', '"').replace('\\\\', '\\')
names = sorted(set(unesc(n) for n in names))

before = []
try:
    before = json.load(io.open(OUT, encoding='utf-8'))
except Exception:
    pass

io.open(OUT, 'w', encoding='utf-8').write(json.dumps(names))

added = sorted(set(names) - set(before))
removed = sorted(set(before) - set(names))
print('%s: %d names (was %d)' % (OUT, len(names), len(before)))
if added:
    print('  added:   ' + ', '.join(added[:12]) + (' …' if len(added) > 12 else ''))
if removed:
    print('  REMOVED: ' + ', '.join(removed[:12]) + (' …' if len(removed) > 12 else ''))
    print('  (removed names break any see-link pointing at them — extend'
          ' merge_agent.py ALIAS if these were renamed rather than deleted)')
