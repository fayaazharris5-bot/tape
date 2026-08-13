# Tape — project instructions

A single self-contained `index.html`: a trading glossary and honest trade
journal. 995 terms, all with long-form bodies. 5 tabs: Terms, Strategies,
Quiz, Live chart, Paper. No build step, no dependencies, no server.

**Read `HANDOFF.md` before doing anything substantial** — it carries current
state, what is already done, the writer pipeline, and the traps that have each
cost real time once.

## Before and after every change

```bash
node test.js > out 2>&1; echo $?     # must be 0. Never pipe and trust the pipe.
py -3 audit_claims.py                # exits non-zero on any banned claim
py -3 audit_coverage.py              # exits non-zero on missing fields
```

`python` is not on PATH on this machine — use `py -3`.

Commit after every task, one task per commit. Never batch.

## Non-negotiables

1. ONE self-contained `index.html`. No framework, bundler, or build step.
   jsdom as a devDependency for testing only.
2. All terms and charts keep rendering. New charts reuse the existing engine —
   never write a second one.
3. **Never invent trading rules, and never attribute rules to a named person.**
   If the rules did not come from the user in-session or from a file the user
   named, the field stays blank. Eleven seed strategies were deleted in
   `00cc3c0` for exactly this — their rules were written from recall and then
   given citations, which made recalled text look sourced.
4. No invented statistics, win rates, edges, or success percentages anywhere.
   Audit scripts enforce this over the whole corpus.
5. Never weaken the evidence model: badges always show sample size, forms
   reject backtested/forward-tested/live at sample size 0, logged trades always
   override typed-in numbers.
6. All user and imported text stays HTML-escaped. Share links carry untrusted
   JSON from other people — that path must never inject markup.
7. localStorage access stays wrapped in try/catch with in-memory fallback.
8. **No credentials, ever.** No field, form, or storage path that accepts an
   API key, secret, token, password, or account number — not even for a paper
   or demo account. Tests scan for this.
9. Nothing places, sizes for real money, mirrors, or recommends a live trade.
   Simulation and record-keeping only. No signal generation, no price
   prediction, no "this setup is X% likely".
10. If a test fails, fix the change — not the test. Intended content changes
    may update a constant or fixture, but only with a comment saying why.

## Voice

Plain, direct, quietly sceptical, mechanism-first, British-leaning spelling.
Explain why a thing happens mechanically, then how it is used, then how it
fools people. Every long-form body's final paragraph starts exactly
`Where people get fooled:`. No hype, no emoji, no second-person sales tone.

Where a concept is contested or unvalidated, say so. Where it has an older
documented name, credit it — a spring is a liquidity sweep, AMD is Wyckoff's
cycle, turtle soup is Connors and Raschke.

## Still blocked on the user — ask, never guess

These three are the only things standing between this and a finished,
published, populated app. Whichever chat the user answers in, **write the
answer into this file immediately**, then act on it.

- **GitHub username** — publishing is two commands in `README.md`; the site
  lands at `https://USERNAME.github.io/tape/`. Nothing has been pushed.
  → username:
- **The user's own strategy rules** — including a session play around the 10am
  and 10pm windows, and one from the creator TJR. Take them one field at a
  time, verbatim. If the user is vague about a field, ask rather than filling
  it. Everything starts untested at sample size 0 unless real numbers are
  given. The library is empty by design until then.
  → rules recorded:
- **Strategy Lab path** — a separate Python backtesting engine on this machine
  (walk-forward, 70/30 split, 2x costs, random-walk control gate, writing to
  `results/PREDICTIONS.md` and `NEXT.md`). Believed to be
  `C:\Users\fayaa\Downloads\ai trading thing\strategy-lab` but must be
  confirmed, not assumed. Then write `sync_strategies.py`: sampleSize is the
  real trade count; evidence is "backtested" only for out-of-sample or
  walk-forward results; control-gate failures stay "untested" regardless of
  returns, with the failure recorded in results; fields the engine does not
  produce stay empty.
  → path confirmed: **YES** — `C:\Users\fayaa\Downloads\ai trading thing\strategy-lab`
  exists and carries the markers this file describes: `engine/`, `daily.py`,
  `config.json`, `NEXT.md`, and `results/PREDICTIONS.md` (alongside
  `PBO_REPORT.md` and the tier lists). Verified by direct inspection on
  2026-08-14, not inferred. `sync_strategies.py` is NOT written yet — that
  is the next step and has not been asked for.

## Do not build unless asked

Accounts, login, a backend, a database, or any server. Storage of broker
credentials or account numbers. Automated order placement, mirroring, or trade
copying. Price prediction or signal generation. A second chart engine, a CSS
framework, or a build step. Any feature whose main effect is that the app has
more features.

## Publishing

Preview artifact (pass as `url` when publishing from a new conversation so the
link stays stable):
`https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016`

Keep `C:\Users\fayaa\Downloads\index.html` and `test.js` synced as plain copies.
