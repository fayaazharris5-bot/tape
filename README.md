# Tape

Reading the tape. A single self-contained `index.html` — a trading glossary,
strategy journal, quiz and live chart. No build step, no dependencies, no
server. Open the file and it works.

## Run the tests

```
npm i jsdom
py -3 check.py
```

`check.py` runs every gate — the test suite plus the claims, coverage,
contrast and sync-bridge audits — and exits non-zero if any fail. Use it
instead of running them piecemeal; a skipped gate is how a regression ships.
`--quick` skips the slow suite.

Currently **320 assertions**, 0 failing. Re-run after every change.

## The config block

Near the bottom of `index.html`, the `TAPE` object drives every commercial and
branding surface. **Every string is empty by default, and an empty string means
the feature is completely hidden** — the app looks and behaves exactly as it
does with no config at all.

```js
var TAPE = {
  name:       "Tape",   // app name
  wordmark:   "TAPE",   // stamped on every exported image
  url:        "",       // shown on exported images, e.g. "tape.example.com"
  accent:     "",       // hex colour, overrides --signal
  supportUrl: "",       // footer link; hidden while empty
  workbookUrl:"",       // printable workbook link; hidden while empty
  sections:   null,     // null = all sections, or ["basics","risk"]
  footer:     ""        // extra footer line; hidden while empty
};
```

### Custom build

To produce a branded version for someone else, edit those eight lines. Set
`name` and `wordmark`, point `url` at their domain, set `accent` to their
colour, and restrict `sections` if they only want part of the glossary. Nothing
else needs touching.

## Image export

Every chart carries Square / Portrait / Landscape export buttons. Rendering is
client-side: the SVG is serialised, its CSS custom properties are substituted
for computed values (without this step the export comes out black), drawn to a
canvas, and returned as a PNG blob. No library, no network.

Exported images carry the wordmark and `TAPE.url`. That is deliberate — it is
the only distribution mechanism that survives someone copying the HTML file.

## Publishing to GitHub Pages

First create an empty repo named `tape` under the account — no README, no
`.gitignore`, no licence, or the first push will be rejected as a
non-fast-forward: <https://github.com/new>

Then:

```bash
git remote add origin https://github.com/fayaazharris5-bot/tape.git
git branch -M main
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: `main` / root**.

Live at <https://fayaazharris5-bot.github.io/tape/> within a minute or two.

The whole app is one file, so Pages needs no build step and no workflow.
Every later update is `git push`; Pages redeploys on its own.

## What this app does not do

No accounts, no server, no database. It never stores an API key, broker
credential or account number. It places no orders, mirrors no trades, and makes
no prediction or probability claim about any setup. Simulation and
record-keeping only.
