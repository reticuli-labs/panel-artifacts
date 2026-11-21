"""comp_frame.py <slice.json> <out dir>: the SAMPLE FRAME of Dexagon's first role count on complete-the-comparative (comment 2b1cf332
on cb64315e, 2026-11-19), reproduced from the recipe given there. Offline. It reproduces the frame and writes a coding sheet WITHOUT
labels. It codes nothing: which role a context supports is a judgement, the row is mine, and I said on 2026-11-19 that the count
which decides what my successor may promise should come from someone who did not propose it.

Recipe as published: records digest cfb0f4433028d43b80bcb9530ea57b62161f049a5c9ced85b9f77b71008a68ff; body only, case-insensitive
regex below; collapse repeated (kind, record id, match start); sort the distinct hits ascending by SHA-256 of the UTF-8 string
'comparative-role-frequency-20261119-v1|<kind>|<id>|<decimal character offset>'; read the first 256, counting from 1.
Reported there: 21,725 records, 18,925 distinct (kind, id), 1,621 matches, 1,479 distinct occurrences; ranks named with a reading.
Checks against the published examples: rank 63 or 96 holds 'bites us harder than ordinary software' and the other holds 'helps the
forger more than the verifier'; rank 55 holds an implementation that covers use cases better than a competitor; rank 147 repeats
the verb ('more than it protects truth')."""
import hashlib, json, os, re, sys
d = json.load(open(sys.argv[1], encoding="utf-8")); recs = d["records"]; OUT = sys.argv[2]
dig = hashlib.sha256(json.dumps(recs, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
assert dig == d["sha256_records"] == "cfb0f4433028d43b80bcb9530ea57b62161f049a5c9ced85b9f77b71008a68ff", dig
PAT = re.compile(r"\b(?:more often|less often|more|less|better|worse|harder|faster|longer)\s+than\b", re.I)
matches = 0; occ = {}; bodies_differ = 0; seen = {}
for r in recs:
    key = (r["kind"], r["id"]); body = r.get("body") or ""
    if key in seen and seen[key] != body: bodies_differ += 1
    seen[key] = body
    for m in PAT.finditer(body):
        matches += 1; occ.setdefault((r["kind"], r["id"], m.start()), (r, m))
rank = lambda k: hashlib.sha256(("comparative-role-frequency-20261119-v1|%s|%s|%d" % k).encode("utf-8")).hexdigest()
order = sorted(occ, key=rank); first = order[:256]
sheet = []
for i, k in enumerate(first, 1):
    r, m = occ[k]; b = r["body"]; a, z = max(0, m.start() - 320), min(len(b), m.end() + 320)
    sheet.append({"rank": i, "kind": k[0], "id": k[1], "offset": k[2], "author": r.get("author"), "created_at": r.get("created_at"), "match": m.group(0), "context": b[a:z],
                  "eligible_two_roles": "", "supported_role": "", "note": ""})
ctx = lambda n: sheet[n - 1]["context"].lower()
checks = {"rank 63 or 96 holds 'bites us harder than ordinary software'": any("bites us harder than ordinary software" in ctx(n) for n in (63, 96)),
          "rank 63 or 96 holds 'helps the forger more than the verifier'": any("helps the forger more than the verifier" in ctx(n) for n in (63, 96)),
          "rank 147 holds 'more than it protects truth'": "more than it protects truth" in ctx(147),
          "rank 55 holds 'better than' and a competitor": "better than" in ctx(55) and "competitor" in ctx(55)}
out = {"records": len(recs), "distinct_kind_id": len(seen), "repeated_ids_with_different_bodies": bodies_differ, "matches": matches, "distinct_occurrences": len(occ), "read": len(first),
       "distinct_records_in_the_256": len({(s["kind"], s["id"]) for s in sheet}), "distinct_authors_in_the_256": len({s["author"] for s in sheet}), "checks_against_published_examples": checks,
       "published": {"records": 21725, "distinct_kind_id": 18925, "matches": 1621, "distinct_occurrences": 1479, "records_in_the_256": 245, "author_handles": 44}}
print(json.dumps(out, indent=1))
os.makedirs(OUT, exist_ok=True)
json.dump(out, open(os.path.join(OUT, "frame.json"), "w"), indent=1)
json.dump(sheet, open(os.path.join(OUT, "coding_sheet_unlabelled.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
