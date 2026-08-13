"""Corpus-wide audit of every long-form body already spliced into index.html.
merge_agent.py enforces these at merge time; this re-checks the file itself,
so hand-edits and older merges are covered too."""
import io, re, sys

s = io.open('index.html', encoding='utf-8').read()

BANS = [
    ("success rate",            r"success rate"),
    ("win rate of <digit>",     r"win rate of \s*\d"),
    ("N% accurate/reliable",    r"\d+\s*%\s*(accurate|reliable)"),
    ("N% of trades win",        r"\d+\s*%\s*of\s+trades\s+win"),
    ("% on pattern/setup",      r"(this|the)\s+(pattern|setup|signal)[^.]{0,40}\d+\s*%"),
    ("will go/reverse/continue",r"will\s+(go|reverse|continue)\b"),
    ("guaranteed returns",      r"guaranteed\s+(returns|profits|income|wins)"),
]

bodies = re.findall(r'"((?:[^"\\]|\\.)*)":\{[\s\n]*long:"((?:[^"\\]|\\.)*)"', s)
print("long-form bodies found:", len(bodies))

hits = 0
for name, body in bodies:
    text = body.replace('\\n', ' ').replace('\\"', '"')
    for label, pat in BANS:
        for m in re.finditer(pat, text, re.I):
            hits += 1
            lo = max(0, m.start() - 50)
            print("  HIT [%s] in %s: ...%s..." % (label, name, text[lo:m.end() + 50]))

# structural checks.
# "Reality check on this section" is a section-level essay rather than a term
# entry — the whole body is the caveat, so it has no closing paragraph.
EXEMPT = {"Reality check on this section"}
missing_fooled = [n for n, b in bodies
                  if "Where people get fooled:" not in b and n not in EXEMPT]
print("bodies missing the 'Where people get fooled:' paragraph:", len(missing_fooled))
for n in missing_fooled[:10]:
    print("   ", n)

print("TOTAL BAN HITS:", hits)
sys.exit(1 if hits or missing_fooled else 0)
