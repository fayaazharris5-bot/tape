# -*- coding: utf-8 -*-
"""Colour-contrast gate: every text token must clear WCAG AA (4.5:1).

The stylesheet layers several :root blocks — an early one is deliberately
overridden by a later "visual pass" block that wins ties. Auditing every
block would flag values that never apply, so this resolves the EFFECTIVE
palette the way the cascade does: for each of the four theme contexts,
the last declaration wins.

  light base      last plain  :root{...}
  light explicit  last        :root[data-theme="light"]{...}
  dark media      last block inside @media (prefers-color-scheme:dark)
  dark explicit   last        :root[data-theme="dark"]{...}

Exits non-zero if any foreground/background pair falls below 4.5:1, so it
works as a gate beside audit_claims.py and audit_coverage.py.

    py -3 audit_contrast.py
"""
import io, re, sys

SRC = 'index.html'
AA = 4.5

FOREGROUNDS = ['--ink', '--ink2', '--ink3', '--up', '--down', '--accent', '--signal']
BACKGROUNDS = ['--paper', '--card']


def srgb(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_colour):
    h = hex_colour.lstrip('#')
    if len(h) == 3:
        h = ''.join(ch * 2 for ch in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def contrast(fg, bg):
    l1, l2 = luminance(fg), luminance(bg)
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def tokens(block):
    return dict(re.findall(r'(--[a-z0-9]+)\s*:\s*(#[0-9A-Fa-f]{3,6})', block))


def blocks_matching(s, selector_re):
    """Every {...} block whose selector matches, in source order."""
    out = []
    for m in re.finditer(selector_re + r'\s*\{([^{}]*)\}', s):
        out.append(m.group(1))
    return out


def split_dark_media(s):
    """Return (source-without-dark-media, [dark-media-bodies]).

    A :root nested inside @media (prefers-color-scheme:dark) also matches a
    plain :root pattern, which would let a dark block masquerade as the
    light base. Cut those regions out first. Braces are matched by counting
    rather than by a lazy regex, because these blocks nest.
    """
    bodies, keep, i = [], [], 0
    for m in re.finditer(r'@media\s*\([^)]*prefers-color-scheme\s*:\s*dark[^)]*\)\s*\{', s):
        start = m.end() - 1               # at the opening brace
        depth, j = 0, start
        while j < len(s):
            if s[j] == '{':
                depth += 1
            elif s[j] == '}':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        keep.append(s[i:m.start()])
        bodies.append(s[start + 1:j])
        i = j + 1
    keep.append(s[i:])
    return ''.join(keep), bodies


def dark_media_blocks(bodies):
    out = []
    for b in bodies:
        out.extend(blocks_matching(b, r':root'))
    return out


def main():
    s = io.open(SRC, encoding='utf-8').read()

    light_src, dark_bodies = split_dark_media(s)

    contexts = {}
    plain = [b for b in blocks_matching(light_src, r'(?<![\]\w]):root(?!\[)') if '--paper' in b]
    if plain:
        contexts['light base'] = tokens(plain[-1])
    for name, sel, src in (('light explicit', r':root\[data-theme="light"\]', light_src),
                           ('dark explicit', r':root\[data-theme="dark"\]', s)):
        b = [x for x in blocks_matching(src, sel) if '--paper' in x]
        if b:
            contexts[name] = tokens(b[-1])
    dm = [x for x in dark_media_blocks(dark_bodies) if '--paper' in x]
    if dm:
        contexts['dark media'] = tokens(dm[-1])

    # Sanity: if a light and a dark context resolve to the same --paper the
    # resolver has mis-attributed a block, and every ratio below is fiction.
    lights = [c.get('--paper') for k, c in contexts.items() if k.startswith('light')]
    darks = [c.get('--paper') for k, c in contexts.items() if k.startswith('dark')]
    if lights and darks and set(lights) & set(darks):
        print('RESOLVER ERROR: a light and a dark context share --paper %s — '
              'the cascade was mis-read, so these ratios cannot be trusted.'
              % (set(lights) & set(darks)))
        return 1

    if not contexts:
        print('no theme blocks found — has the stylesheet structure changed?')
        return 1

    failures = 0
    for name, t in contexts.items():
        print('\n%s' % name)
        for bg in BACKGROUNDS:
            if bg not in t:
                continue
            for fg in FOREGROUNDS:
                if fg not in t:
                    continue
                r = contrast(t[fg], t[bg])
                flag = 'AA' if r >= AA else 'BELOW AA'
                if r < AA:
                    failures += 1
                print('  %-9s on %-8s %5.2f  %s' % (fg[2:], bg[2:], r, flag))

    print('\ncontexts checked: %d | pairs below AA: %d' % (len(contexts), failures))
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
