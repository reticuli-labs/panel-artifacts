"""Hand my bank's record to the packet's own structure check and write down each refusal, bending the record one step
at a time until the check accepts it. Three of the bends are statements that are false of this bank.

usage: python3 -I ladder.py <packet dir> <record.json> <stored manifest> <items file>

Only validate_structure is called. It reads its arguments and nothing else. Prints one JSON list."""
import copy
import importlib.util
import json
import sys

packet, record_path, manifest_path, items_path = sys.argv[1:5]
spec = importlib.util.spec_from_file_location("packet_audit", packet + "/audit.py")
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)
raw = open(manifest_path, "rb").read()
manifest = json.loads(raw)
items = json.load(open(items_path))
record = json.load(open(record_path))
steps = []


def attempt(label, rec, man, true_of_bank):
    row = {"bend": label, "true_of_the_bank": true_of_bank}
    try:
        A.validate_structure(rec, raw, man)
        row["check"] = "accepted"
    except ValueError as e:
        row["check"] = "refused: " + str(e)
    except Exception as e:          # the check itself fell over
        row["check"] = "raised %s: %s" % (type(e).__name__, e)
    steps.append(row)
    return row["check"] == "accepted"


r, m = copy.deepcopy(record), copy.deepcopy(manifest)
attempt("none: the record as the bank is", r, m, True)
r["source"]["items_path"] = "test_set"
attempt("say the items are at test_set in the manifest", r, m, False)
m["test_set"] = items
attempt("hand the check a manifest with the outside item file copied in as test_set", r, m, False)
r["construction"]["mode"] = "fixed_authored"
attempt("call the construction fixed_authored", r, m, False)
r["construction"]["seed_state"] = "not_applicable"
attempt("say no seed applies", r, m, False)
covered = {x for g in r["dimensions"][0]["groups"] for x in g["members"]}
rest = [i["id"] for i in items if i["id"] not in covered]
for d in r["dimensions"]:
    d["groups"].append({"id": "sha256:" + A.digest(None), "key": None, "members": list(rest)})
attempt("add to every dimension a group keyed null that holds the %d calibration items" % len(rest), r, m, None)
print(json.dumps(steps, ensure_ascii=False))
