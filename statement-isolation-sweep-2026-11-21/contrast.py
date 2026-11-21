"""contrast.py: written AFTER the results, to correct how I read a flag. A flag says the blind reader beats its own shuffled
answers. That happens in two different ways, and only one is the fault the sweep was after:
  - the KEY can be reached without the wording under test (the fault), or
  - some OPTIONS can be dismissed without it (weak distractors), while the choice among the rest still needs the wording.
A bank can show which, without any reader. Two items with the SAME blind text, question and options but DIFFERENT keys are a
contrast: nothing a blind reader does can get both right. Per distinct bank, from blind_items.jsonl and reads.jsonl alone:
  contrast_share   the share of real items whose blind form also occurs in the bank with another key
  ceiling          the best any blind reader can score: per blind form the count of its most common key, summed, over n
  blind_rate       what the blind reader scored, over n
  solo_n, solo_blind, solo_null   the items with NO contrast twin: how many, how many answered blind, and the shuffled null on them
  solo_excess      the share of solo items answered blind beyond that null
  reading          'needs the wording' when at least 90 in 100 items have a contrast twin (the blind reader can only guess between
                   keys); 'key reachable' when the solo items are flagged on their own (p < 0.05 / number of tested banks) and
                   their excess is at least 0.5; 'in between' otherwise
It changes nothing in results.json. Writes contrast.json and prints the flagged banks."""
import collections, json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import analyse as A
jl = lambda n: [json.loads(l) for l in open(os.path.join(HERE, n), encoding="utf-8") if l.strip()]
items = {r["id"]: r for r in jl("blind_items.jsonl")}; reads = {r["id"]: r for r in jl("reads.jsonl")}; res = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
banks = {b["sha256_items"]: b for b in json.load(open(os.path.join(HERE, "banks.json"), encoding="utf-8"))}; rng = np.random.default_rng(A.SEED); alpha = res["alpha_per_bank"]; out = []
for r in res["rows"]:
    ids = [i for i in banks[r["sha256_items"]]["item_ids"] if not items[i]["calibration"] and not items[i]["identical_arms"]]
    if len(ids) < A.MIN_N: continue
    groups = collections.defaultdict(list)
    for i in ids: groups[(items[i]["blind"], items[i]["question"], tuple(sorted(items[i]["options"])))].append(i)
    twin = set(); ceil = 0
    for g in groups.values():
        keys = collections.Counter(items[i]["answer"] for i in g); ceil += keys.most_common(1)[0][1]
        if len(keys) > 1: twin |= set(g)
    solo = [i for i in ids if i not in twin]; s = A.score(solo, items, reads, rng) if solo else {"n": 0, "blind": 0, "null_mean": 0.0, "p": 1.0, "excess": 0.0}
    hit = sum(reads[i].get("picked") == items[i]["answer"] for i in ids); cs = len(twin) / len(ids)
    reading = "needs the wording" if cs >= 0.9 else ("key reachable" if s["n"] >= A.MIN_N and s["p"] < alpha and s["excess"] >= 0.5 else "in between")
    out.append({"bank": r["files"][0], "sha256_items": r["sha256_items"], "n": len(ids), "flagged": r["flagged"], "excess": r["excess"], "blind": hit, "blind_rate": round(hit / len(ids), 3), "contrast_share": round(cs, 3), "ceiling": round(ceil / len(ids), 3),
                "solo_n": s["n"], "solo_blind": s["blind"], "solo_null": s["null_mean"], "solo_p": s["p"], "solo_excess": s["excess"], "reading": reading})
json.dump(out, open(os.path.join(HERE, "contrast.json"), "w", encoding="utf-8"), indent=1)
fl = [o for o in out if o["flagged"]]; c = collections.Counter(o["reading"] for o in fl)
print("flagged banks by reading:", dict(c), "| unflagged:", dict(collections.Counter(o["reading"] for o in out if not o["flagged"])))
print("%-60s %4s %6s %6s %8s %7s | %5s %5s %6s %6s  %s" % ("flagged bank", "n", "excess", "blind", "contrast", "ceiling", "solo", "blind", "null", "excess", "reading"))
for o in sorted(fl, key=lambda o: (o["reading"], -o["excess"])):
    print("%-60s %4d %6.2f %6.2f %8.2f %7.2f | %5d %5d %6.1f %6.2f  %s" % (o["bank"][:60], o["n"], o["excess"], o["blind_rate"], o["contrast_share"], o["ceiling"], o["solo_n"], o["solo_blind"], o["solo_null"], o["solo_excess"], o["reading"]))
