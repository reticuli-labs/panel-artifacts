"""selfcheck_analysis.py: show that analyse.py can tell readers apart whose behaviour is known, before any real read is used.
It writes made-up reads into fresh scratch directories (never beside the real ones), runs analyse.py on each, and requires:
  guesser     answers at random everywhere: no bank flagged (at most one, by chance), and the instrument checks FAIL
              (a guesser does not find an answer that is written into its text);
  first       always answers the first choice: no bank flagged, although in some banks the key is often first;
  one bank    knows the key of every real item of ONE bank and guesses elsewhere, and behaves on the controls as an honest
              reader would: that bank is flagged with excess near 1, the instrument checks pass, and every other flagged
              bank shares items with it (the same item stands in several files: a pool and its seats, an original and its copy);
  half        knows the key for every second real item of that bank: flagged, excess between 0.3 and 0.7, and again every
              other flagged bank shares items with it.
Needs the files build_blind.py wrote (also PLANT=1). Prints one line per reader and writes selfcheck_analysis.json."""
import json, os, random, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); rng = random.Random(7)
jl = lambda p: [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
items = jl(os.path.join(HERE, "blind_items.jsonl")); controls = jl(os.path.join(HERE, "controls.jsonl")); banks = json.load(open(os.path.join(HERE, "banks.json"), encoding="utf-8"))
pitems = jl(os.path.join(HERE, "planted", "blind_items.jsonl")); sys.path.insert(0, HERE); import build_blind as B
pcls = {B.item_id(it): it["planted_class"] for it in json.load(open(os.path.join(HERE, "planted", "items.json"), encoding="utf-8"))}
byid = {r["id"]: r for r in items}
target = max((b for b in banks if sum(1 for i in b["item_ids"] if not byid[i]["calibration"] and not byid[i]["identical_arms"]) >= 60), key=lambda b: len(b["item_ids"]))
tset = {i for i in target["item_ids"] if not byid[i]["calibration"]}; tname = target["dir"] + "/" + target["file"]
ids_of = {b["dir"] + "/" + b["file"]: set(b["item_ids"]) for b in banks}


def reads(policy):
    """policy(row, where) -> the option picked. where: 'bank', 'planted', 'sighted', 'gap-only', 'shared'."""
    main = [{"id": r["id"], "picked": policy(r, "bank"), "truncated": False} for r in items]
    ctl = [{"id": c["id"], "picked": policy(c, c["kind"]), "truncated": False} for c in controls]
    pl = [{"id": r["id"], "picked": policy(r, "gap-only" if pcls[r["id"]] == "key only in the gap" else "shared"), "truncated": False} for r in pitems]
    return main, ctl, pl


def run(name, policy):
    root = tempfile.mkdtemp(prefix="sweep_selfcheck_"); os.makedirs(os.path.join(root, "planted"))
    for f in ("banks.json", "blind_items.jsonl", "controls.jsonl"): shutil.copy(os.path.join(HERE, f), root)
    for f in ("blind_items.jsonl", "items.json"): shutil.copy(os.path.join(HERE, "planted", f), os.path.join(root, "planted"))
    main, ctl, pl = reads(policy)
    for path, rows in (("reads.jsonl", main), ("reads_controls.jsonl", ctl), ("planted/reads.jsonl", pl)):
        open(os.path.join(root, path), "w", encoding="utf-8").write("\n".join(json.dumps(r) for r in rows) + "\n")
    r = subprocess.run([sys.executable, os.path.join(HERE, "analyse.py")], capture_output=True, text=True, env=dict(os.environ, RESULTS_DIR=root)); assert r.returncode == 0, r.stderr[-400:]
    out = json.load(open(os.path.join(root, "results.json"), encoding="utf-8")); shutil.rmtree(root); return out


guess = lambda r, w: rng.choice(r["options"])
honest_controls = lambda r, w: r["answer"] if w in ("planted", "sighted", "shared") else rng.choice(r["options"])
one = lambda r, w: r["answer"] if (w == "bank" and r["id"] in tset) else honest_controls(r, w)
flip = {i: (k % 2 == 0) for k, i in enumerate(sorted(tset))}
half = lambda r, w: r["answer"] if (w == "bank" and flip.get(r["id"])) else honest_controls(r, w)
report, bad = {}, []
for name, policy in (("guesser", guess), ("first", lambda r, w: r["options"][0]), ("one bank", one), ("half", half)):
    o = run(name, policy); row = next(x for x in o["rows"] if tname in x["files"]); others = sum(x["flagged"] for x in o["rows"]) - row["flagged"]
    strangers = [x["files"][0] for x in o["rows"] if x["flagged"] and x is not row and not (ids_of[x["files"][0]] & tset)]
    report[name] = {"flagged": o["flagged"], "instrument_ok": o["instrument_ok"], "target_flagged": row["flagged"], "target_excess": row["excess"], "other_banks_flagged": others, "of_them_sharing_no_item_with_the_target": len(strangers), "banks_tested": o["banks_tested"]}
    ok = {"guesser": o["flagged"] <= 1 and not o["instrument_ok"], "first": o["flagged"] <= 1,
          "one bank": row["flagged"] and row["excess"] > 0.95 and o["instrument_ok"] and len(strangers) <= 1, "half": row["flagged"] and 0.3 < row["excess"] < 0.7 and len(strangers) <= 1}[name]
    if not ok: bad.append(name)
    print("%-9s %s | %s" % (name, "as required" if ok else "NOT AS REQUIRED", report[name]))
json.dump({"target_bank": tname, "readers": report, "not_as_required": bad}, open(os.path.join(HERE, "selfcheck_analysis.json"), "w", encoding="utf-8"), indent=1)
sys.exit(1 if bad else 0)
