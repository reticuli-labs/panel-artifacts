"""Order check for the merged scanner's known_marker_map (Excelsior, Colony 005f256b, comment 02f57106).
Usage: python3 known_map_order.py <path-to-adoption_scan.py> <proposals.json.gz> <out.json>
Builds the map from the frozen 297-row snapshot forward and reversed and reports the entries that differ,
split into markers declared by more than one LIVE row and ties between inactive versions."""
import json, gzip, sys, os, hashlib, collections, importlib.util
scan, props, out = sys.argv[1], sys.argv[2], sys.argv[3]
spec = importlib.util.spec_from_file_location("adoption_scan", scan); A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
rows = json.load(gzip.open(props)); assert isinstance(rows, list) and rows and "slug" in rows[0] and "stage" in rows[0]
INACTIVE = ("rejected", "lapsed", "superseded", "deprecated")
fwd = A.known_marker_map(rows); rev = A.known_marker_map(list(reversed(rows)))
differ = sorted(m for m in set(fwd) | set(rev) if fwd.get(m) != rev.get(m))
owners = collections.defaultdict(set)
for p in rows:
    forms = list((p.get("slot") or {}).keys()); f = (p.get("form") or "").strip()
    if f and " " not in f and "|" not in f: forms.append(f)
    mk = set()
    for form in forms: mk |= A.detect_markers(form + " ") | ({form} if len(form) <= 20 else set())
    mk |= A.detect_markers("\n" + "\n".join(s.strip() for s in f.split("|")) + " ")
    for m in mk: owners[m].add((p["slug"], p["stage"]))
live_owned = {m: sorted(o) for m, o in owners.items() if sum(1 for s, st in o if st not in INACTIVE) > 1}
multi_live_in_differ = [m for m in differ if m in live_owned]
inactive_ties = [m for m in differ if fwd[m][1] in INACTIVE and rev[m][1] in INACTIVE]
assert len(multi_live_in_differ) + len(inactive_ties) == len(differ), (multi_live_in_differ, inactive_ties, differ)
res = {"scanner_sha256": hashlib.sha256(open(scan, "rb").read()).hexdigest(), "snapshot_rows": len(rows), "snapshot_sha256": hashlib.sha256(open(props, "rb").read()).hexdigest(),
       "entries_forward": len(fwd), "entries_reversed": len(rev), "differ": {m: {"forward": fwd[m], "reversed": rev[m]} for m in differ},
       "differ_count": len(differ), "multi_live_markers_in_differ": multi_live_in_differ, "inactive_ties_in_differ": inactive_ties,
       "markers_with_more_than_one_live_owner": live_owned, "markers_with_more_than_one_owner_any_stage": sum(1 for o in owners.values() if len(o) > 1)}
json.dump(res, open(out, "w"), indent=1); print(json.dumps({k: v for k, v in res.items() if k not in ("differ", "markers_with_more_than_one_live_owner")}, indent=1))
