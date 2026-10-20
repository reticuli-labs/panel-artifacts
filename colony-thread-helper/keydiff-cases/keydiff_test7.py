"""Seventh case for fieldnotes ad7d9ff7 on 4d855cae (2026-10-20): a rename in transition, the new key served on every common row while the old key is still present. key_diff is lifted from fetch.py by ast and run alone, as in keydiff_test.py (2026-10-19)."""
import ast, json, glob, copy, hashlib
src = open("fetch.py", encoding="utf-8").read(); mod = ast.parse(src)
fn = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name == "key_diff"]; assert len(fn) == 1
ns = {"json": json}; exec(compile(ast.Module(body=fn, type_ignores=[]), "fetch.py:key_diff", "exec"), ns); key_diff = ns["key_diff"]
RULE = ["id", "author", "created_at", "body"]
def missing_for(post, cs): return [[r.get("id"), f] for r in [post] + cs for f in RULE if f not in r]
def suspect(kd, missing): return None if not kd["rows_compared"] else bool(missing and kd["keys_added_on_all_common_rows"])
pf = glob.glob("threads/4d855cae*.json")[0]; pid = pf.split("/")[-1][:-5]; pj = json.load(open(pf)); P, C = pj["post"], pj["comments"]
out = {"prior_copy": pid, "prior_rows": 1 + len(C), "cases": {}}
# 7 transition: posted_at added on every row, created_at kept on every row
P7, C7 = copy.deepcopy(P), copy.deepcopy(C)
for r in [P7] + C7: r["posted_at"] = r["created_at"]
kd = key_diff(pid, P7, C7); out["cases"]["rename_in_transition_old_key_kept"] = {"missing_pairs": len(missing_for(P7, C7)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P7, C7))}
# 7b the transition plus one new comment carrying both keys
P7b, C7b = copy.deepcopy(P7), copy.deepcopy(C7); C7b.append(dict(copy.deepcopy(C7[0]), id="ffffffff-0000-4000-8000-000000000007"))
kd = key_diff(pid, P7b, C7b); out["cases"]["transition_plus_new_comment"] = {"missing_pairs": len(missing_for(P7b, C7b)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P7b, C7b))}
# 7c the transition ends: old key dropped on every row (= case 2 of 10-19, re-run on today's copy)
P7c, C7c = copy.deepcopy(P7), copy.deepcopy(C7)
for r in [P7c] + C7c: r.pop("created_at")
kd = key_diff(pid, P7c, C7c); out["cases"]["transition_ends_old_key_dropped"] = {"missing_pairs": len(missing_for(P7c, C7c)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P7c, C7c))}
c = out["cases"]; n = 1 + len(C)
a = c["rename_in_transition_old_key_kept"]
assert a["rename_suspect"] is False and a["missing_pairs"] == 0 and a["key_diff"]["keys_added_on_all_common_rows"] == ["posted_at"] and a["key_diff"]["keys_removed_from_all_common_rows"] == [] and a["key_diff"]["keys_removed_from_some_common_rows"] == [] and a["key_diff"]["rows_compared"] == n, a
b = c["transition_plus_new_comment"]
assert b["rename_suspect"] is False and b["missing_pairs"] == 0 and b["key_diff"]["keys_added_on_all_common_rows"] == ["posted_at"] and b["key_diff"]["rows_only_now"] == 1, b
d = c["transition_ends_old_key_dropped"]
assert d["rename_suspect"] is True and d["missing_pairs"] == n and d["key_diff"]["keys_added_on_all_common_rows"] == ["posted_at"] and d["key_diff"]["keys_removed_from_all_common_rows"] == ["created_at"], d
out["carrier_sha256"] = hashlib.sha256(src.encode("utf-8")).hexdigest()
json.dump(out, open("keydiff_sim7.json", "w"), indent=1)
for k, v in c.items(): print(f"{k:40s} suspect={v['rename_suspect']!s:5s} missing={v['missing_pairs']} all+={v['key_diff']['keys_added_on_all_common_rows']} all-={v['key_diff']['keys_removed_from_all_common_rows']} some-={v['key_diff']['keys_removed_from_some_common_rows']} rows={v['key_diff']['rows_compared']}/{v['key_diff']['rows_only_now']}")
print("ALL ASSERTS PASSED; rows", n, "carrier", out["carrier_sha256"][:16])
