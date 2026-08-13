"""Field-coverage audit across the whole corpus.
Bodies live in L-blocks keyed by term name; term objects hold t/c/d/e.
Reports which terms are missing each field so gaps are visible rather
than assumed."""
import io, re, collections

s = io.open('index.html', encoding='utf-8').read()
unesc = lambda n: n.replace('\\"', '"').replace('\\\\', '\\')

terms = [(unesc(m.group(1)), m.group(2), m.group(0))
         for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"([a-z0-9]+)"[^}]*', s)]

# L-block entries: name -> which of long/usage/see it carries
blocks = {}
for m in re.finditer(r'"((?:[^"\\]|\\.)*)":\{((?:[^{}]|\{[^{}]*\})*)\}', s):
    name, body = unesc(m.group(1)), m.group(2)
    if 'long:' not in body:
        continue
    blocks[name] = {
        'long': 'long:' in body,
        'usage': 'usage:' in body,
        'see': 'see:' in body,
    }

no_usage = sorted(n for n, f in blocks.items() if not f['usage'])
no_see = sorted(n for n, f in blocks.items() if not f['see'])
no_example = sorted(n for n, c, raw in terms if ',e:"' not in raw)

print('terms: %d | bodies: %d' % (len(terms), len(blocks)))
print('bodies missing usage: %d' % len(no_usage))
for n in no_usage[:15]:
    print('   ', n)
if len(no_usage) > 15:
    print('    ... and %d more' % (len(no_usage) - 15))
print('bodies missing see:   %d' % len(no_see))
for n in no_see[:15]:
    print('   ', n)
if len(no_see) > 15:
    print('    ... and %d more' % (len(no_see) - 15))
print('terms missing an example: %d' % len(no_example))
for n in no_example[:10]:
    print('   ', n)

bysec = collections.Counter(c for _, c, _ in terms)
print('sections: %d' % len(bysec))
