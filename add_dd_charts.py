# -*- coding: utf-8 -*-
"""Add equity charts to the four drawdown-mechanics terms in `prop`.

These are the most consequential rules in the section and the ones prose
teaches worst: the difference between a static, trailing, locked and intraday
floor IS a picture. Every floor series below is computed, not sketched —
floor[i] = high_water[i] - 2.5 on a 50k account — so the chart is the same
arithmetic the Funded tab runs, drawn.

The first two terms share ONE equity series on purpose: identical trading,
only the floor rule differs, so the pair reads as a controlled comparison.

Idempotent; refuses if any target already has a chart. EXPECT_CHARTS 114->118.

    py -3 add_dd_charts.py
"""
import io, re, sys

SRC = 'index.html'

# shared equity series for the static/trailing pair (units: account thousands)
EQ = [50, 51.2, 50.6, 52, 53.5, 53, 54.8, 56, 55, 54.2, 53.8, 55.2]
HW = []
for v in EQ:
    HW.append(max(HW[-1], v) if HW else v)
TRAIL = [round(h - 2.5, 1) for h in HW]        # ratchets up, never down
STATIC = [47.5] * len(EQ)                      # never moves

# the lock: same shape, equity that climbs well past start+buffer
EQ3 = [50, 51, 52.5, 52, 53.8, 55, 54.5, 56.5, 58, 57, 58.5, 60]
HW3 = []
for v in EQ3:
    HW3.append(max(HW3[-1], v) if HW3 else v)
UNLOCKED = [round(h - 2.5, 1) for h in HW3]
LOCKED = [min(f, 50.0) if f > 50.0 else f for f in UNLOCKED]
LOCKED = [f if f < 50.0 else 50.0 for f in UNLOCKED]

# intraday vs end-of-day: closes, the unbanked spike path, and both floors
BAL = [50, 51, 52, 53, 55, 55, 54.5, 54, 54.5, 55]
PEAK = [50, 51.5, 52.5, 53.5, 58, 55.5, 55, 54.5, 55, 55.3]
HWB, HWP = [], []
for v in BAL:
    HWB.append(max(HWB[-1], v) if HWB else v)
for v in PEAK:
    HWP.append(max(HWP[-1], v) if HWP else v)
EOD_FLOOR = [round(h - 2.5, 1) for h in HWB]
INTRA_FLOOR = [round(h - 2.5, 1) for h in HWP]


def js(nums):
    return '[' + ','.join(('%g' % n) for n in nums) + ']'


CHARTS = {
 "Trailing drawdown": (
   '{k:"e",base:50,s:['
   '{v:%s,c:"a",t:"equity"},'
   '{v:%s,c:"d",dash:true,t:"floor",below:true}],'
   'mk:[{i:7,p:56,t:"high-water"}]}' % (js(EQ), js(TRAIL)),
   "The floor is always high-water minus 2.5. Every new high drags it up and "
   "nothing brings it down: this account is 5.2 in profit yet has 1.7 of room, "
   "not the 7.7 the headline drawdown suggests."),

 "Static drawdown": (
   '{k:"e",base:50,s:['
   '{v:%s,c:"a",t:"equity"},'
   '{v:%s,c:"d",dash:true,t:"floor",below:true}]}' % (js(EQ), js(STATIC)),
   "The same trading as the trailing chart, under a static rule. The floor "
   "stays at 47.5 for the life of the account, so profit genuinely widens the "
   "gap — 7.7 of room at the close instead of 1.7."),

 "Drawdown lock": (
   '{k:"e",base:50,s:['
   '{v:%s,c:"a",t:"equity"},'
   '{v:%s,c:"g",dash:true,t:"if it never locked"},'
   '{v:%s,c:"d",dash:true,t:"locked floor",below:true}],'
   'mk:[{i:2,p:50,t:"locks at breakeven",below:true}]}'
   % (js(EQ3), js(UNLOCKED), js(LOCKED)),
   "Both floors trail identically until they reach the starting balance. The "
   "locked one stops there — the account can no longer fail while in profit "
   "overall. The unlocked one keeps tightening forever: by the last bar it "
   "sits at 57.5 under an account at 60."),

 "Intraday vs end-of-day drawdown": (
   '{k:"e",base:50,s:['
   '{v:%s,c:"g",dash:true},'
   '{v:%s,c:"a",t:"balance",below:true},'
   '{v:%s,c:"d",dash:true,t:"intraday floor"},'
   '{v:%s,c:"u",dash:true,t:"EOD floor",below:true}],'
   'mk:[{i:4,p:58,t:"touched 58, never banked"}]}'
   % (js(PEAK), js(BAL), js(INTRA_FLOOR), js(EOD_FLOOR)),
   "One open position ran to 58 and came back unbanked. An end-of-day floor "
   "never saw it: 52.5, leaving 2.5 of room. An intraday floor followed it up "
   "to 55.5 — above the closing balance of 55, so this account is already "
   "breached while its statement shows a 5.0 profit."),
}


def esc(x):
    return x.replace('\\', '\\\\').replace('"', '\\"')


def main():
    s = io.open(SRC, encoding='utf-8').read()
    for name, (viz, cap) in CHARTS.items():
        pat = re.compile(r'\{t:"' + re.escape(name) + r'",c:"prop"[^{}]*')
        m = pat.search(s)
        if not m:
            print('REFUSING: cannot find the %r term object' % name)
            return 1
        if ',v:{' in m.group(0):
            print('already charted: %s — nothing to do' % name)
            continue
        insert = ',v:' + viz + ',cap:"' + esc(cap) + '"'
        s = s[:m.end()] + insert + s[m.end():]
        print('charted: %s' % name)
    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('NOTE: EXPECT_CHARTS moves by the number charted — comment it.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
