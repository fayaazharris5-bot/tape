# Tape — session handoff. Read fully, then continue the work.

Repo: `C:\Users\fayaa\Downloads\tape`. Baseline: commit `11af0cb`,
**222 of 995 terms carry long-form bodies, suite green (224 assertions)**.

```bash
cd C:\Users\fayaa\Downloads\tape
npm i jsdom        # if node_modules missing
node test.js       # MUST print PASSED before you change anything
```

Check the suite's exit code directly — do NOT pipe `node test.js` through
grep/tail and trust the pipeline status; a masked exit code already caused one
red commit this project.

## 1. FIRST JOB — merge the seven in-flight agent deliveries

Seven background agents were writing when the previous session ended. They
deliver **files into this folder**; completion notifications went to the dead
session, so just check the disk. Expected files (some may already exist —
`agent_orders/palev/stat.json` are ALREADY MERGED, ignore them):

| File | Contents | Merge with |
|---|---|---|
| `agent_futcomm.json` | 47 futures/commodities/derivatives bodies | `python merge_agent.py agent_futcomm.json` |
| `agent_opt.json` | 57 options bodies | `python merge_agent.py agent_opt.json` |
| `agent_cryprop.json` | 52 crypto + prop-firm bodies | `python merge_agent.py agent_cryprop.json` |
| `agent_macro.json` | 49 macro/econ/cycle bodies | `python merge_agent.py agent_macro.json` |
| `module_first.html` | "Read this first" honest page | `python splice_module.py module_first.html` |
| `module_path.html` | "Start here" guided learning path | `python splice_module.py module_path.html` |
| `module_paper.html` | Paper-trading tab (Task 9) | `python splice_module.py module_paper.html` + wiring below |

Procedure per file, one at a time, in the table's order:
1. Run the merge/splice command. Both tools VALIDATE before touching
   `index.html` and print per-entry rejections. Rejections are usually the
   filter being right — but three past rejections were the filter being too
   blunt (see policy below). Inspect each rejection before deciding.
2. `node test.js` — check exit code. Fix the change, never weaken a test.
   If a test fails because content legitimately changed (counts, a fixture
   term got written), update the constant/fixture WITH a comment explaining
   why — precedent: EXPECT_TERMS/EXPECT_CHARTS comments already in test.js.
3. Commit with a one-line message. One merge per commit.
4. After ALL content merges: regenerate the whitelist —
   the long-body count and term coverage changed:
   run the snippet in "whitelist" below.

### Paper-tab wiring (only for module_paper.html)
The module self-wires its own click handler, but the app's router must know
it: in `index.html` find `var PANELS=[` and `var TABIDS={` (strategies/routing
module) and add `["paper","panel-paper"]` and `paper:"tab-paper"` respectively.
Then verify IN A REAL BROWSER (serve the folder; file:// blocks scripts):
open the Paper tab, open a position with a stop (size must be DERIVED and
refuse at 0 contracts), mark a price, close it, and confirm the trade appears
in the linked strategy's log as `{d,dir,r,n:"paper"}`. Confirm costs were
charged (fill worse than entry by 1 tick, commission both sides). Also click
every other tab afterwards — the panel must hide when they show.

## 2. Content policy — settled decisions, do not relitigate

- **Ban the claim, not the word** (user-confirmed). Filters target numeric
  win-rate claims, "guaranteed returns", pattern-attributed percentages —
  NOT criticism of win rates, worked arithmetic, or correct mechanics like
  "guaranteed exit with unknown cost". If a filter rejects honest content,
  narrow the filter, and say so in the commit.
- English words "undefined"/"NaN" in bodies trip the JS-leak guard: REWORD
  the sentence (meaning survives), don't touch the guard.
- Strategy library is EMPTY BY DESIGN (11 invented-rule entries were purged;
  provenance guard in test group 18 enforces it). Rules enter only if the
  user dictates them or names a file. Never attribute rules to TJR/ICT/anyone.
- No credentials anywhere, ever — tests scan for password/token/secret/apikey
  fields. No live-order placement, no signal generation, no invented stats.
- Voice: plain, direct, quietly sceptical, mechanism-first, British-ish.
  Final long-body paragraph starts "Where people get fooled:".

## 3. After the merges — the queue, in order

1. **Wave-3 writers** for the remaining ~490 unwritten terms. Proven recipe:
   spawn background agents, ~40-55 terms each, prompt skeleton = any wave-2
   brief (they're in this session's pattern: exact term list + whitelist +
   format + voice exemplar + regex bans + self-check). Extract per-section
   todo lists first:
   remaining sections ≈ ind, ind2, cpat, chpat, fib, wyc, flow, exec, port,
   data, auto, cost, reg, au, eq, rates, etf, factor, perf, part, riskt,
   cycle-leftovers, tech, money, mgmt, style, slang, psy-leftovers,
   risk-leftovers, stat/bt leftovers.
2. **SM-2 quiz upgrade** (user's Task 8): replace weighted repetition with
   SM-2 intervals, daily due-queue, streak, per-section mastery, a mode that
   shows a strategy's rules and asks which concept. Storage under tape.* with
   try/catch. This EDITS the existing quiz module — do it in this session,
   not via agent (same-file surgery).
3. **Strategy detail view** (user's Task 7B): checklist from entry/invalidation
   fields, MAE/MFE columns, stop-width/target-reach readout, concepts-used
   chips (reverse matcher), NY↔Perth session times, dated notes timeline.
   Also same-file surgery — this session, not an agent.
4. Remaining dupe candidates to inspect when writing reaches them:
   pa "Engulfing" vs cpat "Bullish/Bearish engulfing" (kept deliberately so
   far); "Chop" pa/slang pair is DELIBERATE, keep.

## 4. Traps that have each cost real time — do not rediscover

- **Bash heredocs eat backslashes** (`\b`→backspace, `\\`→`\`). Any script
  containing regex or JS goes through the Write tool to a file, then run.
- **Piped test runs mask failures.** `node test.js > /tmp/t.out 2>&1; echo $?`.
- **Term-object key order matters to every regex**: `{t:"...",c:"...",alt:...}`
  — alt goes AFTER c:, never between t: and c:.
- **The test harness bare-evals script blocks lacking the literal
  `document.getElementById`** — UI modules must contain it; data blocks must
  stay runnable with no window/document.
- **Hard-coded test fixtures go stale as writing progresses** — the stub-panel
  fixture is dynamic now; keep new fixtures dynamic too.
- **jsdom version drift**: harness polyfills TextEncoder/CompressionStream;
  don't remove them.
- Agents' see-links may target names deleted in dedupes — merge_agent.py's
  ALIAS map handles known ones; extend it if a new rename happens.

## whitelist (regenerate after any content/dedupe change)

```python
import io, re, json
s = io.open('index.html', encoding='utf-8').read()
names = sorted(set(m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)))
io.open('valid_names.json','w',encoding='utf-8').write(json.dumps(names))
print(len(names))
```

## 5. Blocked on the user — ask only when relevant, never guess

- **GitHub username** → publish via README commands (`USERNAME.github.io/tape`).
- **The user's strategy rules** (10am/10pm session play; TJR) → dictated
  one field at a time, verbatim, else the library stays empty.
- **Strategy Lab path confirmation** → then write sync_strategies.py per the
  mapping rules in the user's Task 11 (sampleSize = real trade count;
  "backtested" only for OOS/walk-forward; control-gate failures stay untested).

## Definition of done for the merge job
All seven deliveries merged or explicitly rejected with reasons, suite green,
paper tab browser-verified, one commit each, artifact republished
(`https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016` —
pass this URL as `url` when publishing from a new conversation), and a short
report: accepted/rejected counts per file, coverage total, what's next.
