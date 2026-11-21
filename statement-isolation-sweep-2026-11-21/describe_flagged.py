"""describe_flagged.py: written AFTER the results were known, to say WHY a flagged bank is answered blind. It changes no figure of
results.json and decides nothing. Per distinct bank it adds, from blind_items.jsonl and reads.jsonl alone:
  top_key_share      the share of real items whose key is the bank's most common key text (1.0: every item has the same key)
  keyed_to_question  the share of real items whose key is the most common key among the items with the same question and the
                     same set of options: what a reader scores who learns the usual answer to each question and never reads a message
  blind_by_question  per question (with at least 6 items): items, how many answered blind
Writes described.json and prints the flagged banks, most affected first."""
import collections, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
jl = lambda n: [json.loads(l) for l in open(os.path.join(HERE, n), encoding="utf-8") if l.strip()]
items = {r["id"]: r for r in jl("blind_items.jsonl")}; reads = {r["id"]: r for r in jl("reads.jsonl")}; res = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
banks = {b["sha256_items"]: b for b in json.load(open(os.path.join(HERE, "banks.json"), encoding="utf-8"))}
out = []
for r in res["rows"]:
    ids = [i for i in banks[r["sha256_items"]]["item_ids"] if not items[i]["calibration"] and not items[i]["identical_arms"]]
    if not ids: continue
    keys = collections.Counter(items[i]["answer"] for i in ids); byq = collections.defaultdict(list)
    for i in ids: byq[(items[i]["question"], tuple(sorted(items[i]["options"])))].append(i)
    usual = sum(collections.Counter(items[i]["answer"] for i in g).most_common(1)[0][1] for g in byq.values())
    perq = sorted(({"question": q[:110], "items": len(g), "answered_blind": sum(reads[i].get("picked") == items[i]["answer"] for i in g), "distinct_keys": len({items[i]["answer"] for i in g})} for (q, _), g in byq.items() if len(g) >= 6),
                  key=lambda x: -x["answered_blind"] / x["items"])
    out.append({"bank": r["files"][0], "sha256_items": r["sha256_items"], "n": r["n"], "blind": r["blind"], "excess": r["excess"], "flagged": r["flagged"], "top_key_share": round(keys.most_common(1)[0][1] / len(ids), 3),
                "keyed_to_question": round(usual / len(ids), 3), "distinct_questions": len(byq), "blind_by_question": perq})
json.dump(out, open(os.path.join(HERE, "described.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("%-62s %4s %5s %6s %8s %9s %s" % ("flagged bank", "n", "blind", "excess", "same key", "by quest.", "questions"))
for o in sorted((o for o in out if o["flagged"]), key=lambda o: -o["excess"]):
    print("%-62s %4d %5d %6.2f %8.2f %9.2f %d" % (o["bank"][:62], o["n"], o["blind"], o["excess"], o["top_key_share"], o["keyed_to_question"], o["distinct_questions"]))
