#!/usr/bin/env python3
"""Fresh-input REPLICA bank for Dexagon's send-snapshot / grant-live-view comprehension original 09cd9ef3.
DESIGN IDENTICAL to dexagon-ai/ainglish-evidence send-snapshot-live-view-comprehension-v1-2026-09-03/build.py:
144 rows = 6 domains x 4 consequence events x 3 probe classes x 2 forms; four options = implementation pole x
consequence/boundary pole; answer position rotated by row; twelve form-by-domain settlement strata; eight
construct-free three-option controls. COMPARATOR PRESERVED: the careful-English instruction texts and the option
vocabulary are Dexagon's verbatim templates (they are the comparator and the probe). INPUTS FRESH: new domains,
object names, recipients, version scheme, shared-context phrasing, and new controls. No inference, no network."""
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SLUG = "send-snapshot-version-ref-to-recipient-grant-live-view"
DOMAINS = [
    ("design brief", "launch-brief", "Tamsin"),
    ("ledger export", "quarter-ledger", "Ulric"),
    ("model checkpoint", "ranker-weights", "Vesna"),
    ("status board", "release-board", "Wendel"),
    ("audio recording", "briefing-audio", "Xiomara"),
    ("access policy", "vendor-access-policy", "Yusuf"),
]
EVENTS = ("source-edit", "source-deletion", "grant-revocation", "later-read")
PROBES = ("core", "authority-boundary", "evidence-boundary")
def canonical(v): return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
def rotate(values, offset):
    offset %= len(values); return values[offset:] + values[:offset]
def place_answer(values, answer, position): return rotate(values, values.index(answer) - position)
def event_context(event, obj, version, nxt):
    return {"source-edit": f"Afterwards the source copy of {obj} is revised: {version} becomes {nxt}.",
            "source-deletion": f"Afterwards the source copy of {obj} is removed from the service that holds it.",
            "grant-revocation": f"Afterwards the recipient's access to the source copy of {obj} is withdrawn.",
            "later-read": f"When the source copy of {obj} is next opened, it holds {nxt}, no longer {version}."}[event]
def consequence_options(event, probe, version, nxt):
    if probe == "authority-boundary":
        return ("no edit or redistribution right follows, and a separately authorised copy is unaffected",
                "edit and redistribution rights follow, and every separately authorised copy is erased")
    if probe == "evidence-boundary":
        return ("the instruction alone proves no later receipt, retention, opening, or service-reachability event",
                "the instruction itself proves receipt, retention, opening, and service reachability")
    return {"source-edit": (f"the recipient-visible content stays at {version}", f"a successful later read shows the current {nxt} contents"),
            "source-deletion": ("the delivered and retained representation remains available after source deletion", "future access through the source-backed permission cannot retrieve the deleted object"),
            "grant-revocation": ("the delivered and retained representation remains available after source access is revoked", "future access through the revoked permission is denied"),
            "later-read": (f"opening the retained representation shows {version}", f"a successful read dereferences the canonical object and shows {nxt}")}[event]
def answer_options(event, probe, form, version, nxt):
    snap_c, live_c = consequence_options(event, probe, version, nxt)
    exp_impl = "snapshot" if form == "send-snapshot" else "live-view"
    exp_cons = "snapshot" if probe == "core" and form == "send-snapshot" else "live-view" if probe == "core" else "conservative"
    conseq = [("conservative", snap_c), ("overclaim", live_c)] if probe != "core" else [("snapshot", snap_c), ("live-view", live_c)]
    impls = [("snapshot", "transmit an independent representation of the named frozen version"), ("live-view", "grant revocable read-only access to the canonical object")]
    options, comps, answer = [], {}, ""
    for impl, itext in impls:
        for cons, ctext in conseq:
            o = f"Implementation: {itext}. Consequence or boundary: {ctext}."
            options.append(o); comps[o] = {"implementation": impl, "consequence": cons, "implementation_correct": impl == exp_impl, "consequence_correct": cons == exp_cons}
            if impl == exp_impl and cons == exp_cons: answer = o
    assert answer; return options, answer, comps
def scientific_items():
    items, row = [], 0
    for di, (domain, obj, rcpt) in enumerate(DOMAINS, 1):
        for ei, event in enumerate(EVENTS, 1):
            for pi, probe in enumerate(PROBES, 1):
                version, nxt = f"rev-{di}{ei}{pi}", f"rev-{di}{ei}{pi + 4}"
                common = f"The {domain} in question is the canonical {obj}. " + event_context(event, obj, version, nxt)
                if probe == "core": common += " Assume that a fixed transfer, if made, was delivered and retained, and that a live grant, if made, is the recipient's only route to the object, with no separate copy."
                elif probe == "authority-boundary": common += " The recipient separately holds a copy obtained under a different authority; the instruction is silent on editing and redistribution."
                else: common += " There is no delivery receipt, no record of the object being opened, and no reachability check for the service."
                careful_snapshot = (f"Instruction: send {rcpt} an independent fixed representation of exactly {obj} {version}. Do not grant continuing access to the source. Later source changes, deletion, or revocation cannot alter or withdraw a delivered and retained representation. Sending does not itself prove receipt.")
                careful_live = (f"Instruction: grant {rcpt} a revocable read-only capability to the stable canonical object {obj}. Each successful read shows its then-current contents. Do not intentionally transfer a durable independent copy. This grants no edit or redistribution right and does not prove that the object was opened.")
                for form, careful, marked in (("send-snapshot", careful_snapshot, f"Instruction: send-snapshot({obj}@{version}, to={rcpt})."),
                                              ("grant-live-view", careful_live, f"Instruction: grant-live-view({obj}, to={rcpt}).")):
                    row += 1
                    options, answer, comps = answer_options(event, probe, form, version, nxt)
                    items.append({"id": f"rt-snapshot-live-{row:03d}", "scenario_id": f"rt-snapshot-live-scenario-{row:03d}",
                                  "english": common + " " + careful, "ainglish": common + " " + marked,
                                  "question": "Answer both questions by choosing the one option with both answers correct. (1) Which implementation satisfies the instruction? (2) What later consequence or authority/evidence boundary follows?",
                                  "questions": ["Which implementation satisfies the instruction?", "What later consequence or authority/evidence boundary follows?"],
                                  "options": place_answer(options, answer, (row - 1) % 4), "answer": answer, "option_components": comps,
                                  "settlement_stratum": f"{form}-{di}", "report_cell": f"{form}-{di}-{event}",
                                  "strata": {"form": form, "domain": domain, "event": event, "probe": probe}})
    return items
def calibration_items():
    rows = [("owner", "Either Bram or Cato owns the failover drill.", "Bram, not Cato, owns the failover drill.", "Who owns the failover drill?", ["Cato", "cannot tell", "Bram"], "Bram"),
            ("region", "The warm standby is in either Tallinn or Lima.", "The warm standby is in Lima, not Tallinn.", "Where is the warm standby?", ["Tallinn", "Lima", "cannot tell"], "Lima"),
            ("state", "The certificate is either valid or revoked.", "The certificate is revoked, not valid.", "What is the certificate state?", ["cannot tell", "revoked", "valid"], "revoked"),
            ("cause", "Either a clock skew or a missing index caused the timeout.", "A clock skew, not a missing index, caused the timeout.", "What caused the timeout?", ["a missing index", "a clock skew", "cannot tell"], "a clock skew"),
            ("order", "The amber build ran either before or after the teal build.", "The amber build ran before, not after, the teal build.", "When did the amber build run?", ["before", "cannot tell", "after"], "before"),
            ("count", "The manifest lists either nine or fourteen entries.", "The manifest lists nine entries, not fourteen.", "How many entries are listed?", ["fourteen", "nine", "cannot tell"], "nine"),
            ("actor", "Either Dov or Ezri approved the rollout.", "Ezri, not Dov, approved the rollout.", "Who approved the rollout?", ["cannot tell", "Dov", "Ezri"], "Ezri"),
            ("colour", "The badge is either olive or maroon.", "The badge is olive, not maroon.", "What colour is the badge?", ["olive", "maroon", "cannot tell"], "olive")]
    return [{"id": f"rt-snapshot-live-cal-{i:02d}", "english": cold, "ainglish": planted, "question": q, "options": opts, "answer": ans,
             "calibration": True, "calibration_scope": "target-independent", "strata": {"control": name}} for i, (name, cold, planted, q, opts, ans) in enumerate(rows, 1)]
if __name__ == "__main__":
    sci, ctl = scientific_items(), calibration_items()
    assert len(sci) == 144 and len(ctl) == 8 and len({i["id"] for i in sci + ctl}) == 152
    assert all(sum(i["strata"]["form"] == f for i in sci) == 72 for f in ("send-snapshot", "grant-live-view"))
    assert len({i["settlement_stratum"] for i in sci}) == 12 and len({i["report_cell"] for i in sci}) == 48
    items = sci + ctl; d = hashlib.sha256(canonical(items)).hexdigest()
    (ROOT / "items.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"scientific": 144, "calibration": 8, "items_sha256": d}))
