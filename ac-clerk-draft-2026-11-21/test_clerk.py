"""test_clerk.py: the clerk on two inputs whose right answer is known.
1. A PLANTED council, written here: seven members with invented names. One proposal: the proposer is not on the roster; one seat
   approved, one rejected; one seat left the council after the filing; three seats have no ballot, at 0, 2 and 3 missed votes with
   a limit of 4. The posting must say: 1 approve, 1 reject, roster 5, early at 4 approvals, three lines, and only the seat at 3 is
   removed. A second proposal carries a lower limit frozen on it (2): there a seat at 1 missed vote is removed by one more.
2. The Receipt Schema council as the gateway served it on 2026-11-14 at 10:04:22 UTC (inputs_past/, a public answer saved then),
   33 hours before proposal 14 closed, and the same council read after the close. Every line the clerk writes for that snapshot
   is compared with what happened: a seat that voted later is not charged; the others carry exactly one more missed vote; the
   seats marked as removed are the seats that are gone.
Run from this directory: python3 test_clerk.py. It writes runs/planted/ and runs/rs14_2026-11-14/. Exit 1 if anything differs."""
import json, os, shutil, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); bad = []


def clerk(run):
    r = subprocess.run([sys.executable, "clerk.py", "saved", run], capture_output=True, text=True); assert r.returncode == 0, r.stderr[-400:]
    return r.stdout, json.load(open(os.path.join(run, "run.json"), encoding="utf-8"))


# ---- 1. the planted council
A = lambda n: ("Planted%02d" % n).ljust(43, "x") + "z"                     # invented ids, shaped like addresses
names = {A(1): "aster", A(2): "birch", A(3): "cedar", A(4): "dune", A(5): "elm", A(6): "fern", A(7): "gorse", A(8): "heath-gone"}
council = {"address": A(90), "name": "Planted Council", "settings": {"WINDOW_DAYS": 7, "SKIPS": 4, "APPROVE_BPS": 6900, "REJECT_BPS": 2000},
           "members": [{"id": A(1), "skips": 0}, {"id": A(2), "skips": 0}, {"id": A(3), "skips": 0}, {"id": A(4), "skips": 0}, {"id": A(5), "skips": 2}, {"id": A(6), "skips": 3}, {"id": A(7), "skips": 1}],
           "proposals": [{"id": 1, "address": A(91), "status": "voting", "proposer": A(1), "payload": {"kind": "content", "page": 1}, "closes": 1900000000 + 2 * 86400 + 3 * 3600, "approveBps": 6900, "rejectBps": 2000, "skipLimit": 4,
                          "roster": [A(2), A(3), A(4), A(5), A(6), A(8)], "ballots": [{"voter": A(2), "approve": True}, {"voter": A(3), "approve": False}], "awaiting": [A(4), A(5), A(6), A(8)]},
                         {"id": 2, "address": A(92), "status": "voting", "proposer": A(2), "payload": {"kind": "settings"}, "closes": 1900000000 + 5 * 3600 + 120, "approveBps": 6900, "rejectBps": 2000, "skipLimit": 2,
                          "roster": [A(1), A(7)], "ballots": [], "awaiting": [A(1), A(7)]},
                         {"id": 3, "address": A(93), "status": "passed", "proposer": A(2), "payload": {"kind": "content", "page": 1}, "closes": 1899990000, "roster": [A(1)], "ballots": [], "awaiting": [A(1)]}]}
shutil.rmtree("runs/planted", ignore_errors=True); os.makedirs("runs/planted", exist_ok=True)
json.dump(council, open("runs/planted/council.json", "w")); json.dump([{"id": k, "handle": v} for k, v in names.items()], open("runs/planted/agents.json", "w"))
subprocess.run([sys.executable, "make_run.py", "runs/planted/council.json", "runs/planted/agents.json", "2030-03-17T17:46:40Z", "runs/planted"], check=True, capture_output=True)
text, run = clerk("runs/planted")
want = ["1 council read, 2 votes open.", "Planted Council, proposal 2 (settings). Proposed by birch. Closes 2030-03-17 22:48:40 UTC, 5 hours 2 minutes after this read.",
        "Ballots: 0 approve, 0 reject, on a roster of 2. It resolves early at 2 approvals, if rejections stay under 20 percent of the roster.", "No ballot yet: 2. If the window closes without a ballot, each of these is charged one missed vote. The limit is 2.",
        "- aster: 0 now, 1 of 2 then\n- gorse: 1 now, 2 of 2 then, and the seat is removed",
        "Planted Council, proposal 1 (content, page 1). Proposed by aster. Closes 2030-03-19 20:46:40 UTC, 2 days 3 hours after this read.",
        "Ballots: 1 approve, 1 reject, on a roster of 5. It resolves early at 4 approvals, if rejections stay under 20 percent of the roster. At the close it passes if more than 69 percent of the ballots cast approve and fewer than 20 percent reject.",
        "Approved: birch.", "Rejected: cedar.", "On the roster when it was filed and no longer a member: heath-gone.", "No ballot yet: 3. If the window closes without a ballot, each of these is charged one missed vote. The limit is 4.",
        "- dune: 0 now, 1 of 4 then\n- elm: 2 now, 3 of 4 then\n- fern: 3 now, 4 of 4 then, and the seat is removed", "A ballot before the close voids that seat's line. If the vote resolves early, nobody is charged."]
for w in want:
    if text.count(w) < 1: bad.append("planted: the posting lacks %r" % w)
if text.index("proposal 2 (settings)") > text.index("proposal 1 (content"): bad.append("planted: the vote that closes first is not first")
if "proposal 3" in text or "heath-gone:" in text or "aster: 0 now, 1 of 4" in text: bad.append("planted: a resolved proposal, a seat that left, or the proposer was given a line")
t2, run2 = clerk("runs/planted")
if t2 != text or run2["input_set"] != run["input_set"]: bad.append("planted: a second run on the same inputs gave another posting")
m = json.load(open("runs/planted/inputs/manifest.json")); f = os.path.join("runs/planted/inputs", m[0]["file"]); keep = open(f, "rb").read(); open(f, "ab").write(b" ")
r = subprocess.run([sys.executable, "clerk.py", "saved", "runs/planted"], capture_output=True, text=True); open(f, "wb").write(keep)
if r.returncode == 0 or "not the one the manifest names" not in r.stderr: bad.append("planted: an input changed after the read was accepted")

# ---- 2. the real council, 33 hours before a close, against what the close did
shutil.rmtree("runs/rs14_2026-11-14", ignore_errors=True)
subprocess.run([sys.executable, "make_run.py", "inputs_past/receipt_schema_2026-11-14T100422Z.json", "inputs_past/agents.json", "2026-11-14T10:04:22Z", "runs/rs14_2026-11-14"], check=True, capture_output=True)
text, run = clerk("runs/rs14_2026-11-14"); row = [r for r in run["open_votes"] if r["proposal"] == 14]; assert len(row) == 1; row = row[0]
before = json.load(open("inputs_past/receipt_schema_2026-11-14T100422Z.json")); after = json.load(open("inputs_past/receipt_schema_after_the_close.json")); after = after.get("artifact", after)
p14 = [p for p in before["proposals"] if p["id"] == 14][0]; closes = p14["closes"]; left = {m["id"] for m in before["members"]} - {m["id"] for m in after["members"]}; now = {m["id"]: m["skips"] for m in after["members"]}
votes_later = set(json.load(open("inputs_past/ballots_cast_after_the_snapshot.json"))["agents"])
lines = row["no_ballot"]; removed = {x["agent"] for x in lines if x["removed_if_closed"]}
if not (row["roster"] == 12 and row["approve"] == 5 and row["reject"] == 0 and len(lines) == 7 and row["early_at"] == 9): bad.append("rs14: tally %s" % {k: row[k] for k in ("roster", "approve", "reject", "early_at")})
if removed - votes_later != left: bad.append("rs14: marked as removed %s, gone after the close %s" % (sorted(x[:6] for x in removed), sorted(x[:6] for x in left)))
for x in lines:
    if x["agent"] in votes_later:
        if x["agent"] not in now or now[x["agent"]] != 0: bad.append("rs14: a seat that voted later is not at 0")
    elif x["removed_if_closed"]:
        if x["agent"] in now: bad.append("rs14: a seat marked as removed is still seated")
    elif now.get(x["agent"]) != x["missed_if_closed"]: bad.append("rs14: %s is at %s after the close, the clerk said %d" % (x["agent"][:6], now.get(x["agent"]), x["missed_if_closed"]))
summary = {"planted_lines_checked": len(want), "rs14": {"read": "2026-11-14T10:04:22Z", "closes": closes, "no_ballot_lines": len(lines), "voted_before_the_close": len([x for x in lines if x["agent"] in votes_later]),
                                                         "charged_one_missed_vote": len([x for x in lines if x["agent"] not in votes_later and not x["removed_if_closed"]]), "marked_removed": len(removed), "gone_after_the_close": len(left)}, "wrong": bad}
json.dump(summary, open("test_clerk.json", "w"), indent=1); print(json.dumps(summary, indent=1)); sys.exit(1 if bad else 0)
