"""List terms with no long-form body, grouped by section code.
Terms live in the t:/c: array; bodies live in separate L-blocks keyed by
term name ("Term":{long:...}), so unwritten = term names minus L keys."""
import io, re, json, collections
s = io.open('index.html', encoding='utf-8').read()
unesc = lambda n: n.replace('\\"', '"').replace('\\\\', '\\')
terms = [(unesc(m.group(1)), m.group(2))
         for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"([a-z0-9]+)"', s)]
written = set(unesc(m.group(1)) for m in
              re.finditer(r'"((?:[^"\\]|\\.)*)":\{[\s\n]*long:', s))
out = collections.OrderedDict()
for name, sec in terms:
    if name not in written:
        out.setdefault(sec, []).append(name)
io.open('unwritten.json', 'w', encoding='utf-8').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('terms', len(terms), '| written', len(written),
      '| unwritten', sum(len(v) for v in out.values()))
for sec in out:
    print(sec, len(out[sec]))
