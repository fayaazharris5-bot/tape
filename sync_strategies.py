# -*- coding: utf-8 -*-
"""
Strategy Lab bridge — reads the Lab's results database and emits strategies.json
in Tape's schema.

    py -3 sync_strategies.py                     # top 20, realistic costs
    py -3 sync_strategies.py --top 50
    py -3 sync_strategies.py --cost flat_legacy
    py -3 sync_strategies.py --gate-only         # only rows that clear the FULL gate
    py -3 sync_strategies.py --strategy momentum_hold

MAPPING RULES (from the user's Task 11 — these matter more than the code):

  sampleSize   the real out-of-sample trade count, straight from oos_n_trades.
               Never a round guess, never inferred, never a placeholder.

  evidence     "backtested" only for an out-of-sample result that clears the
               FULL control gate (see below). Anything else is "untested",
               however good its returns look, and the reason goes in results.

  results      one plain sentence: win rate (never alone), expectancy, max
               drawdown, profit factor, and the control-gate outcome.

  blank        fields the engine does not produce stay empty. The Lab records no
               entry trigger, invalidation or target, so bias/entry/invalidation/
               target/riskNote are emitted empty for the user to fill in. Nothing
               is invented to make a row look complete.

WHAT "CLEARING THE GATE" MEANS HERE, and why it is not a number I picked:

  The Lab already computes `oos_trials_to_kill` — how many independent trials it
  would take for a result this good to show up by chance. The Lab also keeps a
  permanent trial ledger. A result is only meaningful if it survives the ledger
  it was found in, so the bar is `oos_trials_to_kill >= <rows in honest_runs>`.
  Both halves come from the Lab; neither is a threshold invented here.

  As of writing: ledger 58,698, best trials_to_kill 968, best deflated Sharpe
  0.18. Nothing clears it. Every row therefore exports as "untested", which is
  the correct answer and matches the Lab's standing finding, not a bug.

EXPECTANCY IS IN CURRENCY, NOT R. The brief asked for expectancy in R; the
engine does not produce R, so this prints the engine's own per-trade figure and
labels it as such rather than relabelling dollars as R.

WHY THE DEFAULT IS SMALL: the database holds ~58,700 rows. Those are search
artefacts, not strategies — dumping them into the library would flood it with
exactly the confident nonsense this project exists to avoid.
"""
import argparse, io, json, os, sqlite3, sys

DEFAULT_LAB = r"C:\Users\fayaa\Downloads\ai trading thing\strategy-lab"


def fmt_pct(x):
    return "-" if x is None else "%.1f%%" % (x * 100.0)


def fmt_num(x, nd=2):
    return "-" if x is None else ("%." + str(nd) + "f") % x


def val(row, key):
    v = row[key] if key in row.keys() else None
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f          # drop NaN


def build_results_sentence(r, gate_ok, ledger):
    """Plain sentences. Only figures the engine actually produced."""
    bits = []
    wr, exp = val(r, "oos_win_rate"), val(r, "oos_expectancy")
    dd, pf = val(r, "oos_max_drawdown"), val(r, "oos_profit_factor")
    n = val(r, "oos_n_trades")

    if wr is not None and exp is not None:
        # win rate never travels alone in this project
        bits.append("win rate %s with expectancy %s per trade in account currency "
                    "(the engine does not produce R)" % (fmt_pct(wr), fmt_num(exp)))
    elif wr is not None:
        bits.append("win rate %s, expectancy not recorded" % fmt_pct(wr))
    elif exp is not None:
        bits.append("expectancy %s per trade in account currency" % fmt_num(exp))
    if pf is not None:
        bits.append("profit factor %s" % fmt_num(pf))
    if dd is not None:
        bits.append("max drawdown %s" % fmt_pct(abs(dd)))
    if n is not None:
        bits.append("over %d out-of-sample trades" % int(n))

    out = ("Out-of-sample: " + ", ".join(bits) + ".") if bits else \
          "No out-of-sample metrics recorded."

    vr, ttk = val(r, "vs_random"), val(r, "oos_trials_to_kill")
    if vr is None:
        out += " Random-walk control not recorded, so this is unverified against chance."
    elif vr <= 0:
        out += (" FAILED the random-walk control (%s): a random entry with the same trade "
                "count and costs did as well or better." % fmt_num(vr, 3))
    elif ttk is not None and ttk < ledger:
        out += (" Beat the random-walk control by %s, but it would take only about %d trials "
                "for a result this good to appear by chance, and this search has run %d. "
                "That is a fail, not a pass." % (fmt_num(vr, 3), int(ttk), ledger))
    elif gate_ok:
        out += (" Beat the random-walk control by %s and survives the %d-trial ledger "
                "(needs ~%d trials to explain by chance)." % (fmt_num(vr, 3), ledger, int(ttk)))
    else:
        out += (" Beat the random-walk control by %s, but trials-to-kill was not recorded, "
                "so it cannot be checked against the %d-trial ledger." % (fmt_num(vr, 3), ledger))

    dsr, p = val(r, "oos_dsr"), val(r, "oos_p_value")
    if dsr is not None:
        out += " Deflated Sharpe %s." % fmt_num(dsr, 3)
    if p is not None:
        out += " p=%s (uncorrected)." % fmt_num(p, 3)

    # the engine's own red flags, spelled out rather than left as jargon
    fl = (r["flags"] if "flags" in r.keys() else "") or ""
    notes = []
    if "few-trades" in fl:
        notes.append("the engine flagged it as too few trades to read")
    if "beat-random-IS-only" in fl:
        notes.append("it beat random in-sample only")
    if "overfit" in fl:
        notes.append("the engine flagged it as possibly overfit")
    if notes:
        out += " Engine flags: " + "; ".join(notes) + "."
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", default=DEFAULT_LAB)
    ap.add_argument("--out", default="strategies.json")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--cost", default="realistic_v1")
    ap.add_argument("--strategy", default=None)
    ap.add_argument("--min-trades", type=int, default=30)
    ap.add_argument("--gate-only", action="store_true")
    a = ap.parse_args()

    db = os.path.join(a.lab, "results", "results.db")
    if not os.path.exists(db):
        print("no results.db at %s - is --lab correct?" % db); sys.exit(1)

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    cols = set(r[1] for r in con.execute("pragma table_info(honest_runs)"))
    for need in ("oos_n_trades", "vs_random", "cost_model", "oos_trials_to_kill"):
        if need not in cols:
            print("results.db has no %s column - schema changed, refusing to guess." % need)
            sys.exit(1)

    # the ledger the significance bar scales with
    ledger = con.execute("select count(*) from honest_runs").fetchone()[0]

    where, args = ["oos_n_trades >= ?", "cost_model = ?"], [a.min_trades, a.cost]
    if a.strategy:
        where.append("strategy = ?"); args.append(a.strategy)
    if a.gate_only:
        where.append("vs_random > 0"); where.append("oos_trials_to_kill >= %d" % ledger)

    # one row per strategy/asset/timeframe - the table holds many near-identical
    # re-runs of the same variant and they would otherwise fill the library
    sql = ("select * from honest_runs where " + " and ".join(where) +
           " group by strategy, asset, timeframe"
           " having oos_trials_to_kill = max(oos_trials_to_kill)"
           " order by oos_trials_to_kill desc, oos_dsr desc limit %d" % a.top)

    rows = list(con.execute(sql, args))
    if not rows:
        print("no rows matched.")
        print("cost models present:",
              [r[0] for r in con.execute("select distinct cost_model from honest_runs")])
        if a.gate_only:
            best = con.execute("select max(oos_trials_to_kill) from honest_runs").fetchone()[0]
            print("nothing clears the full gate: best trials-to-kill is %s against a "
                  "%d-trial ledger. That is the honest result." % (best, ledger))
        sys.exit(2)

    out, passed = [], 0
    for r in rows:
        vr, ttk = val(r, "vs_random"), val(r, "oos_trials_to_kill")
        gate_ok = (vr is not None and vr > 0 and ttk is not None and ttk >= ledger)
        if gate_ok:
            passed += 1
        n = val(r, "oos_n_trades")
        out.append({
            "name": "%s - %s %s" % (r["strategy"], r["asset"], r["timeframe"]),
            "source": "Strategy Lab %s costs, run %s" % (r["cost_model"], r["run_at"]),
            "market": r["asset"],
            "timeframe": r["timeframe"],
            "session": "",
            # The engine records no human-readable rules. These stay empty on purpose.
            "bias": "",
            "entry": "",
            "invalidation": "",
            "target": "",
            "riskNote": "",
            "tags": ["strategy-lab", r["strategy"]] +
                    (["gate-passed"] if gate_ok else ["gate-failed"]),
            "evidence": "backtested" if gate_ok else "untested",
            "sampleSize": int(n) if n is not None else 0,
            "results": build_results_sentence(r, gate_ok, ledger),
            "notes": ("Imported from the Strategy Lab, which had run %d trials at export. "
                      "Parameters: %s. The engine records no entry trigger, invalidation or "
                      "target, so those fields are blank rather than filled with plausible "
                      "text - write them yourself from the strategy definition."
                      % (ledger, r["params"])),
            "trades": [],
            "provenance": "file",
        })

    io.open(a.out, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print("wrote %s: %d strategies (%d cleared the full gate, %d did not) against a "
          "%d-trial ledger" % (a.out, len(out), passed, len(out) - passed, ledger))
    if passed == 0:
        print("None cleared the gate, so every row is marked untested. That is the honest "
              "outcome and matches the Lab's standing finding - not a failure of this script.")


if __name__ == "__main__":
    main()
