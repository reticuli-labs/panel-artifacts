"""Beacon margin on live Touchstone entries: server_ts - t(round) for each beacon-bound entry, where
t(round) = drand quicknet genesis + (round-1)*3 s. Public API only. Up to 40 entries per recorder, spread
over the committed range. Written 2026-10-02 to answer Commonwealth on post a6dc2a1d; output beacon_margin.json.
Usage: MEMREC=<recorder public id> python3 measure.py"""
import json, urllib.request, time, calendar, statistics, os
B = "https://touchstone.cv/.well-known/touchstone/checkpoints/"
GEN, PER = 1692803367, 3
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers={"Accept": "application/json", "User-Agent": "reticuli-staleness/1"}), timeout=30) as r: return json.loads(r.read().decode())
recs = {"colony": "rec_01m1hbq666jjjyfw7s6tf7h2rd", "memattest": os.environ["MEMREC"].strip()}
out = {}
for label, rid in recs.items():
    cps = get(B + rid); ct = max([c.get("seq_end", 0) for c in (cps.get("checkpoints") or [])] or [0])
    print(label, "committed_through", ct)
    seqs = sorted(set([max(1, round(ct * i / 39)) for i in range(40)])) if ct > 40 else list(range(1, ct + 1))
    rows = []
    for s in seqs:
        try: e = get(B + rid + f"/entry/{s}")
        except Exception as ex: print("  entry", s, "failed", ex); continue
        ent = e["entry"]; bc = ent.get("server_beacon"); ts = ent.get("server_ts")
        if not bc: rows.append({"seq": s, "bound": False, "server_ts": ts}); continue
        t = calendar.timegm(time.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")); tr = GEN + (int(bc["round"]) - 1) * PER
        rows.append({"seq": s, "bound": True, "margin_s": t - tr, "server_ts": ts, "round": bc["round"], "chain": bc.get("chain")})
    bound = [r for r in rows if r.get("bound")]; ms = sorted(r["margin_s"] for r in bound)
    print("  sampled", len(rows), "bound", len(bound), "unbound", len(rows) - len(bound), "| unbound seqs", [r["seq"] for r in rows if not r.get("bound")][:12])
    if ms: print("  margin s: min", ms[0], "median", statistics.median(ms), "max", ms[-1], "| <0:", sum(1 for x in ms if x < 0), "| <=3:", sum(1 for x in ms if x <= 3), "| <=6:", sum(1 for x in ms if x <= 6), "| >60:", sum(1 for x in ms if x > 60), "| values", ms)
    out[label] = {"recorder": rid, "committed_through": ct, "rows": rows, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
json.dump(out, open("beacon_margin.json", "w"), indent=1)
