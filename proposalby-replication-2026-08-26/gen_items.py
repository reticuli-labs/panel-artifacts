#!/usr/bin/env python3
"""Fresh-input replication of Dexagon's proposal-by comprehension original 591db40e… (−37.5 pp).
Estimand retained exactly: careful-English paraphrase (his fixed template) vs `proposal-by(<role>): <action>.`,
four context variants (senior-role sentence / 'everyone voiced support' / 'a different earlier course remains
operative' / no context), the same three-part profile question and five-option set with the key
'offered / no / no' throughout, key positions balanced. Fresh roles and actions, every surface asserted
absent from the original's 54 items. Controls mirror his design: an undeterminable one-line status (cold)
vs the marker — the cold default ('cannot tell / cannot tell / cannot tell') is not the planted key."""
import json, hashlib, collections
ORIG = json.load(open("original-items.json")); orig_items = ORIG.get("items") or ORIG
orig_texts = {x[k].strip().casefold() for x in orig_items for k in ("english", "ainglish")}
TAIL = (" has put the option to {action} forward for consideration. This identifies who offered it and asserts that the option "
        "exists, but asserts no operative selection, authorization, promise, or schedule. This sentence neither commands the reader nor grants permission.")
CTX = {0: "{Role} holds the senior role named here. ", 1: "Everyone present voiced support. ", 2: "A different earlier course remains the operative choice. ", 3: ""}
ROLES = ["Payments Lead", "Data Protection Officer", "Head of Support", "Site Reliability Manager", "Localisation Lead", "Procurement Manager",
         "Mobile Team Lead", "Compliance Analyst", "Content Editor", "Network Engineer", "Growth Marketer", "Warehouse Supervisor"]
ACTIONS = ["retire the legacy invoice format", "pause the weekly digest", "move the standup to nine", "archive the pilot repository",
           "switch the CDN provider", "extend the trial to sixty days", "rename the internal wiki", "freeze feature branches for a week",
           "publish the retrospective", "cap uploads at two gigabytes", "shorten the on-call rotation", "migrate the ticket queue",
           "reopen the beta programme", "drop support for the old client", "hold the vendor review on Thursday", "split the monolith deploy",
           "reissue the badge printers", "change the default locale", "run the audit in October", "merge the two dashboards",
           "close the legacy mailbox", "trial the four-day week", "pin the compiler version", "increase the fraud threshold",
           "outsource the night shift", "translate the terms of service", "sunset the affiliate program", "rotate the API keys quarterly",
           "consolidate the test suites", "delay the price change", "add a second approver", "replace the office router",
           "adopt the new logo", "record all support calls", "bring the launch forward", "rewrite the onboarding email",
           "move backups to the new region", "allow contractors on the VPN", "lower the free tier limit", "standardise the meeting notes",
           "cancel the Friday build", "start the pilot in March", "double the retry budget", "require two-factor for admins",
           "open the API to partners", "remove the signup captcha", "reprint the safety posters", "repaint the loading bay"]
assert len(ACTIONS) == 48 and len(set(ACTIONS)) == 48
OPTS = ["offered / no / no", "selected / yes / no", "invalid source / no / no", "selected / yes / yes", "cannot tell / cannot tell / cannot tell"]
Q = ("Choose the three-part profile that follows from the message. Part 1: is the action only offered for consideration, operatively selected, "
     "invalid because the named source lacks standing, or impossible to determine? Part 2: may the record state that an existing choice has been made? "
     "Part 3: does this sentence itself command the reader or grant permission?")
items = []
for i, action in enumerate(ACTIONS):
    role = ROLES[i % 12]; variant = i % 4; ctx = CTX[variant].format(Role=role)
    eng = ctx + role + TAIL.format(action=action)
    ain = ctx + f"proposal-by({role.lower()}): {action}."
    rot = i % 5; opts = OPTS[rot:] + OPTS[:rot]
    items.append({"id": f"rep-pb-{i+1:02d}", "english": eng, "ainglish": ain, "question": Q, "options": opts, "answer": OPTS[0],
                  "strata": {"form": "proposal", "baseline": "careful", "condition": f"proposal_variant_{variant}", "domain": "operational", "answer_position": rot}})
CAL_ACTIONS = ["rotate the stage lighting", "close the west car park", "reprint the menu cards", "swap the choir rehearsal night", "reseed the cricket square", "relabel the archive boxes"]
for j, action in enumerate(CAL_ACTIONS):
    eng = (f"A one-line status about whether to {action} was received, but the available note does not reveal whether the course was merely floated "
           "or operatively selected, whether an existing choice may be recorded, or whether the sentence had directive force.")
    ain = f"proposal-by(replication control {j+1}): {action}."
    rot = j % 5; opts = OPTS[rot:] + OPTS[:rot]
    items.append({"id": f"rep-pb-cal-{j+1:02d}", "calibration": True, "english": eng, "ainglish": ain, "question": Q, "options": opts, "answer": OPTS[0]})
for it in items:
    for k in ("english", "ainglish"): assert it[k].strip().casefold() not in orig_texts, ("collides with the original", it["id"], k)
real = [x for x in items if not x.get("calibration")]
assert collections.Counter(x["strata"]["condition"] for x in real) == {f"proposal_variant_{v}": 12 for v in range(4)}
assert sorted(collections.Counter(x["options"].index(x["answer"]) for x in real).values()) == [9, 9, 10, 10, 10], "key positions must be balanced like the original (10/10/10/9/9)"
def canon(items): return hashlib.sha256(json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
env = {"kind": "ainglish.panel.items.v1", "proposal": "proposal-by-p-decision-by-a-say-whether-an-option-is-offered", "form": "proposal-by(<P>): <X> | decision-by(<A>): <X>",
       "comparator": "complete careful-English paraphrase (the original's estimand; proposal-by form only)", "replicates_hash": "591db40ea263a21e1922f78d9bbfa4342637701c7e29126cbca13f8d7fd123ae",
       "scope_note": "Fresh-input replication of Dexagon's original 591db40e (proposal-by only, careful paraphrase vs marker, three-part profile). 48 fresh role/action scenarios across the same four context variants, key positions balanced 10/10/10/9/9 as in the original; every surface asserted absent from the original's 54 items. Note for the record: like the original, every real item's key is 'offered / no / no' — the estimand the replication retains; a constant responder would ace it, which the calibration (cold default 'cannot tell') and the reported arms make visible rather than hide.",
       "sha256": canon(items), "items": items}
open("items.json", "w").write(json.dumps(env, indent=1, ensure_ascii=False))
print("proposal-by replication set: 48 real + 6 cal, sha", env["sha256"][:12])
