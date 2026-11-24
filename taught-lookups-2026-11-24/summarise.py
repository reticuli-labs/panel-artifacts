"""summarise.py: read results_run3.json beside this file and write table.md: every bank with a flagged lookup, sorted into three
kinds by which lookups are flagged. Reads one file, writes one file, calls nothing."""
import collections, json, os
HERE = os.path.dirname(os.path.abspath(__file__)); r = json.load(open(os.path.join(HERE, "results_run3.json"), encoding="utf-8"))
BASE = ("menu", "options", "label0", "label1", "label2")
fam = lambda b, f: any(b["rules"][f + d]["flagged"] for d in ("/a", "/b"))
cell = lambda b, f: " + ".join("%d of %d" % (b["rules"][f + d]["right"], b["rules"][f + d]["decided"]) for d in ("/a", "/b"))


def kind(b):
    if any(fam(b, f) for f in ("label0", "label1", "label2")): return "label"
    if fam(b, "menu") and not fam(b, "options"): return "order"
    return "options"


rows = [b for b in r["rows"] if b["flagged_rules"]]; by = collections.defaultdict(list)
for b in rows: by[kind(b)].append(b)
TITLE = {"order": "The order of the options names the key (flagged on `menu`, not on `options`)", "options": "The options name the key whatever their order (flagged on `options`; `menu` shown beside it)",
         "label": "An identifier in the shared text names the key (flagged on a label lookup)"}
out = ["# Run 3: banks with a flagged lookup", "", "Right answers of items answered, for each of the two directions (taught on one half, scored on the other). A lookup that is not",
       "flagged in either direction is left out of a row. %d banks tested, %d tests, level per test %.6f; with keys drawn at random: %d banks flagged." % (r["banks_tested"], r["tests"], r["alpha_per_test"], r["control_keys_drawn_at_random"]["banks_with_a_flagged_rule"]), ""]
for k in ("order", "options", "label"):
    out += ["## " + TITLE[k], "", "| bank | real items | lookup: right of answered, both directions |", "|---|---|---|"]
    for b in sorted(by[k], key=lambda b: b["bank"]):
        out.append("| `%s` | %d | %s |" % (b["bank"], b["n"], "; ".join("%s %s" % (f, cell(b, f)) for f in BASE if fam(b, f))))
    out += ["", "%d bank files, in %d directories." % (len(by[k]), len({b["bank"].rsplit("/", 1)[0] for b in by[k]})), ""]
allright = [b for b in by["order"] if all(b["rules"]["menu" + d]["wrong"] == 0 for d in ("/a", "/b"))]
out += ["Of the %d bank files of the first kind, %d have no wrong answer from `menu` in either direction." % (len(by["order"]), len(allright)), ""]
open(os.path.join(HERE, "table.md"), "w", encoding="utf-8").write("\n".join(out))
print(json.dumps({"flagged": len(rows), "by_kind": {k: len(v) for k, v in by.items()}, "dirs_by_kind": {k: sorted({b["bank"].rsplit("/", 1)[0] for b in v}) for k, v in by.items()}, "order_all_right": len(allright)}, indent=1))
