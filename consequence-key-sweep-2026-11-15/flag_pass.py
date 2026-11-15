"""flag_pass.py: read-only, no network; run with python3 -I. A second, item-level net under the bank-level reading.
The bank-level reading (consequence_sweep.py, build_public.py) looks at each bank's most frequent question stems and two samples,
so a few items of the class could hide in a bank with many different questions. This pass reads EVERY scored item of every bank
that was read and flags any whose question asks, in so many words, about a present or resulting state of the world.
POSITIVE CONTROL: the 48 scored items of the bank behind 7200b173 must all be flagged, or the net is broken.
Arguments: 1 = the October cache directory, 2 = yesterday's round directory, 3 = output json."""
import collections, json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)); CACHE, Y, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
I = json.load(open(os.path.join(CACHE, "bank_index.json"))); paths = {b["bank_id"]: os.path.join(CACHE, b["path"]) for b in I["banks"] if b.get("path")}
for f in ("sweep_extra.json", "sweep_extra2.json"):
    for e in json.load(open(os.path.join(Y, f))): paths[e["bank_id"]] = e["path"]
MINE = json.load(open(os.path.join(Y, "my_rows_sweep.json")))["mine"]; FOUND = json.load(open(D + "/dl/missing_found.json"))
NET = re.compile(r"state of the world|what is true now|what (has )?happened|what is the (current |present |resulting )?(state|status)\b|resulting state|"
                 r"\bis (it|the \w+( \w+)?) (now|still|currently|already) |\b(has|have) (it|the \w+( \w+)?) (now |already |actually )?been \w+ed\b|did .* (actually )?(happen|take place|go ahead|proceed)\b|was .* (actually )?(carried out|performed|done|merged|sent|deleted|deployed)\b", re.I)


def is_cal(it): return bool(it.get("calibration")) or bool(it.get("control")) or it.get("kind") == "calibration" or "calibration_construct" in it or "calibration_truth" in it or it.get("key_class") == "calibration"
def load(p):
    J = json.load(open(p, encoding="utf-8")); items = J if isinstance(J, list) else (J.get("items") or J.get("bank") or J.get("pairs") or [])
    return [i for i in items if isinstance(i, dict) and not is_cal(i)]


out = []; total = 0
for r in MINE:
    h = r["measurement"]; p = paths.get(r.get("bank")) if r.get("bank") else None
    if not (p and os.path.exists(p)): p = FOUND.get(h)
    if not p: continue
    real = load(p); total += len(real); fl = [i for i in real if NET.search(str(i.get("question") or i.get("prompt") or ""))]
    out.append({"measurement": h, "scored_items": len(real), "flagged": len(fl), "examples": [str(i.get("question"))[:200] for i in fl[:3]]})
ctl = [o for o in out if o["measurement"].startswith("7200b173")]; assert len(ctl) == 1 and ctl[0]["flagged"] == ctl[0]["scored_items"] == 48, ctl     # the net fires on the known case
json.dump({"banks_read_from_files": len(out), "scored_items_read": total, "rows": out}, open(OUT, "w"), indent=1, ensure_ascii=False)
print("banks read from files", len(out), "| scored items read", total, "| banks with a flagged item:", sum(o["flagged"] > 0 for o in out))
for o in out:
    if o["flagged"]: print("  ", o["measurement"][:8], "flagged %d of %d" % (o["flagged"], o["scored_items"]), "|", o["examples"])
