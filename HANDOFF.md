# Tape — session handoff. Read fully, then continue.

Repo: `C:\Users\fayaa\Downloads\tape`. As of commit `deaddcb`:
**995 terms, ~340 with long-form bodies, 5 tabs, suite green.**

```bash
cd C:\Users\fayaa\Downloads\tape
npm i jsdom     # if node_modules missing
node test.js    # MUST print PASSED (currently 224 assertions) before any change
```

Never pipe the test run when you need its status: `node test.js > out 2>&1; echo $?`.

## Already DONE — do not redo
- Content merged: orders/positions (30), statistics (32), pa/leverage (36),
  futures/commodities/derivatives (47), options (57) — plus 125 hand-written.
- Modules spliced AND wired: `module_first.html` (Read-this-first page),
  `module_path.html` (Start-here path; panel opener exported as
  `TAPE_NS.openTerm`), `module_paper.html` (Paper tab; router's setTab knows
  "paper" and tolerates module-created tabs). splice_module.py refuses
  duplicates via marker comments — re-running is safe but pointless.
- Paper tab passed jsdom checks (opens, hides on leave, form, honest caption,
  no credential fields — `term-tokenomics` matching id*="token" probes is the
  glossary term, not a field). STILL OWED: a real-browser click-through of a
  full paper trade (open with stop -> derived size -> mark -> close -> R
  written to a linked strategy log as {d,dir,r,n:"paper"}) — do this first.

## FIRST JOBS, in order
1. Real-browser verification of the Paper tab (serve the folder over http;
   file:// blocks scripts). Fix what you find; suite stays green.
2. Respawn the TWO writers that died at the session limit (their files never
   landed): briefs below. They write agent_cryprop.json / agent_macro.json;
   merge each with `python merge_agent.py <file>` then test then commit.
3. Wave-3 writers for remaining ~370 unwritten terms (sections: ind, ind2,
   cpat, chpat, fib, wyc, flow, exec, port, data, auto, cost, reg, au, eq,
   rates, etf, factor, perf, part, riskt, tech, money, mgmt, style, slang,
   plus leftovers in psy/risk/stat/bt). Extract exact per-section lists first
   (regenerate valid_names.json after ANY content change — snippet below).
4. SM-2 quiz upgrade, then strategy detail view — BOTH are edits to existing
   modules: do them in-session, never via agents (same-file collisions).

## Respawn brief — WRITER A (crypto + prop firms, 52 terms)
Spawn a general-purpose background agent with EXACTLY this task:
- Output ONLY C:\Users\fayaa\Downloads\tape\agent_cryprop.json ; never touch
  index.html. First read valid_names.json; every "see" name must match exactly.
- Terms (52): Spot vs perpetual | Liquidation cascade | Long squeeze / short
  squeeze | CEX vs DEX | Custody | AMM | Impermanent loss | Yield farming |
  Gas | MEV | Stablecoin | Depeg | On-chain metrics | Halving | Wash trading |
  24/7 market | Layer 1 / Layer 2 | Bridge | Staking | Liquid staking |
  Slashing | Tokenomics | Vesting / unlock | TVL | Oracle | Open interest
  (crypto) | Basis / cash-and-carry | Proof of reserves | Cold vs hot wallet |
  Seed phrase | Airdrop | Memecoin | Exchange outage | Insurance fund |
  Auto-deleveraging | Isolated vs cross margin | Perp funding arbitrage |
  Evaluation | Profit target | Trailing drawdown | Intraday vs end-of-day
  drawdown | Consistency rule | Payout split | Reset fee | Scaling plan |
  News trading restriction | Simulated funding | Copy trading a funded
  account | Consistent profitability | Evaluation expected cost | Payout
  verification | Two-step vs one-step
- Format: one JSON object {"Term":{"long","usage","see"}}; long = 3-4
  paragraphs joined by \n\n, 150-200 words, final paragraph starts exactly
  "Where people get fooled:"; usage 1-2 sentences, never advice; see = 3-5
  whitelist names. Voice: plain, direct, quietly sceptical, mechanism-first,
  British spelling.
- Bans (regex-enforced): "success rate"; "win rate of <digit>"; "<n>%
  accurate/reliable/of trades win"; % attached to this/the pattern/setup/
  signal; the words "undefined" and "NaN"; "will go/reverse/continue";
  "guaranteed returns/profits/income/wins". No invented statistics —
  including prop-firm pass rates (qualitative only; expected cost = fee ×
  attempts as arithmetic the reader does). Citable documented facts: FTX
  collapse 2022 (custody), bridges as major exploit vector, ADL closing
  profitable positions on some venues, funding as periodic peer-to-peer
  payments keeping perps near spot, seed phrase = every request for it is
  theft. Prop entries state the business model plainly: fees are revenue
  whether or not anyone passes; trailing-from-unrealised-peak drawdowns turn
  open profit into a raised floor; consistency rules select against lumpy
  but genuine strategies. Verify JSON parses + zero whitelist misses before
  writing; report counts.

## Respawn brief — WRITER B (macro + econ + cycles, 49 terms)
Same rules, output ONLY agent_macro.json.
- Terms (49): Market cap | EPS / P/E | Earnings | FOMC | CPI | NFP | Hawkish
  / dovish | Risk-on / risk-off | Pre-FOMC drift | Economic calendar |
  Central bank speak | Flight to quality | Liquidity conditions | Positioning
  | Priced in | Event risk | PPI / PCE | GDP | Yield curve | DXY | Quad
  witching | Dot plot | Seasonality | Core vs headline | Unemployment rate |
  Participation rate | Jobless claims | ISM / PMI | Retail sales | Consumer
  confidence | Housing starts | Leading indicator | Revisions | Consensus /
  expected | Whisper number | Data-day volatility | Business cycle |
  Recession | Soft landing | Stagflation | Credit cycle | Volatility regime |
  Bull market | Bear market | Bear market rally | Melt-up risk | Rotation |
  Sector | Structural break
- Extra accuracy: markets price the SURPRISE vs consensus, not the level;
  core strips food/energy; PCE is the Fed's preferred gauge; dot plot moves
  markets because the decision is priced; curve inversion precedes recessions
  with long variable lags (context not timer); seasonality mostly rests on
  small samples of non-independent years — say so; Pre-FOMC drift = published
  academic finding (Lucca & Moench, NY Fed), post-publication strength
  disputed, no numbers beyond attribution; recessions dated retrospectively;
  bear-market rallies are the sharpest. Perth/AWST timing notes welcome (US
  data lands late evening/night AWST).

## Settled policy — do not relitigate
- Ban the CLAIM, not the word (user-confirmed): filters target numeric
  win-rate claims, "guaranteed returns", pattern-attributed percentages —
  never criticism, worked arithmetic, or correct mechanics. If a filter
  rejects honest content, narrow the filter and say so in the commit.
- English "undefined"/"NaN" in prose: reword the prose, keep the guard.
- Strategy library EMPTY BY DESIGN (provenance guard, test group 18). Rules
  enter only dictated by the user or from a named file. Never attribute
  rules to TJR/ICT/anyone.
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

## Publishing
Artifact URL (pass as `url` when publishing from a new conversation):
https://claude.ai/code/artifact/cfa1078d-9ac2-4163-9abd-5b2cc5a1b016
Also keep C:\Users\fayaa\Downloads\index.html and test.js synced (plain copies).
