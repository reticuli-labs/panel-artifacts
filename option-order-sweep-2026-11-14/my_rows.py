"""Tabulate the order sweep for every reader-panel measurement of MINE: the 35 on banks of the October cache and the 22 filed
on banks outside it. Reads order_sweep.json (argument 1), the October scan result (argument 2) and my newer measurements
(argument 3); writes my_rows_sweep.json (argument 4). No network. Run with python3 -I."""
import collections, json, sys
R = json.load(open(sys.argv[1])); S = json.load(open(sys.argv[2])); new = json.load(open(sys.argv[3]))
banks = dict(R["banks"]); banks.update({e["bank_id"]: e for e in R["extra"]})
fresh = {r["manifest_hash"]: r for r in new}   # a row read today wins over the October scan's row for the same measurement
mine = [(m["manifest_hash"], m.get("bank_id"), "cache", m.get("retracted"), m.get("is_replication")) for m in S["measurements"] if m.get("submitter") == "Reticuli" and m["manifest_hash"] not in fresh] + [(r["manifest_hash"], r.get("bank_id"), "read today", r.get("retracted"), None) for r in new]
assert len({h for h, *_ in mine}) == len(mine), "a measurement is listed twice"
out = []; st = collections.Counter()
for h, bid, src, retr, repl in mine:
    b = banks.get(bid) if bid else None
    if not b or b.get("state") != "scored":
        st["not scored"] += 1; out.append({"measurement": h, "bank": bid, "source": src, "result": "not scored", "why": (b or {}).get("state", "no pinned bank on file")}); continue
    share = b["best_order_share"]; cls = "complete" if b["best_order"] == b["usable"] else ("90% or more" if share >= 0.9 else ("60% to 90%" if share >= 0.6 else "under 60%"))
    st[cls] += 1; out.append({"measurement": h, "bank": bid, "source": src, "retracted": retr, "is_replication": repl, "result": cls, "rule": b["best_order_rule"], "hits": b["best_order"], "usable": b["usable"], "options": b["options"], "chance": b["chance"]})
print("my reader-panel measurements:", len(mine), dict(st))
for o in out:
    if o["result"] in ("complete", "90% or more"): print("  ", o["measurement"][:8], "bank", o["bank"][:8], "|", o["rule"], "|", "%d of %d" % (o["hits"], o["usable"]), "| options", o["options"], "| retracted", o["retracted"], "| replication", o["is_replication"], "|", o["source"])
print("60 to 90%:", [(o["measurement"][:8], o["rule"], o["hits"], o["usable"], o["options"]) for o in out if o["result"] == "60% to 90%"])
print("not scored:", collections.Counter(o["why"] for o in out if o["result"] == "not scored"))
json.dump({"mine": out, "counts": dict(st), "total": len(mine)}, open(sys.argv[4], "w"), indent=1)
