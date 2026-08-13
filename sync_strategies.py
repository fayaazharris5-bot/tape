# -*- coding: utf-8 -*-
"""
Strategy Lab bridge — reads the Lab's results database and emits strategies.json
in Tape's schema.

    py -3 sync_strategies.py                     # top 20 by deflated Sharpe, brutal costs
    py -3 sync_strategies.py --top 50            # more rows
    py -3 sync_strategies.py --cost normal       # a different cost model
    py -3 sync_strategies.py --gate-only         # only rows that beat the random control
    py -3 sync_strategies.py --strategy atr_trail

MAPPING RULES (from the user's Task 11 — these matter more than the code):

  sampleSize   the real out-of-sample trade count. Never a round guess, never
               inferred, never a placeholder.

  evidence     "backtested" ONLY for out-of-sample results that also beat the
               random-walk control. A row that failed the control gate stays
               "untested" regardless of how good its returns look, and the
               failure is written into results.

  results      one plain sentence: win rate, expectancy, max drawdown, profit
               factor and the control-gate outcome.

  blank        fields the engine does not produce stay empty. The Lab records no
               entry trigger, invalidation or target, so bias/entry/invalidation/
               target/riskNote are emitted empty for the user to fill in. Nothing
               is invented to make a row look complete.

WHY THE DEFAULT IS SMALL: the database holds ~58,700 rows. Those are search
artefacts, not strategies — dumping them all into the library would flood it
with exactly the confident nonsense this project exists to avoid. The default
exports a handful, clearly labelled, and --all warns before doing more.
"""
import argparse, io, json, os, sqlite3, sys

DEFAULT_LAB = r"C:\Users\fayaa\Downloads\ai trading thing\strategy-lab"


def fmt_pct(x):
    return "—" if x is None else "%.1f%%" % (x * 100.0)


def fmt_num(x, nd=2):
    return "—" if x is None else ("%." + str(nd) + "f") % x


def val(row, key):
    v = row[key] if key in row.keys() else None
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if f != f else f          # drop NaN


def build_results_sentence(r, passed_gate):
    """One plain sentence. Only figures the engine actually produced."""
    bits = []
    wr, exp = val(r, "oos_win_rate"), val(r, "oos_expectancy")
    dd, pf = val(r, "oos_max_drawdown"), val(r, "oos_profit_factor")
    n = val(r, "oos_n_trades")

    if wr is not None and exp is not None:
        # win rate never travels alone in this project
        bits.append("win rate %s with expectancy %s per trade" % (fmt_pct(wr), fmt_num(exp, 3)))
    elif wr is not None:
        bits.append("win rate %s (expectancy not recorded)" % fmt_pct(wr))
    if pf is not None:
        bits.append("profit factor %s" % fmt_num(pf))
    if dd is not None:
        bits.append("max drawdown %s" % fmt_pct(abs(dd)))
    if n is not None:
        bits.append("over %d out-of-sample trades" % int(n))

    head = "Out-of-sample: " + ", ".join(bits) + "." if bits else "No out-of-sample metrics recorded."

    vr = val(r, "vs_random")
    if vr is None:
        gate = " Random-walk control: not recorded, so this is unverified against chance."
    elif passed_gate:
        gate = " Beat the random-walk control by %s." % fmt_num(vr, 3)
    else:
        gate = (" FAILED the random-walk control (%s) — a random entry with the same "
                "trade count and costs did as well or better, so this is kept untested "
                "regardless of its returns." % fmt_num(vr, 3))

    dsr, p = val(r, "oos_dsr"), val(r, "oos_p_value")
    extra = ""
    if dsr is not None:
        extra += " Deflated Sharpe %s." % fmt_num(dsr, 3)
    if p is not None:
        extra += " p=%s." % fmt_num(p, 4)
    return head + gate + extra


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", default=DEFAULT_LAB)
    ap.add_argument("--out", default="strategies.json")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--cost", default="brutal_v1")
    ap.add_argument("--strategy", default=None)
    ap.add_argument("--min-trades", type=int, default=30)
    ap.add_argument("--gate-only", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    db = os.path.join(a.lab, "results", "results.db")
    if not os.path.exists(db):
        print("no results.db at %s — is --lab correct?" % db); sys.exit(1)

    con = sqlite3.connect(db)
    con.row_factory = sqlite3.Row

    cols = set(r[1] for r in con.execute("pragma table_info(honest_runs)"))
    for need in ("oos_n_trades", "vs_random", "cost_model"):
        if need not in cols:
            print("results.db is missing the %s column — schema changed, refusing to guess." % need)
            sys.exit(1)

    where, args = ["oos_n_trades >= ?"], [a.min_trades]
    if a.cost and "cost_model" in cols:
        where.append("cost_model = ?"); args.append(a.cost)
    if a.strategy:
        where.append("strategy = ?"); args.append(a.strategy)
    if a.gate_only:
        where.append("vs_random > 0")

    order = "oos_dsr" if "oos_dsr" in cols else "oos_sharpe"
    sql = ("select * from honest_runs where " + " and ".join(where) +
           " order by %s desc" % order)
    if not a.all:
        sql += " limit %d" % a.top

    rows = list(con.execute(sql, args))
    if not rows:
        print("no rows matched. Try --cost normal, a lower --min-trades, or drop --gate-only.")
        print("cost models present:",
              [r[0] for r in con.execute("select distinct cost_model from honest_runs")])
        sys.exit(2)

    if a.all and len(rows) > 200:
        print("refusing to emit %d strategies — that is a search, not a library." % len(rows))
        print("Narrow it with --strategy/--gate-only, or raise --top deliberately.")
        sys.exit(3)

    out, passed = [], 0
    for r in rows:
        vr = val(r, "vs_random")
        gate_ok = vr is not None and vr > 0
        if gate_ok:
            passed += 1
        n = val(r, "oos_n_trades")
        name = "%s %s %s" % (r["strategy"], r["asset"], r["timeframe"])
        out.append({
            "name": name,
            "source": "Strategy Lab (%s, %s costs) — run %s" % (
                os.path.basename(a.lab), r["cost_model"] if "cost_model" in r.keys() else a.cost,
                r["run_at"]),
            "market": r["asset"],
            "timeframe": r["timeframe"],
            "session": "",
            # The engine records no human-readable rules. These stay empty on purpose.
            "bias": "",
            "entry": "",
            "invalidation": "",
            "target": "",
            "riskNote": "",
            "tags": ["strategy-lab", r["strategy"]] + (["gate-passed"] if gate_ok else ["gate-failed"]),
            "evidence": "backtested" if gate_ok else "untested",
            "sampleSize": int(n) if n is not None else 0,
            "results": build_results_sentence(r, gate_ok),
            "notes": ("Imported from the Strategy Lab. Parameters: %s. The engine records "
                      "no entry trigger, invalidation or target, so those fields are blank "
                      "rather than filled with plausible text — write them yourself from the "
                      "strategy definition before trading anything." % r["params"]),
            "trades": [],
            "provenance": "file",
        })

    io.open(a.out, "w", encoding="utf-8").write(json.dumps(out, indent=1))
    print("wrote %s: %d strategies (%d beat the random control, %d did not)"
          % (a.out, len(out), passed, len(out) - passed))
    if passed == 0:
        print("None cleared the control gate — every row is marked untested, which is the "
              "honest outcome and matches the Lab's standing finding.")


if __name__ == "__main__":
    main()
