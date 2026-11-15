"""audit_gun_bank.py: read-only, no network, standard library only. Run from anywhere: python3 audit_gun_bank.py
Audits the bank behind my comprehension original 7200b173 on go-unless-no / hold-until-yes, as pinned in this repository
(../go-unless-no-comprehension-2026-08-29/items-as-run.json), for one defect: the question asks for a state of the world and the
key is a concrete state that the messages do not establish.
It checks the pinned digest first, then asserts the four cells, that the abstaining option is offered on every scored item and
keyed on none, and that no item supplies a starting state, a sole-actor rule or a success premise. Exit code 0 means the defect
is present as described; any assertion failure means this description is wrong."""
import hashlib, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(HERE, "..", "go-unless-no-comprehension-2026-08-29", "items-as-run.json"), encoding="utf-8"))
digest = hashlib.sha256(json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
assert digest == "85ed9cd26586f9e57818d195d2a05dc0e86391e985cf963355fab52241799d90", digest      # items_sha256 of the measurement's manifest
real = [i for i in items if not i.get("calibration")]; cal = [i for i in items if i.get("calibration")]
assert (len(real), len(cal)) == (48, 6)
assert {i["question"] for i in items} == {"What is the state of the world now?"}                   # one question, calibration items included
assert all(i["options"][2] == "cannot tell from the message" for i in items)                       # the abstaining option is always offered
assert not [i for i in items if i["answer"].startswith("cannot tell")]                             # and never the key


def cell(i):
    form = "go-unless-no" if "go-unless-no" in i["ainglish"] else "hold-until-yes"; assert ("hold-until-yes" in i["ainglish"]) == (form == "hold-until-yes")
    after = i["ainglish"].split("”", 1)[1]
    did = "sent nothing" if "sent nothing" in after else ("said to proceed" if "telling Avery to proceed" in after else ("objected in time" if "asking Avery not to" in after else "?"))
    return form, did, ("the action is done" if i["options"].index(i["answer"]) == 0 else "nothing has changed")


cells = {}
for i in real: cells[cell(i)] = cells.get(cell(i), 0) + 1
want = {("go-unless-no", "sent nothing", "the action is done"): 12, ("hold-until-yes", "said to proceed", "the action is done"): 12,
        ("go-unless-no", "objected in time", "nothing has changed"): 12, ("hold-until-yes", "sent nothing", "nothing has changed"): 12}
assert cells == want, cells
PREMISE = re.compile(r"only|no one else|nobody else|sole|succeed|success|currently|at present|is still|keeps|did what|did so|then (merged|did)", re.I)
assert not [i["id"] for i in real if PREMISE.search(i["english"]) or PREMISE.search(i["ainglish"])]
print("digest matches the manifest; 48 scored items and 6 calibration items, one question for all 54")
for (form, did, key), n in sorted(cells.items()): print("  %2d  %-15s addressee %-17s keyed: %s" % (n, form, did, key))
print("abstaining option offered on 48, keyed on 0; items that state a starting state, a sole actor or a success: 0")
e = real[0]; print("example %s\n  message: %s\n  options: %s\n  key: %s" % (e["id"], e["ainglish"], e["options"], e["answer"]))
