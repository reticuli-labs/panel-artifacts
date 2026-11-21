"""second_look_repeat_restore.py: a second look at SAVED panel answers, chosen after the sweep's results were known. A diagnostic;
no new measurement, and nothing is filed. It asks one thing: do items whose key follows from text both arms share still show a
difference between the arms? In ../repeat-restore-comp-2026-08-31, 128 of the 256 real items ask what the main clause does with
the action it names; the main clause is the same in both arms, and the sweep's blind reader answered all 128. The other 128 ask
what the statement presupposes, which depends on the wording under test. The panel's saved answers (one cell per item, the arm
dealt by the harness) are split by those two kinds. Reads only files of this repository; writes second_look_repeat_restore.json."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.join(os.path.dirname(HERE), "repeat-restore-comp-2026-08-31"); sys.path.insert(0, HERE)
import build_blind as BB
its = json.load(open(os.path.join(B, "items.json"), encoding="utf-8")); its = its if isinstance(its, list) else its["items"]; byid = {i["id"]: i for i in its}
cells = json.load(open(os.path.join(B, "runspec.json.attempt-26f2f557-a8e7-417f-9cff-8afd7f385620.cells.json"), encoding="utf-8")); rows = cells["rows"]
filed = json.load(open(os.path.join(B, "runspec.json.attempt-26f2f557-a8e7-417f-9cff-8afd7f385620.measurement.json"), encoding="utf-8"))
reads = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(HERE, "reads.jsonl"), encoding="utf-8")}
FORCE = {"it is stated as having happened", "it is stated as not having happened", "it is asked about as a question", "it is requested to be carried out"}
real = [i for i in its if not i.get("calibration")]; kind = lambda it: "main clause, the same in both arms" if it["answer"] in FORCE else "presupposition, depends on the wording"
same = [i for i in real if i["answer"] in FORCE]
# the claim that the main clause is the same in both arms, checked: the careful-English arm begins with the marked arm's clause
clause = lambda it: it["ainglish"].rsplit(": ", 1)[1]                 # what follows the marker; an item may open with a context sentence that has a colon of its own
assert len(real) == 256 and len(same) == 128 and len(rows) == 256 and len({r["item_id"] for r in rows}) == 256 and cells["attempt_id"] == filed["attempt_id"]
shared = sum(1 for i in same if clause(i) in i["english"]); assert shared == len(same), "the main clause does not stand word for word in the careful arm of %d items" % (len(same) - shared)
blind = collections.Counter(); acc = collections.defaultdict(lambda: [0, 0])
for i in real: blind[kind(i)] += reads[BB.item_id(i)].get("picked") == i["answer"]
for r in rows:
    it = byid[r["item_id"]]; a = acc[(kind(it), r["arm"])]; a[0] += bool(r["correct"]); a[1] += 1
out = {"what": "a second look at saved answers, chosen after the fact", "filed_value": filed["value"], "reader": filed.get("panel_models"), "items": {k: sum(1 for i in real if kind(i) == k) for k in sorted({kind(i) for i in real})},
       "main_clause_found_in_the_careful_arm": "%d of %d" % (shared, len(same)), "answered_blind": dict(blind), "panel": {}}
for k in sorted({kind(i) for i in real}):
    m, e = acc[(k, "ainglish")], acc[(k, "english")]
    out["panel"][k] = {"marked": "%d of %d" % tuple(m), "careful": "%d of %d" % tuple(e), "difference_points": round(100 * (m[0] / m[1] - e[0] / e[1]), 1)}
json.dump(out, open(os.path.join(HERE, "second_look_repeat_restore.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False); print(json.dumps(out, indent=1, ensure_ascii=False))
