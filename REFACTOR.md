# Task 2 — Consolidation. Handoff.

Read this file, then do the work. Everything needed is here; nothing needs
re-deriving from the chat history.

## Start here

```bash
cd C:\Users\fayaa\Downloads\tape
npm i jsdom
node test.js
```

Must print **PASSED — 223 assertions passed, 0 failed**. If it does not, stop
and say so — the file is already broken and everything after is guesswork.

Revert point if the refactor goes wrong:

```bash
git reset --hard 00cc3c0
```

## The rule that governs this task

**Behaviour-identical.** The 223 assertions pass before and after, with **no
assertion edited, weakened, skipped or removed at any point.** If a test fails
during the refactor, the refactor broke something — fix the code, never the
test. If an assertion looks genuinely wrong, stop and show it to the user
rather than changing it.

Net line count must go **down**. If the file grew, the refactor did not do its
job — explain why before committing.

One commit, no features bundled in.

## Baseline as of 00cc3c0

| | |
|---|---|
| Size | 545 KB, 5,687 lines |
| `<script>` blocks | 29 |
| `<style>` blocks | 18 |
| Duplicate helpers | `esc` ×7, `slug` ×6, `el(` ×5, `slugify` ×3, plus `lrEsc`, `lrSlug`, `lrEl` |
| Defensive guards | 14 × `typeof window/document !==` |
| Assertions | 223 passing |

## Target structure

One `<style>`. Script blocks in exactly this order:

1. **CONFIG** — every tunable constant, documented, at the top (`TAPE` object lives here)
2. **DATA** — `CAT`, `D`, `TAPE_SEED` (currently empty on purpose — see below)
3. **ENGINE** — `candleSvg` / `equitySvg` / `svgFor` and nothing else
4. **UTIL** — ONE `esc`, ONE `slug`, ONE `el`, ONE `$`, the storage wrapper, share encode/decode, date and timezone helpers
5. **STATE** — the stores, with every `localStorage` access behind the single wrapper from UTIL
6. **MODULES** — one IIFE per tab: terms, strategies, quiz, live, export/post-builder, walkthroughs, panel, import
7. **BOOT** — routing, tab wiring, first render

Modules stay IIFEs but share UTIL and STATE through **one explicit namespace
object**, not by reaching for globals and hoping.

## Traps that have already cost time — read before starting

**1. Test group 2 evaluates "data" script blocks in a bare context.**
It collects every `<script>` that does not contain the string
`document.getElementById` and runs them through `new Function` to rebuild `D`.
That context has no `window` and no `document`. This is why the 14 defensive
guards exist. Once CONFIG/DATA/ENGINE are separated from anything touching the
DOM, the guards become unnecessary — but check group 2 still finds `D`, because
the block-selection heuristic is fragile. If it breaks, fix the module split so
data blocks are genuinely data-only; do not edit the test.

**2. Appended modules cannot see each other's scope.**
This is the whole reason for the refactor. `esc`, `slug`, `$`, `openForm` and
`window.D` were each unreachable from a later block at some point, and each
failure surfaced only at runtime. Fixing scope is the point of the task.

**3. Do not use bash heredocs for anything containing regex escapes.**
`<<'PY'` has mangled `\d`, `\b` and `\\` repeatedly. Write Python or JS to a
file with the Write tool and run the file.

**4. The panel rewrites its own innerHTML.**
`#tpanel` content is replaced on every term. A MutationObserver re-attaches the
walkthrough. Preserve that or walkthroughs silently stop mounting.

**5. `svgFor` must stay global.**
Several modules call `window.svgFor`. There is exactly one chart engine and the
brief forbids a second — keep it in ENGINE and expose it once.

## Verify — all four, report each

1. `node test.js` → 223 passing, 0 failing. Paste the raw tail.
2. `git diff --stat` → must be **net negative**.
3. Open in a real browser. Click every tab and every panel: Terms, Strategies,
   Quiz, Live chart. Open a term panel, step a walkthrough, run a CSV import,
   export a PNG, toggle Simple/Detailed, open the section drawer.
4. Confirm it still works opened directly from the filesystem with no network.

Report size, block counts and duplicate-helper counts before vs after, plus a
list of dead code and unused CSS removed.

## Do not

- Do not add features. Not one.
- Do not restyle. This is deduplication; the rendered design must not change.
  Screenshot before and after and compare.
- Do not write a second chart engine, add a framework, a bundler or a build step.
- Do not put anything in `TAPE_SEED`. It is empty deliberately: eleven
  strategies were removed because their rules were written from recall and then
  given citations, which made recalled text look sourced. Rules enter that array
  only if the user dictates them or points at a file. Test group 18 enforces this.

## After this

Stop and wait. The user is handing out tasks one at a time from here.
