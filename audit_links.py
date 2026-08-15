# -*- coding: utf-8 -*-
"""Cross-reference integrity across the whole corpus.

merge_agent.py validates `see` links at MERGE time, so agent-written
bodies are covered. Nothing has ever checked:
  - `rel` on the term objects (hand-written, predates that pipeline)
  - `see` on bodies that were hand-written rather than merged
  - links pointing at a name retired by a dedupe pass

A link to a name that no longer exists renders a chip that goes nowhere.
Also reports orphans — terms nothing links to — which are findable only
by search or by scrolling their section.

Exits non-zero on a dead link. Orphans are reported, not failed: some
terms legitimately have no inbound reference.

    py -3 audit_links.py
"""
import io, re, sys, collections

SRC = 'index.html'

s = io.open(SRC, encoding='utf-8').read()
unesc = lambda n: n.replace('\\"', '"').replace('\\\\', '\\')

terms = [unesc(m.group(1)) for m in
         re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)]
known = set(terms)

# alt names are legitimate link targets too — they resolve in search
alts = set()
for m in re.finditer(r'alt:"([^"]*)"', s):
    for w in m.group(1).split():
        alts.add(w.lower())

dead = []
inbound = collections.Counter()

# rel: on term objects
for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"[^}]*?rel:\[([^\]]*)\]', s):
    owner = unesc(m.group(1))
    for r in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2)):
        r = unesc(r)
        inbound[r] += 1
        if r not in known:
            dead.append(('rel', owner, r))

# see: on long-form bodies
for m in re.finditer(r'"((?:[^"\\]|\\.)*)":\{[\s\n]*long:.*?see:\[([^\]]*)\]', s, re.S):
    owner = unesc(m.group(1))
    for r in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2)):
        r = unesc(r)
        inbound[r] += 1
        if r not in known:
            dead.append(('see', owner, r))

print('terms: %d | link targets checked: %d' % (len(terms), sum(inbound.values())))
print('dead links: %d' % len(dead))
for kind, owner, target in dead[:25]:
    print('  %-4s %s -> %r' % (kind, owner, target))
if len(dead) > 25:
    print('  ... and %d more' % (len(dead) - 25))

orphans = [t for t in terms if inbound[t] == 0]
print('orphans (nothing links to them): %d' % len(orphans))
for t in orphans[:15]:
    print('   ', t)
if len(orphans) > 15:
    print('    ... and %d more' % (len(orphans) - 15))

sys.exit(1 if dead else 0)
