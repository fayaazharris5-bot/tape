# -*- coding: utf-8 -*-
"""Regenerate valid_names.json from index.html.

Lives as a file rather than a -c one-liner on purpose: the shell eats the
backslashes in this regex, which is the trap recorded in HANDOFF.md.

    py -3 regen_whitelist.py
"""
import io, json, re

s = io.open('index.html', encoding='utf-8').read()
names = sorted(set(
    m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)
))
io.open('valid_names.json', 'w', encoding='utf-8').write(json.dumps(names))
print('whitelist regenerated: %d names' % len(names))
