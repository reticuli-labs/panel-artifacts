"""score.py <manifest.json> <own_run.json> <report.txt> <out.json>: the sealed manifest against the detector's report and against my own run.

report.txt is the text of the detector's report as posted (one table row per file: | B01 | verdict | deciding check | outside | sibling-only |).
Nothing is taken from a summary: the verdict word is read from each row, the manifest gives the truth, own_run.json gives what the
published offline verifier said. Prints the tables and writes them."""
import hashlib, json, re, sys
MAN, RUN, REP, OUT = sys.argv[1:5]
raw = open(MAN, "rb").read(); m = json.loads(raw); run = json.load(open(RUN)); rep = open(REP, encoding="utf-8").read()
rows = {}
for line in rep.splitlines():
    c = [x.strip() for x in line.split("|")]
    if len(c) >= 7 and re.fullmatch(r"B\d\d", c[1]):
        word = c[2].split()[0].lower(); assert word in ("faithful", "altered", "cannot"), c[2]
        rows[c[1]] = {"verdict": "cannot tell" if word == "cannot" else word, "qualifier": c[2][len(c[2].split()[0]):].strip(), "outside_the_file": c[4], "sibling_only": c[5]}
assert sorted(rows) == sorted(m["variants"]) == ["B%02d" % i for i in range(1, 11)], sorted(rows)
out = {"manifest_sha256": hashlib.sha256(raw).hexdigest(), "report_sha256": hashlib.sha256(rep.encode("utf-8")).hexdigest(), "files": {}}
for b, v in sorted(m["variants"].items()):
    truth = "faithful" if v["kind"] == "control" else "altered"; r = rows[b]; ok = run["bundles"][b]["ok"]
    out["files"][b] = {"id": v["id"], "kind": v["kind"], "tier": v["tier"], "what": v["what"], "truth": truth, "detector_verdict": r["verdict"], "detector_qualifier": r["qualifier"], "detector_right": r["verdict"] == truth,
                       "sibling_only": r["sibling_only"], "predicted_detector_flags_it": v["predicted_detector_flags_it"], "detector_flagged_it": r["verdict"] == "altered",
                       "my_detector_prediction_right": v["predicted_detector_flags_it"] == (r["verdict"] == "altered"),
                       "predicted_offline_verifier": v["predicted_offline_verifier"], "offline_verifier_said": "PASS" if ok else "FAIL", "my_verifier_prediction_right": v["predicted_offline_verifier"] == ("PASS" if ok else "FAIL"),
                       "offline_verifier_fails": run["bundles"][b]["fails"]}
F = out["files"]; D = {b: f for b, f in F.items() if f["kind"] == "defect"}; C = {b: f for b, f in F.items() if f["kind"] == "control"}
out["totals"] = {
    "files": len(F), "defects": len(D), "controls": len(C),
    "detector_right": sum(f["detector_right"] for f in F.values()), "detector_defects_flagged": sum(f["detector_flagged_it"] for f in D.values()),
    "detector_false_positives": sum(f["detector_flagged_it"] for f in C.values()), "detector_cannot_tell": sum(f["detector_verdict"] == "cannot tell" for f in F.values()),
    "sibling_only_yes": sum(f["sibling_only"].lower() != "no" for f in F.values()),
    "offline_verifier_defects_failed": sum(f["offline_verifier_said"] == "FAIL" for f in D.values()), "offline_verifier_defects_passed": sum(f["offline_verifier_said"] == "PASS" for f in D.values()),
    "offline_verifier_controls_passed": sum(f["offline_verifier_said"] == "PASS" for f in C.values()),
    "my_verifier_predictions_right": sum(f["my_verifier_prediction_right"] for f in F.values()), "my_detector_predictions_right": sum(f["my_detector_prediction_right"] for f in F.values()),
    "my_detector_predictions_wrong": sorted(b for b, f in F.items() if not f["my_detector_prediction_right"]),
    "false_positives_predicted": m["prediction_summary"]["false_positives_predicted"],
    "defects_by_tier": {str(t): sorted(b for b, f in D.items() if f["tier"] == t) for t in (1, 2, 3)},
}
json.dump(out, open(OUT, "w"), indent=1)
print(json.dumps(out["totals"], indent=1))
for b, f in F.items():
    print("%s %-3s %-8s tier %-4s | detector %-9s %s | I predicted flag=%-5s %s | verifier predicted %s said %s %s" % (b, f["id"], f["kind"], f["tier"], f["detector_verdict"], "right" if f["detector_right"] else "WRONG", f["predicted_detector_flags_it"], "right" if f["my_detector_prediction_right"] else "WRONG", f["predicted_offline_verifier"], f["offline_verifier_said"], "right" if f["my_verifier_prediction_right"] else "WRONG"))
