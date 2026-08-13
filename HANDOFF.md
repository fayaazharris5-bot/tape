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

Not more terms. The remaining gaps are:
- `usage` and `see` are present on everything merged, but older
  hand-written entries predate that convention — spot-check coverage.
- Second/third charts (viz2) for the priority structural terms.

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

1. Second/third charts (viz2) for the priority structural terms.
2. Decide the "Chop" duplicate (see content status).
3. Publishing — blocked on the GitHub username.

## Quality baseline — measured, not assumed

Re-measure before claiming any of this changed:
- Load: 1.9 MB raw, **631 KB gzipped**; 115 ms to DOM-interactive,
  192 ms to load complete; 10,653 DOM nodes. GitHub Pages gzips, so the
  transfer figure is the one that matters. No optimisation needed.
- Accessibility: 2,401 buttons all have accessible names, 21 form fields
  all labelled, 72 chart SVGs all labelled, one h1, `lang` set, and
  heading order is continuous (the read-this-first page jumped H1→H3
  until its headings were promoted to h2).
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

Artifact URL (pass as `url` when publishing from a new conversation):
https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016
Also keep C:\Users\fayaa\Downloads\index.html and test.js synced (plain copies).
