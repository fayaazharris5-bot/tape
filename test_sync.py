# -*- coding: utf-8 -*-
"""
Tests for sync_strategies.py — the Strategy Lab bridge.

These do NOT test the Lab's data. They build a synthetic results.db with the
same schema and pin the MAPPING RULES, so the test runs on any machine and
fails loudly if the honesty guarantees ever regress:

  1. Rule fields the engine cannot produce are ALWAYS empty. The bridge must
     never invent a bias, entry, invalidation, target or risk note.
  2. sampleSize is exactly oos_n_trades. Never rounded, never guessed.
  3. evidence is "backtested" ONLY when the full gate passes. A control-gate
     failure stays untested no matter how good the returns look — that is the
     rule most likely to be quietly relaxed later, so it gets three cases.
  4. Win rate never appears in prose without expectancy beside it.
  5. Expectancy is never labelled R. The engine produces currency.
  6. Output only uses evidence values the app's importer accepts.

Run: py -3 test_sync.py
"""
import io, json, os, sqlite3, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "sync_strategies.py")

# the evidence values index.html's EVRANK accepts on import
APP_EVIDENCE = {"untested", "backtested", "forward-tested", "live"}

COLS = [
    "id", "run_at", "strategy", "params", "asset", "timeframe", "cost_model",
    "oos_n_trades", "oos_win_rate", "oos_expectancy", "oos_profit_factor",
    "oos_payoff_ratio", "oos_max_drawdown", "oos_sharpe", "oos_dsr",
    "oos_p_value", "oos_trials_to_kill", "vs_random", "vs_buy_and_hold", "flags",
]

FAILS = []


def check(cond, msg):
    if cond:
        return True
    FAILS.append(msg)
    return False


def row(**kw):
    d = dict.fromkeys(COLS)
    d.update(kw)
    return d


def build_lab(rows):
    """Write a synthetic lab dir; return its path."""
    lab = tempfile.mkdtemp(prefix="fakelab_")
    os.makedirs(os.path.join(lab, "results"))
    db = os.path.join(lab, "results", "results.db")
    con = sqlite3.connect(db)
    con.execute("create table honest_runs (%s)" % ", ".join(COLS))
    for r in rows:
        con.execute("insert into honest_runs (%s) values (%s)"
                    % (", ".join(COLS), ", ".join("?" * len(COLS))),
                    [r[c] for c in COLS])
    con.commit()
    con.close()
    return lab


def run(lab, *extra):
    out = os.path.join(lab, "out.json")
    p = subprocess.run([sys.executable, SCRIPT, "--lab", lab, "--out", out] + list(extra),
                       capture_output=True, text=True)
    data = None
    if os.path.exists(out):
        data = json.load(io.open(out, encoding="utf-8"))
    return p, data


BASE = dict(run_at="2026-01-01T00:00:00", params="{'n': 20}", cost_model="realistic_v1",
            timeframe="1d", oos_win_rate=0.62, oos_expectancy=41.5,
            oos_profit_factor=2.1, oos_max_drawdown=-0.18, oos_sharpe=1.1,
            oos_dsr=0.2, oos_p_value=0.3, flags="")

# Four rows. Ledger will be 4, so trials_to_kill >= 4 is the survival bar.
rows = [
    # clears everything: beats random AND survives the ledger
    row(id=1, strategy="clears_gate", asset="AAA", oos_n_trades=137,
        vs_random=0.4, oos_trials_to_kill=9000, **BASE),
    # beats random but is explained by the search size
    row(id=2, strategy="beats_random_only", asset="BBB", oos_n_trades=88,
        vs_random=0.4, oos_trials_to_kill=2, **BASE),
    # loses to random but has spectacular returns — the temptation case
    row(id=3, strategy="lost_to_random", asset="CCC", oos_n_trades=250,
        vs_random=-0.9, oos_trials_to_kill=9000, **BASE),
    # engine flagged it as junk
    row(id=4, strategy="flagged", asset="DDD", oos_n_trades=31,
        vs_random=0.1, oos_trials_to_kill=5, **dict(BASE, flags="few-trades overfit? beat-random-IS-only")),
]

lab = build_lab(rows)
proc, data = run(lab, "--top", "10", "--min-trades", "30")

check(proc.returncode == 0, "script exited %d: %s" % (proc.returncode, proc.stderr[:300]))
check(data is not None, "no output file written")

if data:
    by = {s["tags"][1]: s for s in data}
    check(len(data) == 4, "expected 4 strategies, got %d" % len(data))

    # --- 3. the evidence rule, the one that matters most -------------------
    check(by["clears_gate"]["evidence"] == "backtested",
          "a row clearing the full gate should be backtested, got %r"
          % by["clears_gate"]["evidence"])
    check(by["beats_random_only"]["evidence"] == "untested",
          "beating random but dying to the trial ledger must stay untested")
    check(by["lost_to_random"]["evidence"] == "untested",
          "LOSING to the random control must stay untested regardless of returns")
    check("FAILED" in by["lost_to_random"]["results"],
          "a control-gate failure must be stated in results, not just implied")

    for name, s in by.items():
        w = "strategy %r: " % name

        # --- 1. never invent rules ----------------------------------------
        for f in ("bias", "entry", "invalidation", "target", "riskNote"):
            check(s[f] == "", w + "%s must stay empty (the engine cannot produce it)" % f)

        # --- 2. real trade count ------------------------------------------
        src = next(r for r in rows if r["strategy"] == name)
        check(s["sampleSize"] == src["oos_n_trades"],
              w + "sampleSize %r != real trade count %r" % (s["sampleSize"], src["oos_n_trades"]))

        # --- 6. app-importable evidence value ------------------------------
        check(s["evidence"] in APP_EVIDENCE, w + "evidence %r is not a value the app accepts"
              % s["evidence"])

        # --- 4/5. prose honesty --------------------------------------------
        res = s["results"]
        low = res.lower()
        if "win rate" in low:
            check("expectancy" in low, w + "win rate appears without expectancy beside it")
        check(" R " not in res and "in R" not in res,
              w + "expectancy must not be labelled R — the engine produces currency")
        check("guaranteed" not in low and "success rate" not in low,
              w + "banned claim language in results")

        # sample size must never be a suspiciously round guess
        check(s["sampleSize"] > 0, w + "sampleSize must be the real count, not 0")

    # engine flags surface rather than being dropped
    check("few trades" in by["flagged"]["results"].lower()
          or "too few" in by["flagged"]["results"].lower(),
          "engine 'few-trades' flag should be surfaced in plain words")

# --- --gate-only on a corpus where nothing clears --------------------------
# Six rows, not one. The ledger IS the row count, so a single-row corpus makes
# the bar `trials_to_kill >= 1`, which anything passes — the first draft of this
# fixture failed for that reason and the script was right.
lab2 = build_lab([row(id=i, strategy="nope%d" % i, asset="AAA", oos_n_trades=50,
                      vs_random=0.5, oos_trials_to_kill=2, **BASE)
                  for i in range(1, 7)])
proc2, data2 = run(lab2, "--gate-only")
check(proc2.returncode != 0, "--gate-only must exit non-zero when nothing clears the gate")
check(data2 is None, "--gate-only must not write a file when nothing clears")

# --- a schema change must refuse, not guess --------------------------------
lab3 = tempfile.mkdtemp(prefix="badlab_")
os.makedirs(os.path.join(lab3, "results"))
con = sqlite3.connect(os.path.join(lab3, "results", "results.db"))
con.execute("create table honest_runs (id, strategy, asset)")   # missing the gate columns
con.commit(); con.close()
proc3, _ = run(lab3)
check(proc3.returncode != 0, "a missing gate column must refuse, not silently proceed")
check("schema changed" in proc3.stdout or "refusing" in proc3.stdout,
      "refusal should say why: %r" % proc3.stdout[:200])

if FAILS:
    print("FAILED - %d problem(s):" % len(FAILS))
    for f in FAILS:
        print("  -", f)
    sys.exit(1)
print("PASSED - sync_strategies honesty invariants hold")
