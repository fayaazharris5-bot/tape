# Tape — session handoff. Read fully, then continue.

Repo: `C:\Users\fayaa\Downloads\tape`.
**995 terms, 5 tabs, suite green at 261 assertions.**

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

## Content status — COMPLETE

**All 995 terms carry a long-form body.** `py -3 list_unwritten.py` prints
`unwritten 0`. Run it after ANY content change; it regenerates
`unwritten.json`, which is what writer briefs read their term lists from.

Two audit scripts, both exiting non-zero on a finding so they work as
gates. Run them after content changes alongside the suite:

- `py -3 audit_claims.py` — re-checks every body actually spliced into
  index.html: the ban regexes, and that each closes with the
  "Where people get fooled:" paragraph. Currently 994 bodies, 0 hits.
- `py -3 audit_coverage.py` — field coverage. Currently 0 bodies missing
  `usage`, 0 missing `see`, 0 terms missing an example, 48 sections.

Body count is 994 for 995 terms because **"Chop" exists twice** — once in
`pa`, once in `slang` — with near-identical definitions, so both cards
share the one body. This is a pre-existing near-duplicate of the same
class as the 11 removed in earlier dedupe passes, and it was left alone
deliberately: deduping changes EXPECT_TERMS, needs see-links re-pointed
and the ALIAS map extended, and is a curation call for the user. Nothing
is broken by it — both cards render correctly.

## Next content work

Not more terms, and not more charts on the structural set — both are done.
`audit_coverage.py` reports 0 bodies missing `usage`, 0 missing `see`, and
0 terms missing an example.

**Counter-case charts.** 17 terms carry a `viz2` second chart, and the
principle is deliberate: each entry's prose already argues the pattern is
ambiguous live and obvious only in hindsight, so showing only the version
that worked teaches it as a signal. The second chart is always the case
that looks identical and resolves the other way. Added by `add_viz2.py`
(existing charts) and `add_charts.py` (terms that had none). Both are
idempotent and reuse the one engine — never write a second renderer.

`viz2` renders in the detail panel only, so it never changes the grid
chart count. A new `v:` does — that is why EXPECT_CHARTS moved 72 -> 75
when BOS, CHoCH and False breakout were charted, commented at the
constant in test.js.

If you extend this: captions go through the same honesty filters as
bodies. One of mine was rejected for saying "which way it will go" — the
banned-prediction guard working correctly. Reword the caption, never the
guard.

## Getting a bot's results in — the honest integration

There is **no trading bot on this machine**. Searched on 2026-08-14:
`strategy-lab` is a research backtester, `tradingview-mcp` is a market-data
MCP server, `New Folder/backtest-engine-spec.txt` and `B-master-trading.md`
are specs. The only broker-API code anywhere is `ccxt` sitting inside
`strategy-lab/.venv` as a library dependency — not bot code the user wrote.

So "integrate the bot" means **ingesting whatever a bot produces**, which
Tape already does two ways, both record-keeping only:

1. **Statement import** (Strategies tab) — the general path. It now handles
   three shapes: one row per completed trade with a P&L column; one row per
   trade with entry/exit to derive P&L from; and **fill logs**, where each
   row is one leg. ccxt, most exchange exports and most bots emit the third
   kind, and it used to import as zero trades. Fills are paired FIFO per
   symbol, fees charged pro-rata to the matched quantity, still-open
   positions reported as skipped rather than closed at an invented price,
   and over-closing treated as a reversal. The report says plainly that
   trades were reconstructed and on what basis. Test group 23.
2. **Strategy Lab bridge** — `sync_strategies.py`, then the Import button.

What must NOT be built, per non-negotiables 8 and 9: order placement,
credentials of any kind, mirroring, copy-trading, or signal generation.
A bot that *executes* is out of scope; a bot's *record* is exactly what
this app is for.

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
- **`unwritten.json` is a live queue, not a static spec.** Regenerating it
  while writer agents are running makes it shrink under them; two agents
  noticed and stopped to investigate, and one nearly abandoned correct work
  because its section had vanished from the file. Either regenerate only
  between waves, or tell each agent in its brief that the file drains
  concurrently and its FIRST read is authoritative.
- Writers may rewrite their output file late, after you have already merged
  an earlier version of it. That is safe: merge_agent.py's ALREADY WRITTEN
  guard skips any term that already has a body, and re-running a stale
  fragment leaves index.html byte-identical. Verified, not assumed.
- Agents will report "another process is modifying index.html" — that is the
  merge-and-commit pipeline, i.e. you. No writer ever touches index.html.
- **Measuring layout in the Browser pane: finish the animations first.**
  The pane does not always composite frames, so a CSS animation sits at
  `currentTime: 0` with `playState: "running"` forever. With
  `animation-fill-mode: both` that pins the element at its `from` keyframe.
  The term panel's slide-in starts at `translateX(28px)`, which makes it
  look like the panel hangs 28px off a 360px viewport and clips its own
  close button. It does not — that is the measurement, not the layout.
  Before reading any rect, run
  `document.querySelectorAll('*').forEach(e=>e.getAnimations&&e.getAnimations().forEach(a=>a.finish()))`.
  Cost an investigation once; nearly cost a "fix" to code that was correct.

## whitelist regeneration (after any content/dedupe change)

```python
import io, re, json
s = io.open('index.html', encoding='utf-8').read()
names = sorted(set(m.group(1) for m in re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s)))
io.open('valid_names.json','w',encoding='utf-8').write(json.dumps(names))
print(len(names))
```

## Blocked on the user — never guess

- GitHub username -> publish via README commands. Checked directly: no
  `git config --global user.name/user.email` is set and `gh` is not installed,
  so this genuinely cannot be derived from the machine. Only the user has it.
- The user's strategy rules (10am/10pm session play; TJR) -> dictated
  verbatim, one field at a time, else the library stays empty.
- ~~Strategy Lab path~~ **DONE** — path confirmed, `sync_strategies.py` written,
  run and verified. See the "Strategy Lab bridge" section of CLAUDE.md for the
  db schema, the real cost-model names, and the measured numbers. Headline:
  58,698 trials, best trials-to-kill 3,670, zero rows clear the gate, so every
  exported strategy is `untested`. That is the honest outcome, not a defect.

## Next queue

1. Decide the "Chop" duplicate (see content status).
2. GitHub publishing — blocked on the username.
3. The user's own strategy rules — blocked, and must be verbatim.

Counter-case charts are done (17 terms). If more are wanted, the obvious
remaining candidates are Stop hunt, Retest and Trendline, none of which
currently carry a chart.

## Quality baseline — measured, not assumed

Re-measure before claiming any of this changed:
- Load: 1.9 MB raw, **631 KB gzipped**; 115 ms to DOM-interactive,
  192 ms to load complete; 10,653 DOM nodes. GitHub Pages gzips, so the
  transfer figure is the one that matters. No optimisation needed.
- Accessibility: 2,401 buttons all have accessible names, 21 form fields
  all labelled, every chart SVG labelled, one h1, `lang` set, and heading
  order is continuous (the read-this-first page jumped H1→H3 until its
  headings were promoted to h2).
- Colour contrast: **zero text tokens below WCAG AA in either theme**,
  measured not assumed. Dark always passed. Light failed only on
  `--signal` at 3.54:1 — used for small text in the forward-tested badge,
  the proxy warning, the section chip and the 9.5px chart labels — and was
  darkened `#B87613 → #96600F` (5.02:1 on paper, 5.28:1 on card). If you
  touch the palette, re-measure: the light `--signal` has no headroom to
  give back.
- Both modals (term panel, strategy detail) carry role=dialog,
  aria-modal, an accessible name, a focus trap, focus restore and a body
  scroll lock. The scroll lock adds and removes in balanced pairs — the
  only two sites are the term panel and the detail overlay.
- Zero console errors on load.

### Testing note that will bite you

Group 22 boots its own dom on purpose. On the shared `d`, after ~20
groups, the term panel can be left open with a pushed history entry, and
jsdom fires `popstate` from earlier `history.back()` calls on later
ticks — which re-opens it and moves focus. Chasing that as an app bug
wastes time: it is test contamination, and the fix is isolation, not a
weaker assertion. Group 20 (Paper) does the same for the same reason.

Done and not worth redoing: responsive check at 360/768/1440 in both
colour schemes across every tab, with the strategy detail overlay open
and closed — zero horizontal overflow after fixing two bugs (the
strategies search row never wrapped, so the sort select's ~200px
intrinsic width pushed the document to 456px on a phone; and the detail
overlay needed border-box plus min-width:0, because a flex item defaults
to min-width:auto and was stretched to its widest child's min-content).
Offline holds: no external fonts, scripts or images — the only network
dependency is the Live chart embed, which has a tested offline fallback.

## Publishing

`index.html` cannot be handed to the Artifact publisher directly: the
publisher wraps whatever it is given in its own
`<!doctype html><head>…</head><body>FILE</body>` skeleton, so a complete
document ends up nested inside a body. `py -3 build_artifact.py` solves
this — it strips the doctype and `<html>` wrapper (and handles explicit
`<head>`/`<body>` too, if the source ever grows them), drops the now-inert
charset meta, keeps title/style/script/JSON-LD, and reports any external
reference that the artifact CSP would block. It exits non-zero if any
document-level tag survives. Output: `artifact_tape.html`.

Verified before publishing by wrapping the fragment exactly as the
publisher does and loading it: 995 entries, 72 charts, 5 tabs, quiz and
paper render, both modals work, zero overflow, zero console errors.

**Current artifact (this app, complete):**
https://claude.ai/code/artifact/24dc6b25-6da7-4603-9171-32356c72db13

Older URL from a previous session:
`https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016`
— updating it in place would have required `force:true`, which discards
whatever that other session published. Not done without the user asking.
To consolidate onto the old URL, confirm the overwrite is wanted first.

One CSP note: the Live chart's TradingView iframe is the single external
reference and will be blocked in an artifact. That tab already degrades
to its tested offline notice, so nothing breaks — it just cannot show a
live chart there.

Also keep C:\Users\fayaa\Downloads\index.html and test.js synced (plain copies).
