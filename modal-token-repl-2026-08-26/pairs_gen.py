#!/usr/bin/env python3
"""Fresh complete pairs for three independent token_delta replications (Reticuli, 2026-08-26).
No tokenizer import: pairs are frozen before any tokenizer loads. Every English and Ainglish surface
is asserted absent from every prior token manifest on its row (prior-surfaces.json, fetched live)."""
import json, hashlib, sys
PRIOR = json.load(open("prior-surfaces.json"))

def freeze(name, kind, replicates, pairs, forms):
    surf = set(s.strip() for s in PRIOR[name])
    seen = set()
    for p in pairs:
        for k in ("english", "ainglish"):
            assert p[k] not in seen, ("duplicate", p[k]); seen.add(p[k])
            assert p[k].strip() not in surf, ("collides with a prior surface", p[k])
        assert p["form"] in forms
    for f in forms:
        assert sum(1 for p in pairs if p["form"] == f) == len(pairs) // len(forms), f
    doc = {"kind": kind, "replicates_hash": replicates, "pairs": pairs}
    blob = json.dumps(doc, indent=1, ensure_ascii=False)
    open(f"{name}-pairs.json", "w").write(blob)
    print(f"{name}: {len(pairs)} pairs frozen, sha256 {hashlib.sha256(blob.encode()).hexdigest()}")

# ---------- may-as (replicates 285d9436…; controls per the original: "is permitted to" / "might") ----------
PERM = [("The reconciliation job", "purge orphaned invoices"), ("The night auditor", "reopen a closed shift"),
        ("The onboarding bot", "grant read-only access"), ("The release manager", "skip the canary stage"),
        ("The intake service", "reject malformed uploads"), ("The custodian", "unlock the cold vault"),
        ("The dispatcher", "reassign an idle courier"), ("The proxy", "cache authenticated responses"),
        ("The moderator", "hide a flagged reply"), ("The build agent", "retag a failed image"),
        ("The registrar", "merge duplicate accounts"), ("The relay", "drop unsigned packets"),
        ("The librarian", "recall an overdue volume"), ("The treasurer", "advance the quarterly float"),
        ("The sentinel", "quarantine a noisy host"), ("The steward", "reprice the idle capacity")]
POSS = [("The nightly sweep", "miss a renamed bucket"), ("The upstream feed", "repeat yesterday's rows"),
        ("The lease", "expire during the handover"), ("The thaw", "flood the lower archive"),
        ("The rollback", "strand an in-flight order"), ("The courier", "arrive before the gate opens"),
        ("The sensor", "drift past its calibration band"), ("The mirror", "serve a truncated index"),
        ("The vendor", "rotate the endpoint without notice"), ("The queue", "reorder the ballots"),
        ("The forecast", "understate the evening load"), ("The parser", "swallow the final record"),
        ("The heater", "trip the shared breaker"), ("The referee", "overrun the review window"),
        ("The fork", "diverge on the shared index"), ("The dry run", "mask a permission gap")]
mayas = [{"form": "may-as-permission", "english": f"{s} is permitted to {v}.", "ainglish": f"{s} may-as-permission {v}."} for s, v in PERM] + \
        [{"form": "may-as-possibility", "english": f"{s} might {v}.", "ainglish": f"{s} may-as-possibility {v}."} for s, v in POSS]
freeze("mayas", "modal-token-replication.pairs.v1", "285d943697fc1567fc3c3d00ffd160942226b712aee71ed244f16829b8601e7e", mayas, ["may-as-permission", "may-as-possibility"])

# ---------- may-not (replicates d7de3899…; complete careful mappings in my own wording) ----------
SUBJ = [("the courier", "enter the depot after dark"), ("the intern", "sign the vendor contract"),
        ("the night crew", "restart the furnace"), ("the visiting auditor", "photograph the ledgers"),
        ("the pilot", "taxi across the closed runway"), ("the tenant", "sublet the storage cage"),
        ("the trainee", "operate the crane alone"), ("the contractor", "cut the marked cable"),
        ("the guest account", "export the member list"), ("the junior clerk", "approve its own expense"),
        ("the volunteer", "handle the sealed evidence"), ("the mirror node", "accept external writes"),
        ("the substitute", "alter the seating plan"), ("the apprentice", "fire the kiln unattended"),
        ("the field team", "bypass the checkpoint"), ("the caretaker", "sell the surplus timber")]
SUBJ2 = [("the ferry", "sail on the morning tide"), ("the backup", "finish before the cutover"),
         ("the witness", "attend the second hearing"), ("the shipment", "clear customs by Friday"),
         ("the patch", "reach the older kiosks"), ("the reservoir", "refill before the dry season"),
         ("the delegate", "return for the final vote"), ("the cache", "warm before the launch"),
         ("the survey crew", "reach the northern plots"), ("the settlement", "post before the ledger closes"),
         ("the tenant's cheque", "clear this week"), ("the relief driver", "cover the late route"),
         ("the second engine", "start on the first attempt"), ("the archive scan", "complete overnight"),
         ("the replacement valve", "arrive with the next convoy"), ("the choir", "perform on the closing night")]
def cap(s): return s[0].upper() + s[1:]
maynot = [{"form": "may-not-as-prohibition",
           "english": f"An applicable rule forbids this: {s} will {v}; it predicts nothing about what actually happens and claims nothing about physical possibility.",
           "ainglish": f"{cap(s)} may-not-as-prohibition {v}."} for s, v in SUBJ] + \
         [{"form": "may-not-as-possibility",
           "english": f"On the speaker's current evidence it remains possible that this will not happen: {s} will {v}; no rule is stated and no permission is granted.",
           "ainglish": f"{cap(s)} may-not-as-possibility {v}."} for s, v in SUBJ2]
freeze("maynot", "modal-token-replication.pairs.v1", "d7de3899b7531fd0c5bf941099772b4cb56bc91f9ff5689352948dbaca9a235b", maynot, ["may-not-as-prohibition", "may-not-as-possibility"])

# ---------- must (replicates f103aba3…) ----------
RULE = [("the courier", "sign for every parcel"), ("the intern", "log each call"), ("the night crew", "vent the furnace hourly"),
        ("the auditor", "seal the sampled boxes"), ("the pilot", "file the alternate plan"), ("the tenant", "insure the storage cage"),
        ("the trainee", "wear the harness"), ("the contractor", "tag every live cable"), ("the guest account", "rotate its token daily"),
        ("the clerk", "countersign the refund"), ("the volunteer", "return the badge at close"), ("the mirror node", "verify each checkpoint"),
        ("the substitute", "follow the seating plan"), ("the apprentice", "record the kiln temperature"), ("the field team", "radio in at noon"),
        ("the caretaker", "inventory the timber monthly")]
INF = [("the ferry", "left on the morning tide"), ("the backup", "finished before the cutover"), ("the witness", "attended the second hearing"),
       ("the shipment", "cleared customs early"), ("the patch", "reached the older kiosks"), ("the reservoir", "refilled overnight"),
       ("the delegate", "returned for the final vote"), ("the cache", "warmed before the launch"), ("the survey crew", "reached the northern plots"),
       ("the settlement", "posted before the close"), ("the cheque", "cleared on Monday"), ("the relief driver", "covered the late route"),
       ("the second engine", "started on the first try"), ("the archive scan", "completed overnight"), ("the valve", "arrived with the convoy"),
       ("the choir", "performed on the closing night")]
def past_to_have(v):  # "left on…" -> "have left on…"
    return "have " + v
must = [{"form": "must-as-rule",
         "english": f"An applicable rule requires {s} to {v}; this does not assert that it happens, and failing to do so is noncompliance.",
         "ainglish": f"{cap(s)} must-as-rule {v}."} for s, v in RULE] + \
       [{"form": "must-as-inference",
         "english": f"From the available evidence the speaker concludes that {s} {v}; this states a conclusion and creates no duty.",
         "ainglish": f"{cap(s)} must-as-inference {past_to_have(v)}."} for s, v in INF]
freeze("must", "modal-token-replication.pairs.v1", "f103aba371e9c0213fad29f30e614a55608d58ec1709c24821c6547785298f70", must, ["must-as-rule", "must-as-inference"])
