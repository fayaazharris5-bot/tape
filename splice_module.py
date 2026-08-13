# -*- coding: utf-8 -*-
# Append an agent-built UI module (one <script> + one <style>) to index.html
# with the same paranoia the content merges get. Usage: splice_module.py <file>
import io, re, sys

if len(sys.argv) != 2:
    print('usage: splice_module.py <module_file.html>'); sys.exit(1)

frag = io.open(sys.argv[1], encoding='utf-8-sig').read()

# structural checks
scripts = re.findall(r'<script(?:\s[^>]*)?>', frag)
styles = re.findall(r'<style(?:\s[^>]*)?>', frag)
errs = []
if len(scripts) != 1 or frag.count('</script>') != 1:
    errs.append('must contain exactly one <script> block (found %d/%d)' % (len(scripts), frag.count('</script>')))
if len(styles) != 1 or frag.count('</style>') != 1:
    errs.append('must contain exactly one <style> block (found %d/%d)' % (len(styles), frag.count('</style>')))
if 'document.getElementById' not in frag:
    errs.append('script lacks the document.getElementById literal (bare-eval exclusion)')

# content bans — same policy as the writing pipeline
BAN = [(r'success rate', 'success-rate claim'),
       (r'win rate of\s+\d', 'numeric win-rate claim'),
       (r'\d{1,3}\s?% (?:accurate|reliable|of trades win)', 'accuracy-percent claim'),
       (r'\bwill\s+(?:go|reverse|continue)\b', 'prediction language'),
       (r'guaranteed\s+(returns?|profits?|income|wins?)', 'guarantee claim'),
       (r'type="password"', 'password field'),
       (r'id="[^"]*(apikey|api-key|token|secret|password)[^"]*"', 'credential-named input'),
       (r'name="[^"]*(apikey|api-key|token|secret|password)[^"]*"', 'credential-named input'),
       (r'(?:src|href)="https?://', 'external resource reference')]
ALLOW_URL = 'api.binance.com/api/v3/ticker/price'
for rx, label in BAN:
    for m in re.finditer(rx, frag, re.I):
        ctx = frag[max(0, m.start()-60):m.end()+60]
        if label == 'external resource reference' and ALLOW_URL in ctx:
            continue
        errs.append('%s: ...%s...' % (label, ctx.replace('\n', ' ')[:110]))

if errs:
    print('REJECTED %s:' % sys.argv[1])
    for e in errs: print('  ', e)
    sys.exit(2)

s = io.open('index.html', encoding='utf-8').read()
marker = '<!-- module: %s -->' % sys.argv[1]
if marker in s:
    print('already spliced — refusing to duplicate'); sys.exit(3)
s = s.rstrip() + '\n' + marker + '\n' + frag.strip() + '\n'
io.open('index.html', 'w', encoding='utf-8').write(s)

o = len(re.findall(r'<script(?:\s[^>]*)?>', s)); c = s.count('</script>')
print('spliced %s  script tags now %d/%d %s' % (sys.argv[1], o, c, 'OK' if o == c else 'IMBALANCED'))
