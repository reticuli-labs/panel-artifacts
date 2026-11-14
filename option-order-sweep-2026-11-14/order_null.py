"""Null control for order_sweep.py: take every cached bank on which an order rule recovered every key, shuffle each item's
options with a seeded permutation (the key moves with its text), and score the same rule family again. If the sweep's hits came
from the family being too rich, the shuffled banks would keep them. Reads order_sweep.json (argument 1) and the October cache
(argument 2); writes argument 3. Run with python3 -I. It imports nothing from the sweep: the scorer is passed the shuffled items
through a temporary file, so the code under test is the code that produced the hits."""
import collections, json, os, random, subprocess, sys, tempfile
R = json.load(open(sys.argv[1])); CACHE = sys.argv[2]; I = {b["bank_id"]: b for b in json.load(open(os.path.join(CACHE, "bank_index.json")))["banks"]}
HERE = os.path.dirname(os.path.abspath(__file__))
complete = [b for b in R["banks"].values() if b["state"] == "scored" and b["options"] >= 3 and b["best_order"] == b["usable"]]
tmp = tempfile.mkdtemp(prefix="null_"); os.makedirs(os.path.join(tmp, "banks")); index = {"banks": []}
rng = random.Random(20261114)
for b in complete:
    parsed = json.loads(open(os.path.join(CACHE, I[b["bank_id"]]["path"]), "rb").read().decode("utf-8"))
    items = parsed.get("items") if isinstance(parsed, dict) and "items" in parsed else parsed.get("test_set") if isinstance(parsed, dict) and "test_set" in parsed else parsed
    out = []
    for it in items:
        it = dict(it); opts = it.get("options")
        if isinstance(opts, list) and all(isinstance(o, str) for o in opts) and isinstance(it.get("answer", it.get("key")), str):
            o2 = list(opts); rng.shuffle(o2); it["options"] = o2                              # the key is named by its text, so it moves with it
        out.append(it)
    p = "banks/%s.json" % b["bank_id"][:24]; json.dump(out, open(os.path.join(tmp, p), "w")); index["banks"].append({"bank_id": b["bank_id"], "path": p, "manifest_hashes": []})
# the sweep asserts its positive control, which must be in the index: add my 636e31d4 bank UNSHUFFLED as that control
ctrl = "0e3cf6b2ccdab95cd71138fc6f5bb40e064908871b84e2c5fdf7ed73a7997ba9"
index["banks"] = [x for x in index["banks"] if x["bank_id"] != ctrl]; raw = open(os.path.join(CACHE, I[ctrl]["path"]), "rb").read(); open(os.path.join(tmp, "banks/ctrl.json"), "wb").write(raw)
index["banks"].append({"bank_id": ctrl, "path": "banks/ctrl.json", "manifest_hashes": []})
json.dump(index, open(os.path.join(tmp, "bank_index.json"), "w")); json.dump([], open(os.path.join(tmp, "comp_measurements.json"), "w"))
r = subprocess.run([sys.executable, "-I", os.path.join(HERE, "order_sweep.py"), tmp, os.path.join(tmp, "out.json")], capture_output=True, text=True); assert r.returncode == 0, r.stderr[-400:]
N = json.load(open(os.path.join(tmp, "out.json")))["banks"]; sh = [v for k, v in N.items() if k != ctrl and v["state"] == "scored"]
keep = [v for v in sh if v["best_order"] == v["usable"]]; shares = sorted(v["best_order_share"] for v in sh)
res = {"seed": 20261114, "banks_shuffled": len(sh), "not_shuffled_because_options_or_key_are_not_plain_text": len(complete) - 1 - len(sh) if ctrl in {b["bank_id"] for b in complete} else len(complete) - len(sh),
       "still_complete_after_shuffle": len(keep), "still_at_90pct": sum(1 for s in shares if s >= 0.9), "best_share_after_shuffle": {"min": shares[0], "median": shares[len(shares) // 2], "max": shares[-1]},
       "still_complete": [{"bank": v["bank_id"][:8], "usable": v["usable"], "rule": v["best_order_rule"]} for v in keep], "unshuffled_control_complete": N[ctrl]["best_order"] == N[ctrl]["usable"]}
json.dump(res, open(sys.argv[3], "w"), indent=1); print(json.dumps(res, indent=1))
