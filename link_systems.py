# -*- coding: utf-8 -*-
"""Give the newly-added terms inbound links.

The app navigates by cross-reference: every term panel shows Related
chips. A term nothing links TO is reachable only by search or by
scrolling its section, which is how all 12 named-systems entries and the
VWAP/value terms shipped — an omission from adding them, not a design
choice.

Each pair below is a link that should have existed anyway: the general
term pointing at the specific named instance of it.

Appends to an existing rel array, or adds one after `e:` when absent.
Idempotent. Never removes an existing link.

    py -3 link_systems.py
"""
import io, re, sys

SRC = 'index.html'

# owner term -> targets to add to its rel
LINKS = {
 "RSI":                      ["Connors RSI-2"],
 "Mean reversion":           ["Connors RSI-2", "Pairs trading"],
 "Momentum factor":          ["Dual momentum"],
 "Cross-sectional momentum": ["Dual momentum"],
 "Trend following":          ["Turtle system", "Dual momentum"],
 "Donchian Channel":         ["Turtle system"],
 "Breakout":                 ["Darvas box", "London breakout"],
 "Asian range":              ["London breakout"],
 "Arbitrage":                ["Statistical arbitrage", "Pairs trading"],
 "Risk parity":              ["All Weather portfolio", "Permanent portfolio"],
 "Diversification":          ["60/40 portfolio", "Permanent portfolio"],
 "Rebalancing":              ["60/40 portfolio", "Value averaging"],
 "Dollar cost averaging":    ["Value averaging"],
 "Dividend yield":           ["Dogs of the Dow"],
 "Harmonic patterns":        ["Wolfe wave", "Three-drive pattern"],
 "Elliott Wave":             ["Wolfe wave", "Orochi framework"],
 "Auction market theory":    ["Orochi framework", "TPO", "Value development"],
 "Market profile":           ["TPO", "Poor high / poor low", "Single print"],
 "Value area":               ["TPO", "Value development"],
 "Point of Control":         ["TPO", "Value development"],
 "VWAP":                     ["VWAP standard deviation bands", "Value development"],
 "Anchored VWAP":            ["VWAP standard deviation bands"],
 "Standard deviation":       ["Normal distribution", "VWAP standard deviation bands"],
 "Fat tails":                ["Normal distribution"],
 "Kurtosis":                 ["Normal distribution"],
 "Delta":                    ["Cumulative volume delta"],
 "Order flow":               ["Cumulative volume delta"],
 "Fair value gap":           ["Single print"],
 "Liquidity gap":            ["Single print"],
 "Initial balance":          ["Poor high / poor low"],
}


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def main():
    s = io.open(SRC, encoding='utf-8').read()
    known = set(m.group(1) for m in
                re.finditer(r'\{t:"((?:[^"\\]|\\.)*)",c:"[a-z0-9]+"', s))
    added = missing = 0
    for owner, targets in LINKS.items():
        i = s.find('{t:"%s",c:"' % esc(owner))
        if i < 0:
            print('owner not found:', owner); missing += 1; continue
        end = s.find('},\n', i)
        if end < 0:
            end = i + 4000
        chunk = s[i:end]
        want = [t for t in targets
                if esc(t) in known or t in known]
        want = [t for t in want if ('"%s"' % esc(t)) not in chunk]
        if not want:
            continue
        m = re.search(r'rel:\[([^\]]*)\]', chunk)
        if m:
            new_rel = 'rel:[%s,%s]' % (m.group(1),
                                       ','.join('"%s"' % esc(t) for t in want))
            chunk2 = chunk[:m.start()] + new_rel + chunk[m.end():]
        else:
            # place rel after the e:"..." value, matching the house order
            me = re.search(r',e:"(?:[^"\\]|\\.)*"', chunk)
            if not me:
                print('no e: field on', owner); missing += 1; continue
            ins = ',rel:[%s]' % ','.join('"%s"' % esc(t) for t in want)
            chunk2 = chunk[:me.end()] + ins + chunk[me.end():]
        s = s[:i] + chunk2 + s[end:]
        added += len(want)
    io.open(SRC, 'w', encoding='utf-8', newline='').write(s)
    print('inbound links added: %d | owners not found: %d' % (added, missing))
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())
