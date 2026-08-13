# Tape — session handoff. Read fully, then continue.

Repo: `C:\Users\fayaa\Downloads\tape`.
**995 terms, 5 tabs, suite green at 252 assertions.**

```bash
cd C:\Users\fayaa\Downloads\tape
npm i jsdom     # if node_modules missing
node test.js    # MUST print PASSED before any change
```

Never pipe the test run when you need its status: `node test.js > out 2>&1; echo $?`.
Python is `py -3` on this machine — plain `python` hits the Store shim and fails.

## Already DONE — do not redo

- Content merged and wired. Long-form bodies exist for the sections listed
  under "content status" below. Every merge went through
  `py -3 merge_agent.py <file>` with its ban-regex and whitelist checks.
- Modules spliced AND wired: `module_first.html`, `module_path.html`,
  `module_paper.html`. splice_module.py refuses duplicates via marker comments.
- **Paper tab verified in a real browser** (Node static server; `file://`
  blocks scripts). Full click-through passed: open with stop → derived size
  (risk budget ÷ stop distance, arithmetic shown) → mark → close → R written
  to the linked strategy as `{d,dir,r,n:"paper"}`.
- **Bug found and fixed during that verification** (commit `9bd79ee`): the
  strategy dropdown was always empty and R-logging was dead. Boot marks
  `tape.migrated` before the Strategies tab first saves, so `tape.strats.v1`
  never exists on a fresh profile — the library lives under the OLD
  `tg.strats.v1` name. Paper now reads the live key first, writes back to
  whichever key the list came from, keeps `sampleSize` in step, and fires
  `tape:strats-changed` so the Strategies tab re-renders without a reload.
  Test group 20 covers the whole loop.
- **SM-2 quiz** (commit `8a90589`): per-term `ef`/`reps`/`iv`/`due` alongside
  the legacy `{n,w}`. Correct → quality 4, wrong → quality 1 (multiple choice
  carries no hesitation signal, so middle grades are unused). Due and unseen
  terms are asked first; when everything is scheduled ahead it reviews early,
  soonest-due first. Old records schedule as if unseen. Test group 21.
- **Strategy detail view** (commit `453c118`): Detail button on every card
  opens a read-only overlay — rules, full metrics (win rate never without
  expectancy beside it), payoff ratio, equity curve, R histogram, and
  long/short + paper/hand splits each carrying a too-few-to-read caveat.
  Deep-linkable via `#strategies&s=<key>`, Escape closes. Logging stays on
  the card so input ids exist exactly once. Test group 22.

## Content status

`py -3 list_unwritten.py` regenerates `unwritten.json` (terms lacking a long
body, grouped by section code) and prints the totals. Run it after ANY content
change — the wave-3 writer briefs read their term lists straight from it.

Written this session: crypto+prop (52), macro+econ (49), portfolio/factor/
participants (42), indicators (11+23), fibonacci/waves/harmonics (11),
red flags (14), forex (14), trading operations (17), basics+pa (7).

Remaining sections had writers dispatched; check `unwritten.json` for the
current truth rather than trusting this list.

## Writer pipeline — how content gets made

One agent per section group, each writing ONE json file, never touching
index.html. Brief template (this exact shape has a high first-pass accept rate):

- Read `unwritten.json`, take EXACTLY the terms under keys `<x>`, `<y>`.
- Read `valid_names.json`; every `see` name must match exactly. **Section
  names are NOT valid see targets** — this was the only repeated reject.
- Format: `{"Term":{"long","usage","see"}}`; long = 3-4 paragraphs joined by
  `\n\n`, 150-200 words, final paragraph starts exactly
  `"Where people get fooled:"`; usage 1-2 sentences, never advice; see = 3-5
  whitelist names. Voice: plain, direct, quietly sceptical, mechanism-first,
  British spelling.
- Bans (regex-enforced by merge_agent.py): "success rate"; "win rate of
  <digit>"; "<n>% accurate/reliable/of trades win"; % attached to this/the
  pattern/setup/signal; the words "undefined" and "NaN" in prose; "will
  go/reverse/continue"; "guaranteed returns/profits/income/wins". No invented
  statistics.
- Plus a per-section accuracy stance (what the honest mechanism is, which
  documented origins to credit, what the standard trap is).
- Verify the JSON parses and zero whitelist misses before writing; report counts.

Then: `py -3 merge_agent.py <file>` → `node test.js` → commit.
Rejects print the reason; fix in a small `_fix.json` and re-merge.

**Agents die at session/credit limits and their files never land.** When that
happens, write the section in-session instead — same format, same merge path.
Sonnet writers work fine for this and cost less.

## Settled policy — do not relitigate

- Ban the CLAIM, not the word (user-confirmed): filters target numeric
  win-rate claims, "guaranteed returns", pattern-attributed percentages —
  never criticism, worked arithmetic, or correct mechanics. If a filter
  rejects honest content, narrow the filter and say so in the commit.
- English "undefined"/"NaN" in prose: reword the prose, keep the guard.
  (The Data quality entry legitimately discusses NaNs in a feed; the NaN
  assertion is scoped to chart SVG output for exactly this reason.)
- Strategy library EMPTY BY DESIGN (provenance guard, test group 18). Rules
  enter only dictated by the user or from a named file. Never attribute
  rules to TJR/ICT/anyone. Eleven seed strategies were deleted in `00cc3c0`
  because their rules were written from recall and then given citations.
- No credentials ever; no live orders; no signal generation; simulation only.
- Intended content changes may update test constants/fixtures WITH a comment
  (precedent throughout test.js); behaviour regressions never may.

## Traps (each cost real time once)

- Bash heredocs eat backslashes -> write scripts via the Write tool.
- Piped test runs mask exit codes.
- Term-object key order: alt AFTER c:, never between t: and c:.
- Test harness bare-evals blocks lacking the literal document.getElementById.
- Hard-coded fixtures go stale as writing progresses — keep fixtures dynamic.
- jsdom polyfills (TextEncoder/CompressionStream) in boot() must stay.
- merge_agent.py's ALIAS map handles renamed/deleted see-link targets;
  extend it on any new dedupe.
- Long bodies live in separate `L={...}` blocks keyed by term NAME, not
  inside the term objects — that is why list_unwritten.py diffs names
  against `"Name":{long:` matches rather than parsing term chunks.
- `python` is not on PATH; use `py -3`.

## whitelist regeneration (after any content/dedupe change)

```python
import io, re, json
s = io.open('index.html', encoding='utf-8').read()
names = sorted(set(m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)))
io.open('valid_names.json','w',encoding='utf-8').write(json.dumps(names))
print(len(names))
```

## Blocked on the user — never guess

- GitHub username -> publish via README commands.
- The user's strategy rules (10am/10pm session play; TJR) -> dictated
  verbatim, one field at a time, else the library stays empty.
- Strategy Lab path -> then sync_strategies.py per the user's Task 11 mapping
  (sampleSize = real trade count; "backtested" only for OOS/walk-forward;
  random-walk-gate failures stay untested with the failure in results).

## Next queue

1. Merge whatever writer files have landed; re-run list_unwritten.py.
2. Write any section whose writer died, in-session.
3. Second/third charts (viz2) for the priority structural terms.
4. Responsive + offline-from-file check at 360/768/1440 in both schemes.

## Publishing

Artifact URL (pass as `url` when publishing from a new conversation):
https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016
Also keep C:\Users\fayaa\Downloads\index.html and test.js synced (plain copies).
