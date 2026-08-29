"""go-unless-no / hold-until-yes comprehension panel, built to the design preregistered in the
proposal's predicted_measurement BEFORE any reader saw an item:
  48 items, form-balanced (24 go-unless-no, 24 hold-until-yes), each form crossed 12 silent /
  12 replying, so the TRIGGER is tested and not only the silence.
  Held-out question rule: the question asks a consequence whose answer vocabulary appears in
  neither arm; outcome text is disjoint from the action verb and from go/no/yes/hold/silence/consent.
  English arm = the filing's english_mapping applied verbatim. Ainglish arm = the marker.
"""
import json, re, hashlib

MAPPING_GO   = 'I will {act} at {t} unless you tell me not to before {t}; if I hear nothing from you by {t}, I will treat that as consent and proceed.'
MAPPING_HOLD = 'I will not {act} until you explicitly tell me to go ahead; if I hear nothing from you, I will not proceed.'
BARE = ['let me know if you have concerns.', 'please confirm.', 'thoughts?', "I'll proceed unless I hear otherwise.", 'shout if this is wrong.', 'waiting on your go-ahead.']

# (verb-phrase, state-if-done, state-if-not-done). Outcome text deliberately avoids the action verb
# and the words go/no/yes/hold/silence/consent.
ACTIONS = [
 ("merge PR 330",              "PR 330 is closed and its commits are on master", "PR 330 remains open"),
 ("publish the v2 changelog",  "the v2 changelog is reachable at its live URL",  "the v2 changelog exists only as a draft"),
 ("rotate the signing key",    "the registry lists a fresh fingerprint",         "the registry lists the previous fingerprint"),
 ("archive the Q3 dataset",    "the Q3 dataset sits in cold storage",            "the Q3 dataset sits in the working bucket"),
 ("cancel the vendor contract","the vendor relationship has ended",              "the vendor relationship continues"),
 ("deploy build 41",           "the production host answers as build 41",        "the production host answers as build 40"),
 ("delete the stale branch",   "the branch is absent from the remote",           "the branch is present on the remote"),
 ("send the investor update",  "the update sits in the investors' inboxes",      "the update sits in the drafts folder"),
 ("lock the pricing page",     "the pricing page rejects edits",                 "the pricing page accepts edits"),
 ("restore the 02:00 snapshot","the database contents match the 02:00 state",    "the database contents match this morning's state"),
 ("revoke Dana's token",       "Dana's token fails authentication",              "Dana's token still authenticates"),
 ("mint the release tag",      "the tag resolves on the remote",                 "the remote lacks that tag"),
 ("transfer the domain",       "the domain sits in the new registrar account",   "the domain sits in the former registrar account"),
 ("purge the CDN cache",       "visitors receive freshly generated pages",       "visitors receive stored copies"),
 ("close the funding round",   "the cap table marks the round final",            "the cap table marks the round open"),
 ("disable the legacy endpoint","requests to the legacy path receive an error",  "requests to the legacy path receive data"),
 ("hand the pager to Wren",    "the alerts reach Wren",                          "the alerts continue reaching Rafi"),
 ("freeze the item set",       "the item set carries an immutable digest",       "the item set remains editable"),
 ("anonymise the survey export","the export omits participant names",            "the export includes participant names"),
 ("block out the maintenance window","the calendar shows that hour unavailable",  "the calendar shows that hour free"),
 ("escalate the incident to sev-1","the incident carries a sev-1 label",         "the incident carries a sev-2 label"),
 ("execute the partnership letter","the letter bears both parties' marks", "the letter bears one party's mark"),
 ("retire the beta flag",      "every user receives the new behaviour",          "only opted-in users receive the new behaviour"),
 ("wipe the test tenant",      "the test tenant is empty",                       "the test tenant keeps its previous records"),
]
DEADLINES = ["17:00 on Friday","09:00 on Monday","noon on Wednesday","18:30 on Thursday","08:00 on Tuesday","15:00 on Friday"]
BANNED = ["go","no","yes","hold","silence","consent"]

def scenario(act, marker_or_mapping, behaviour, t):
    return (f"Avery wrote to Blake: “{marker_or_mapping}” {behaviour} It is now after {t}.")

def build():
    items=[]; idx=0
    for k,(act, done, notdone) in enumerate(ACTIONS):
        t = DEADLINES[k % len(DEADLINES)]
        # actions 0-11: go+SILENT and hold+REPLYING ; actions 12-23: go+REPLYING and hold+SILENT
        go_silent = k < 12
        for form in ("go-unless-no","hold-until-yes"):
            idx += 1
            if form == "go-unless-no":
                silent = go_silent
                ain = f"{act}, go-unless-no({t})."
                eng = MAPPING_GO.format(act=act, t=t)
                beh = "Blake sent nothing before that time." if silent else f"Blake replied well before {t} asking Avery not to."
                answer = done if silent else notdone          # silence = consent -> proceeds
            else:
                silent = not go_silent
                ain = f"{act}, hold-until-yes."
                eng = MAPPING_HOLD.format(act=act)
                beh = "Blake sent nothing at all." if silent else "Blake replied telling Avery to proceed."
                answer = notdone if silent else done          # silence = not authorised -> does not proceed
            items.append({
                "id": f"gun-{idx:02d}",
                "form": form, "behaviour": "silent" if silent else "replying",
                "english":  scenario(act, eng, beh, t),
                "ainglish": scenario(act, ain, beh, t),
                "question": "What is the state of the world now?",
                "options": [done, notdone, "cannot tell from the message"],
                "answer": answer,
            })
    # calibration: information present only in the marked arm (planted effect), bare English beside it
    cal=[]
    for j,(act, done, notdone) in enumerate(ACTIONS[:6]):
        t = DEADLINES[j % len(DEADLINES)]
        cal.append({
            "id": f"cal-{j+1}", "calibration": True, "form": "calibration", "behaviour": "silent",
            "english":  scenario(act, f"{act}. {BARE[j]}", "Blake sent nothing.", t),
            "ainglish": scenario(act, f"{act}, go-unless-no({t}).", "Blake sent nothing.", t),
            "question": "What is the state of the world now?",
            "options": [done, notdone, "cannot tell from the message"],
            "answer": done,
        })
    return cal + items

def bare_variant(items):
    """Third descriptive arm: same scenarios, real bare-English closings instead of the mapping."""
    out=[]
    for i,it in enumerate(items):
        if it.get("calibration"): continue
        act = it["english"].split("“")[1].split(" at ")[0].replace("I will not ","").replace("I will ","")
        b = BARE[i % len(BARE)]
        tail = it["english"].split("”",1)[1]
        o=dict(it); o["id"]=it["id"]+"-bare"
        o["english"]=f"Avery wrote to Blake: “{act}. {b}”{tail}"
        out.append(o)
    return out

if __name__=="__main__":
    items=build()
    sci=[i for i in items if not i.get("calibration")]
    assert len(sci)==48, len(sci)
    from collections import Counter
    print("form x behaviour:", Counter((i["form"],i["behaviour"]) for i in sci))
    # HELD-OUT VOCABULARY CHECK — programmatic, not eyeballed
    bad=[]
    for i in sci:
        verb = i["ainglish"].split("“")[1].split(",")[0].split()[0].lower()
        for opt in i["options"][:2]:
            o=opt.lower()
            if re.search(rf"\b{re.escape(verb)}", o): bad.append((i["id"],"verb",verb,opt))
            for w in BANNED:
                if re.search(rf"\b{w}\b", o): bad.append((i["id"],"banned",w,opt))
    print("vocabulary violations:", len(bad))
    for b in bad[:12]: print("   ", b)
    answers=Counter(("done" if i["answer"]==i["options"][0] else "notdone") for i in sci)
    print("answer balance:", answers)
    json.dump(items, open("gun_panel_items.json","w"), indent=1, ensure_ascii=False)
    json.dump(bare_variant(items), open("gun_panel_bare.json","w"), indent=1, ensure_ascii=False)
    print("items_sha256:", hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16])
    print("\nSAMPLE go+silent:"); print("  ENG:", sci[0]["english"][:200]); print("  AIN:", sci[0]["ainglish"][:200]); print("  ANS:", sci[0]["answer"])
    print("SAMPLE hold+replying:"); print("  AIN:", sci[1]["ainglish"][:200]); print("  ANS:", sci[1]["answer"])
