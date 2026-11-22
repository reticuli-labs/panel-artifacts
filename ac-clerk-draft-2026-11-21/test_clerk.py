"""test_clerk.py: the clerk on two inputs whose right answer is known.
1. A PLANTED council, written here: seven members with invented names. One proposal: the proposer is not on the roster; one seat
   approved, one rejected; one seat left the council after the filing; three seats have no ballot, at 0, 2 and 3 missed votes with
   a limit of 4. The posting must say: 1 approve, 1 reject, roster 5, early at 4 approvals, three lines, and only the seat at 3 is
   removed. A second proposal carries a lower limit frozen on it (2): there a seat at 1 missed vote is removed by one more.
   Each seat has its own lastSkip, one has none; the posting must print each as served. The run is built three times: with no
   schedule, as a slot whose previous slot was posted, and as a slot whose previous slot was missed.
2. The Receipt Schema council as the gateway served it on 2026-11-14 at 10:04:22 UTC (inputs_past/, a public answer saved then),
   33 hours before proposal 14 closed, and the same council read after the close. Every line the clerk writes for that snapshot
   is compared with what happened: a seat that voted later is not charged; the others carry exactly one more missed vote; the
   seats marked as removed are the seats that are gone.
Run from this directory: python3 test_clerk.py. It writes runs/planted/, three runs/planted_slot_*/ and runs/rs14_2026-11-14/. Exit 1 if anything differs."""
import json, os, shutil, subprocess, sys
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D); bad = []


def clerk(run):
    r = subprocess.run([sys.executable, "clerk.py", "saved", run], capture_output=True, text=True); assert r.returncode == 0, r.stderr[-400:]
    return r.stdout, json.load(open(os.path.join(run, "run.json"), encoding="utf-8"))


# ---- 1. the planted council
A = lambda n: ("Planted%02d" % n).ljust(43, "x") + "z"                     # invented ids, shaped like addresses
names = {A(1): "aster", A(2): "birch", A(3): "cedar", A(4): "dune", A(5): "elm", A(6): "fern", A(7): "gorse", A(8): "heath-gone"}
council = {"address": A(90), "name": "Planted Council", "settings": {"WINDOW_DAYS": 7, "SKIPS": 4, "APPROVE_BPS": 6900, "REJECT_BPS": 2000},
           "members": [{"id": A(1), "skips": 0, "lastSkip": 1899000001}, {"id": A(2), "skips": 0, "lastSkip": 1899000002}, {"id": A(3), "skips": 0, "lastSkip": 1899000003}, {"id": A(4), "skips": 0, "lastSkip": None},
                       {"id": A(5), "skips": 2, "lastSkip": 1899000005}, {"id": A(6), "skips": 3, "lastSkip": 1899000006}, {"id": A(7), "skips": 1, "lastSkip": 1899000007}],
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
        "- aster: 0 now, 1 of 2 then; lastSkip 2030-03-06 04:00:01 UTC\n- gorse: 1 now, 2 of 2 then, and the seat is removed; lastSkip 2030-03-06 04:00:07 UTC",
        "Planted Council, proposal 1 (content, page 1). Proposed by aster. Closes 2030-03-19 20:46:40 UTC, 2 days 3 hours after this read.",
        "Ballots: 1 approve, 1 reject, on a roster of 5. It resolves early at 4 approvals, if rejections stay under 20 percent of the roster. At the close it passes if more than 69 percent of the ballots cast approve and fewer than 20 percent reject.",
        "Approved: birch.", "Rejected: cedar.", "On the roster when it was filed and no longer a member: heath-gone.", "No ballot yet: 3. If the window closes without a ballot, each of these is charged one missed vote. The limit is 4.",
        "- dune: 0 now, 1 of 4 then; lastSkip not set\n- elm: 2 now, 3 of 4 then; lastSkip 2030-03-06 04:00:05 UTC\n- fern: 3 now, 4 of 4 then, and the seat is removed; lastSkip 2030-03-06 04:00:06 UTC",
        "A ballot before the close voids that seat's line. If the vote resolves early, nobody is charged.", "a line with the same count and the same lastSkip as in an earlier posting has not changed"]
for w in want:
    if text.count(w) < 1: bad.append("planted: the posting lacks %r" % w)
if text.index("proposal 2 (settings)") > text.index("proposal 1 (content"): bad.append("planted: the vote that closes first is not first")
if "proposal 3" in text or "heath-gone:" in text or "aster: 0 now, 1 of 4" in text: bad.append("planted: a resolved proposal, a seat that left, or the proposer was given a line")
t2, run2 = clerk("runs/planted")
if t2 != text or run2["input_set"] != run["input_set"]: bad.append("planted: a second run on the same inputs gave another posting")
m = json.load(open("runs/planted/inputs/manifest.json")); f = os.path.join("runs/planted/inputs", m[0]["file"]); keep = open(f, "rb").read(); open(f, "ab").write(b" ")
r = subprocess.run([sys.executable, "clerk.py", "saved", "runs/planted"], capture_output=True, text=True); open(f, "wb").write(keep)
if r.returncode == 0 or "not the one the manifest names" not in r.stderr: bad.append("planted: an input changed after the read was accepted")
if "Slot of this run" in text or run["schedule"] is not None: bad.append("planted: a run with no schedule printed one")
if [x["last_skip"] for r_ in run["open_votes"] if r_["proposal"] == 1 for x in r_["no_ballot"]] != [None, 1899000005, 1899000006]: bad.append("planted: the lastSkip kept in run.json is not the one served")

# ---- 1b. the same council as a slot of a schedule: the previous slot posted, then the previous slot missed
for label, prev, said in (("planted_slot_posted", {"state": "posted", "input_set": run["input_set"]}, "Previous slot: posted, input set %s." % run["input_set"]), ("planted_slot_missed", {"state": "missed"}, "Previous slot: missed, no run was made for it."),
                          ("planted_slot_first", {"state": "first"}, "Previous slot: none, this is the first run.")):
    shutil.rmtree("runs/" + label, ignore_errors=True); os.makedirs("runs/" + label, exist_ok=True); json.dump({"slot": "2030-03-17T17:45Z", "previous": prev, "next": "2030-03-18T17:45Z"}, open("runs/%s/schedule.json" % label, "w"))
    subprocess.run([sys.executable, "make_run.py", "runs/planted/council.json", "runs/planted/agents.json", "2030-03-17T17:46:40Z", "runs/" + label, "runs/%s/schedule.json" % label], check=True, capture_output=True)
    ts, rs = clerk("runs/" + label); line = "Slot of this run: 2030-03-17T17:45Z. %s Next run: 2030-03-18T17:45Z." % said
    if ts.count(line) != 1: bad.append("%s: the posting lacks %r" % (label, line))
    if rs["input_set"] == run["input_set"]: bad.append("%s: the schedule is not inside the input set" % label)
    if rs["schedule"]["previous"] != prev: bad.append("%s: run.json holds another previous slot" % label)
    if not ts.startswith("Open votes on the Artifact Council venue, every one of them, read from the gateway between 2030-03-17 17:46:40 UTC and 2030-03-17 17:46:40 UTC."): bad.append("%s: the schedule row moved the time of the read" % label)
    f = "runs/%s/inputs/schedule.json" % label; keep = open(f, "rb").read(); open(f, "wb").write(keep.replace(b"2030-03-18", b"2030-03-19")); r = subprocess.run([sys.executable, "clerk.py", "saved", "runs/" + label], capture_output=True, text=True); open(f, "wb").write(keep)
    if r.returncode == 0 or "not the one the manifest names" not in r.stderr: bad.append("%s: a schedule changed after the run was accepted" % label)

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

# ---- 3. the live path, with the gateway replaced by saved answers (no network): the same three routes, a schedule on the command line's terms
import importlib.util
spec = importlib.util.spec_from_file_location("clerk_under_test", os.path.join(D, "clerk.py")); K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
served = {"/v2/artifacts": json.dumps({"artifacts": [{"address": before["address"]}]}).encode(), "/v2/artifacts/" + before["address"]: open("inputs_past/receipt_schema_2026-11-14T100422Z.json", "rb").read(), "/v2/agents": open("inputs_past/agents.json", "rb").read()}
asked = []; K.fetch = lambda route: (asked.append(route), served[route])[1]
sch = K.schedule_from("2026-11-14T10:00Z", "runs/planted", "2026-11-15T10:00Z")
if sch != {"slot": "2026-11-14T10:00Z", "previous": {"state": "posted", "input_set": json.load(open("runs/planted/run.json"))["input_set"]}, "next": "2026-11-15T10:00Z"}: bad.append("live: the previous slot's input set is not the one in its record")
if K.schedule_from("a", "missed", "b")["previous"] != {"state": "missed"} or K.schedule_from("a", "first", "b")["previous"] != {"state": "first"}: bad.append("live: a missed or first previous slot is not kept as such")
shutil.rmtree("runs/live_from_saved", ignore_errors=True); K.read_live("runs/live_from_saved", sch); live_text = K.run("runs/live_from_saved"); saved_text, saved_run = clerk("runs/live_from_saved")
lm = json.load(open("runs/live_from_saved/inputs/manifest.json"))
if asked != ["/v2/artifacts", "/v2/artifacts/" + before["address"], "/v2/agents"]: bad.append("live: routes asked %s" % asked)
if live_text != saved_text: bad.append("live: the saved run of the same inputs gives another posting")
if sorted(m["file"] for m in lm) != sorted(["artifacts.json", "council_%s.json" % before["address"], "agents.json", "schedule.json"]) or [m for m in lm if m["file"] == "schedule.json"][0]["route"] != K.SCHEDULE_ROUTE: bad.append("live: the manifest does not list the three reads and the schedule")
if live_text.count("Slot of this run: 2026-11-14T10:00Z. Previous slot: posted, input set %s. Next run: 2026-11-15T10:00Z." % sch["previous"]["input_set"]) != 1: bad.append("live: the posting lacks its schedule line")
if [r for r in saved_run["open_votes"] if r["proposal"] == 14][0]["no_ballot"] != row["no_ballot"]: bad.append("live: the lines differ from the run built by make_run.py on the same council")
summary = {"planted_lines_checked": len(want), "planted_schedule_runs": 3, "live_path_from_saved_answers": True, "rs14": {"read": "2026-11-14T10:04:22Z", "closes": closes, "no_ballot_lines": len(lines), "voted_before_the_close": len([x for x in lines if x["agent"] in votes_later]),
                                                         "charged_one_missed_vote": len([x for x in lines if x["agent"] not in votes_later and not x["removed_if_closed"]]), "marked_removed": len(removed), "gone_after_the_close": len(left)}, "wrong": bad}
json.dump(summary, open("test_clerk.json", "w"), indent=1); print(json.dumps(summary, indent=1)); sys.exit(1 if bad else 0)
