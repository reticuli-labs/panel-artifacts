"""Exercise fetch.py's key_diff without running fetch.py: the def is lifted from the source by ast and exec'd alone (fetch.py's top level fetches whatever is on argv)."""
import ast, json, glob, copy, sys
src = open("fetch.py", encoding="utf-8").read(); mod = ast.parse(src)
fn = [n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name == "key_diff"]; assert len(fn) == 1
ns = {"json": json}; exec(compile(ast.Module(body=fn, type_ignores=[]), "fetch.py:key_diff", "exec"), ns); key_diff = ns["key_diff"]
RULE = ["id", "author", "created_at", "body"]
def missing_for(post, cs): return [[r.get("id"), f] for r in [post] + cs for f in RULE if f not in r]
def suspect(kd, missing): return None if not kd["rows_compared"] else bool(missing and kd["keys_added_on_all_common_rows"])
pf = glob.glob("threads/4d855cae*.json")[0]; pid = pf.split("/")[-1][:-5]; pj = json.load(open(pf)); P, C = pj["post"], pj["comments"]
out = {"prior_copy": pid, "prior_rows": 1 + len(C), "cases": {}}
# 1 identical rows
kd = key_diff(pid, copy.deepcopy(P), copy.deepcopy(C)); out["cases"]["identical"] = {"key_diff": kd, "rename_suspect": suspect(kd, missing_for(P, C))}
# 2 rename created_at -> posted_at on every row
P2, C2 = copy.deepcopy(P), copy.deepcopy(C)
for r in [P2] + C2: r["posted_at"] = r.pop("created_at")
kd = key_diff(pid, P2, C2); out["cases"]["rename_all_rows"] = {"missing_pairs": len(missing_for(P2, C2)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P2, C2))}
# 3 one new comment carrying an optional field nobody else has
P3, C3 = copy.deepcopy(P), copy.deepcopy(C); C3.append(dict(copy.deepcopy(C[0]), id="ffffffff-0000-4000-8000-000000000001", optional_only_here=1))
kd = key_diff(pid, P3, C3); out["cases"]["new_comment_with_optional_field"] = {"key_diff": kd, "rename_suspect": suspect(kd, missing_for(P3, C3))}
# 3b same, but the rule field is also missing on that one new row (drop + optional, not a rename)
P3b, C3b = copy.deepcopy(P3), copy.deepcopy(C3); C3b[-1].pop("created_at")
kd = key_diff(pid, P3b, C3b); out["cases"]["new_comment_optional_field_and_rule_field_missing_on_it"] = {"missing_pairs": len(missing_for(P3b, C3b)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P3b, C3b))}
# 4 one existing comment gains edited_at (an optional field appearing on a row both copies hold)
P4, C4 = copy.deepcopy(P), copy.deepcopy(C); C4[3]["edited_at"] = "2026-10-19T08:00:00Z"
kd = key_diff(pid, P4, C4); out["cases"]["existing_comment_gains_optional_field"] = {"key_diff": kd, "rename_suspect": suspect(kd, missing_for(P4, C4))}
# 5 rename on every common row AND one new comment: still the rename shape
P5, C5 = copy.deepcopy(P2), copy.deepcopy(C2); C5.append(dict(copy.deepcopy(C2[0]), id="ffffffff-0000-4000-8000-000000000002"))
kd = key_diff(pid, P5, C5); out["cases"]["rename_all_rows_plus_new_comment"] = {"missing_pairs": len(missing_for(P5, C5)), "key_diff": kd, "rename_suspect": suspect(kd, missing_for(P5, C5))}
c = out["cases"]
assert c["identical"]["rename_suspect"] is False and c["identical"]["key_diff"]["keys_added_since_prior_copy"] == [] and c["identical"]["key_diff"]["keys_added_on_all_common_rows"] == [] and c["identical"]["key_diff"]["rows_compared"] == 1 + len(C)
assert c["rename_all_rows"]["rename_suspect"] is True and c["rename_all_rows"]["key_diff"]["keys_added_on_all_common_rows"] == ["posted_at"] and c["rename_all_rows"]["key_diff"]["keys_removed_from_all_common_rows"] == ["created_at"] and c["rename_all_rows"]["missing_pairs"] == 1 + len(C)
assert c["new_comment_with_optional_field"]["rename_suspect"] is False and c["new_comment_with_optional_field"]["key_diff"]["keys_added_since_prior_copy"] == ["optional_only_here"] and c["new_comment_with_optional_field"]["key_diff"]["keys_added_on_all_common_rows"] == [] and c["new_comment_with_optional_field"]["key_diff"]["rows_only_now"] == 1
assert c["new_comment_optional_field_and_rule_field_missing_on_it"]["rename_suspect"] is False and c["new_comment_optional_field_and_rule_field_missing_on_it"]["missing_pairs"] == 1
assert c["existing_comment_gains_optional_field"]["rename_suspect"] is False and c["existing_comment_gains_optional_field"]["key_diff"]["keys_added_on_some_common_rows"] == ["edited_at"] and c["existing_comment_gains_optional_field"]["key_diff"]["keys_added_on_all_common_rows"] == []
assert c["rename_all_rows_plus_new_comment"]["rename_suspect"] is True and c["rename_all_rows_plus_new_comment"]["key_diff"]["rows_only_now"] == 1
import hashlib; out["carrier_sha256"] = hashlib.sha256(src.encode("utf-8")).hexdigest()
json.dump(out, open("keydiff_sim.json", "w"), indent=1)
for k, v in c.items(): print(f"{k:58s} suspect={v['rename_suspect']!s:5s} union+={v['key_diff']['keys_added_since_prior_copy']} all+={v['key_diff']['keys_added_on_all_common_rows']} some+={v['key_diff']['keys_added_on_some_common_rows']} rows={v['key_diff']['rows_compared']}/{v['key_diff']['rows_only_now']}")
print("ALL ASSERTS PASSED; carrier", out["carrier_sha256"][:16])
