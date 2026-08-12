# -*- coding: utf-8 -*-
# Merge one agent-written JSON fragment into index.html, through the same
# validation the hand-written batches go through. Usage: merge_agent.py <file.json>
import io, json, re, sys

if len(sys.argv) != 2:
    print('usage: merge_agent.py <agent_file.json>'); sys.exit(1)

FRAG = sys.argv[1]
P = 'index.html'

entries = json.loads(io.open(FRAG, encoding='utf-8-sig').read())
# names deleted in dedupe passes -> their keepers, so agent fragments
# written against the older whitelist still merge cleanly
ALIAS = {'Support': 'Support / resistance', 'Resistance': 'Support / resistance',
         'Trendline / channel': 'Trendline', 'Swing high / low': 'Swing high / swing low',
         'In-sample / out-of-sample': 'In-sample / out-of-sample split',
         'Multiple comparisons': 'Multiple testing', 'Killzone': 'Kill zone',
         'Power of three': 'Power of 3', 'OTE': 'Optimal trade entry',
         'Order book / depth': 'Order book / DOM'}
for _k, _v in entries.items():
    if isinstance(_v, dict) and isinstance(_v.get('see'), list):
        _v['see'] = list(dict.fromkeys(ALIAS.get(t, t) for t in _v['see']))
s = io.open(P, encoding='utf-8').read()
names = set(m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s))
have = set(re.findall(r'"([^"]{2,60})":\{\s*long:', s))

BAN = [re.compile(r'(this|the)\s+(pattern|setup|signal)[^.]{0,40}\b\d{1,3}\s?%', re.I),
       re.compile(r'success rate', re.I),
       re.compile(r'win rate of\s+\d', re.I),
       re.compile(r'\d{1,3}\s?% (?:accurate|reliable|of trades win)', re.I),
       re.compile(r'\bwill\s+(?:go|reverse|continue)\b', re.I),
       re.compile(r'\bguaranteed\b', re.I)]

bad, ok = [], {}
for k, v in entries.items():
    if not isinstance(v, dict) or 'long' not in v or 'usage' not in v or 'see' not in v:
        bad.append('MALFORMED: ' + k); continue
    if k not in names:
        bad.append('NOT A TERM: ' + k); continue
    if k in have:
        bad.append('ALREADY WRITTEN (skipping): ' + k); continue
    if len(v['long'].split()) <= 80:
        bad.append('TOO SHORT: ' + k); continue
    if 'Where people get fooled:' not in v['long']:
        bad.append('MISSING fooled-paragraph: ' + k); continue
    hit = next((rx.pattern[:38] for rx in BAN if rx.search(v['long'] + ' ' + v['usage'])), None)
    if hit:
        bad.append('BANNED (%s): %s' % (hit, k)); continue
    dead = [t for t in v['see'] if t not in names]
    if dead:
        bad.append('DEAD SEE-LINK: %s -> %s' % (k, dead)); continue
    ok[k] = {'long': v['long'], 'usage': v['usage'], 'see': v['see'][:5]}

print('fragment: %s  entries=%d  accepted=%d  rejected=%d' % (FRAG, len(entries), len(ok), len(bad)))
for b in bad:
    print('  REJECT ', b)

if not ok:
    print('nothing to merge'); sys.exit(2)

anchor = 'Economic rationale"]},\n\n'
assert anchor in s
parts = []
for k, v in ok.items():
    parts.append(json.dumps(k) + ':{\nlong:' + json.dumps(v['long']) +
                 ',\nusage:' + json.dumps(v['usage']) +
                 ',\nsee:' + json.dumps(v['see']) + '}')
s = s.replace(anchor, anchor + ',\n\n'.join(parts) + ',\n\n', 1)
io.open(P, 'w', encoding='utf-8').write(s)
print('merged %d entries, %d words' %
      (len(ok), sum(len((v['long'] + v['usage']).split()) for v in ok.values())))
