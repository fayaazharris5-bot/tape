# Tape — project instructions

A single self-contained `index.html`: a trading glossary and honest trade
journal. 995 terms, all with long-form bodies. 5 tabs: Terms, Strategies,
Quiz, Live chart, Paper. No build step, no dependencies, no server.

**Read `HANDOFF.md` before doing anything substantial** — it carries current
state, what is already done, the writer pipeline, and the traps that have each
cost real time once.

## Before and after every change

```bash
py -3 check.py                       # runs ALL gates, exits non-zero if any fail
py -3 check.py --quick               # same without the slow test suite
```

The gates individually, if you need one on its own:

```bash
node test.js > out 2>&1; echo $?     # must be 0. Never pipe and trust the pipe.
py -3 audit_claims.py                # exits non-zero on any banned claim
py -3 audit_coverage.py              # exits non-zero on missing fields
py -3 audit_contrast.py              # exits non-zero if a text token drops below WCAG AA
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
  → **DONE.** Path confirmed by direct inspection on 2026-08-14:
  `C:\Users\fayaa\Downloads\ai trading thing\strategy-lab`, carrying `engine/`,
  `daily.py`, `config.json`, `NEXT.md` and `results/PREDICTIONS.md`.
  `sync_strategies.py` is written and run. See "Strategy Lab bridge" below.

## Strategy Lab bridge — `sync_strategies.py`

```bash
py -3 sync_strategies.py            # top 20, realistic costs, writes strategies.json
py -3 sync_strategies.py --gate-only   # only rows clearing the full gate
```

Then load `strategies.json` through the app's existing **Import** button. No
"Load from Strategy Lab" button was added: a web page cannot read a fixed local
path, so it would have been a second file picker beside the first — exactly the
"feature whose main effect is more features" the list below rules out.

The Lab's database is `results/results.db`, table `honest_runs`. Schema as
inspected: `oos_n_trades, oos_win_rate, oos_expectancy, oos_profit_factor,
oos_payoff_ratio, oos_max_drawdown, oos_sharpe, oos_dsr, oos_p_value,
oos_trials_to_kill, vs_random, vs_buy_and_hold, flags, cost_model, params`.
Cost models are `realistic_v1` and `flat_legacy` — **not** `brutal_v1`.

What the data actually says, measured on 2026-08-14 and not to be softened:

- Ledger: **58,698 rows**. Best `oos_trials_to_kill` anywhere: **3,670**.
  Best deflated Sharpe: **0.18**. Rows with DSR > 0.95: **zero**.
- So **nothing clears the gate**, every export is `untested`, and `--gate-only`
  exits 2 with that stated plainly. That is the correct result and it matches
  the Lab's standing finding — it is not a bug in the script.
- The gate is `vs_random > 0` **and** `oos_trials_to_kill >= <rows in
  honest_runs>`. Both halves are the Lab's own numbers; no threshold was
  invented here. `vs_random > 0` alone passes 1,886 rows and means nothing at
  this trial count — beating one random draw is what noise does.
- **Expectancy is in account currency, not R.** The brief asked for R; the
  engine does not produce it. The sentence says which it is rather than
  relabelling dollars as R.
- Rows are deduped to one per strategy/asset/timeframe — the table holds many
  near-identical re-runs of the same variant.

## Do not build unless asked

Accounts, login, a backend, a database, or any server. Storage of broker
credentials or account numbers. Automated order placement, mirroring, or trade
copying. Price prediction or signal generation. A second chart engine, a CSS
framework, or a build step. Any feature whose main effect is that the app has
more features.

## Publishing

Never hand `index.html` to the Artifact publisher directly — it wraps the
file in its own document skeleton. Run `py -3 build_artifact.py` first and
publish the `artifact_tape.html` fragment it produces. See HANDOFF.md for
the details and the pre-publish verification.

Current artifact:
`https://claude.ai/code/artifact/24dc6b25-6da7-4603-9171-32356c72db13`
(republish the same file path in the same conversation to keep this URL, or
pass it as `url` from a new one).

Keep `C:\Users\fayaa\Downloads\index.html` and `test.js` synced as plain copies.
