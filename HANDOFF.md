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

**Run `py -3 check.py`** — one command, every gate, non-zero if any fail.
`--quick` skips the 24s suite. Use it instead of running the audits
piecemeal; a skipped gate is how a regression ships.

The individual audits, all exiting non-zero on a finding:

- `py -3 audit_claims.py` — re-checks every body actually spliced into
  index.html: the ban regexes, and that each closes with the
  "Where people get fooled:" paragraph. Currently 994 bodies, 0 hits.
- `py -3 audit_coverage.py` — field coverage. Currently 0 bodies missing
  `usage`, 0 missing `see`, 0 terms missing an example, 48 sections.
- `py -3 audit_links.py` — cross-reference integrity. `merge_agent.py`
  only validates `see` links on bodies it merges, so `rel` on term
  objects and any hand-written `see` had never been checked: 13 were
  dead, rendering chips that went nowhere ("Costs", "Turtle",
  "Markowitz", "Red flags" — names that never existed or were retired).
  All repaired; two of them by terms the named-systems section added.
  Also reports orphans (terms nothing links to) as information, not a
  failure — some legitimately have no inbound reference.
- `py -3 audit_contrast.py` — WCAG AA on every text token, in all four
  theme contexts (light base, light explicit, dark media, dark explicit).
  Currently 0 pairs below AA. It resolves the cascade rather than reading
  every block, because the stylesheet deliberately overrides an early
  `:root` with a later visual-pass one — auditing all blocks would flag
  values that never apply. It also refuses to report at all if a light and
  a dark context resolve to the same `--paper`, since that means the
  cascade was mis-read. Verified in both directions: injecting a low
  contrast colour into the *winning* block exits 1 and names the failing
  pairs; the same colour in an overridden block correctly changes nothing.

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

## Strategy templates — structure, never rules

Ten quick-add templates on the Strategies tab. Each prefills **structure**
(timeframe, tags, sizing convention) and leaves every rule field empty,
with a **placeholder prompting what that rule must answer to be testable**
— which timeframe, which close, what single fact would disprove it.
Placeholders are never stored; only typed text is.

Do not be tempted to "improve" these by filling in the rules. That is
exactly what got eleven seeded strategies deleted in `00cc3c0`, and test
group 18 plus group 22b both fail if it happens again. A template that
contains rules is a strategy the user did not write, filed in their
library under their name.

A **testability hint** sits under the rule fields. It applies the standard
the corpus argues throughout — a rule that cannot fail cannot be validated
— by flagging vague wording by name ("strong", "confirmation"), flagging a
rule with no price/number/bar event to test against, and confirming when
one reads as checkable. It judges WORDING only, never the idea or the
direction, and it warns without ever blocking a save.

## Paper log CSV export

The Paper tab exports closed trades in exactly the dialect the Strategies
importer reads, so a record round-trips without a converter.

`PnL_Gross` is gross **on purpose**: the importer's contract is that a P&L
column is gross and a commission column is deducted from it. The first
version exported the net figure beside a Commission column, so re-import
subtracted costs twice and $151.04 came back as $146.08. Spread is already
inside the fill prices and its column name deliberately does not match the
importer's fee hints. Group 21b asserts the round trip is exact — if you
change either side of this, that test is the one that will catch you.

Cells are also hardened against **spreadsheet formula injection**: a value
starting with `= + - @` tab or CR is prefixed with an apostrophe, because
instrument and strategy names are free text and a strategy name can arrive
from someone else's shared library link. Genuine numbers are explicitly
excluded from that rule — prefixing a negative P&L would export it as text
and break the round trip. Both properties are asserted together, so a fix
to one that breaks the other fails the suite.

## Named systems & frameworks (section `sys`)

Fifteen entries for systems that come with a name attached: Orochi, the
Turtle system, Connors RSI-2, Darvas box, dual momentum, pairs trading,
statistical arbitrage, 60/40, the permanent portfolio, All Weather, value
averaging, Dogs of the Dow, the London breakout, the Wolfe wave and the
three-drive pattern. Added by `add_systems.py` and `add_systems2.py`,
both idempotent.

**This is where "add the strategies you find online" goes — never the
library.** Rule 3 and test group 18 both forbid the library. A named
system is described here the way Wyckoff and the ICT vocabulary already
are: named, dated, credited to a documented originator, with what is and
is not established stated plainly. They are descriptions, never rule sets.

Every claim was researched, not recalled. Orochi in particular is written
from this project's own record — its five components, four needing tick
data, and the fifth (VWAP reversion) tested as PR-007 in the companion
engine and refused by the hard gate once an independent bootstrap was
corrected to a block bootstrap and the effective sample fell to about
three. Its no-alpha-decay marketing is named as unfalsifiable, not repeated.

`regen_whitelist.py` replaces the old copy-paste snippet — run it after
any content change, since writer briefs validate see-links against it.

## Publishing the artifact: the downloads capability

The artifact sandbox blocks page-initiated saves, so the paper CSV export
is dead in the published viewer unless the `downloads` capability is
declared — pass `capabilities: {downloads: true}` when publishing, or the
publish response warns and the button silently does nothing.

The export uses the capability when `window.claude.use` is present and the
anchor download otherwise, and exactly one must fire. `csv` is in the
viewer's extended type set and can be refused, so a refusal retries once
as `.txt`. A declined save says so rather than claiming success.

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

Verified end to end in a real browser, not just at the parser: a real
`File` through the actual file input renders a report with net $910 from
a four-fill ccxt log (a long round trip at +470 and a short at +440),
disclosing that trades were reconstructed FIFO oldest-first, that
positions still open at the end of the file are skipped, and that nothing
was uploaded — with the win rate shown beside expectancy and a
small-sample warning, as the honesty rules require.

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
- **`alt` was dead in search until 2026-08-15.** The grid haystack was
  built from `t + d + e` only, so all 29 terms carrying an `alt` were
  unfindable by their synonym — and the claim elsewhere in this file that
  names retired in the dedupe passes "remain searchable via alt text on
  their keepers" was simply false: "multiple comparisons", "killzone",
  "order book depth" and "power of three" all returned nothing. The
  haystack now includes `alt` and five assertions in group 3 hold it
  there. If you retire a name, put it in `alt` AND check it searches.
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

Counter-case charts are done (17 terms). The three candidates this note used
to name — Stop hunt, Retest and Trendline — **all now carry both a chart and a
viz2 counter-case**; verified 2026-08-14, so don't re-add them. 86 terms have a
chart, 22 carry a viz2. There is no remaining chart backlog.

`sync_strategies.py` (the Strategy Lab bridge) is now a gate: `test_sync.py`
pins its honesty invariants and `check.py` runs it. The test builds its own
synthetic results.db, so it passes with no Lab on the machine. It was
mutation-tested, not just run — forcing the control gate open and injecting a
fabricated entry rule each turn it red. What it pins: rule fields the engine
cannot produce stay empty, sampleSize is exactly oos_n_trades, evidence is
never "backtested" without clearing the full gate (three separate cases,
including the tempting one — spectacular returns that LOST to the random
control), win rate never appears without expectancy, expectancy is never
relabelled R, and a schema change refuses rather than guesses.

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
