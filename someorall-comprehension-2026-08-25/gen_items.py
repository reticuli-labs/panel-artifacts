#!/usr/bin/env python3
"""some-or-all comprehension original — item set (some-or-all form vs its careful mapping).

Contract operationalization, declared: the two logically independent probes (LOWER: contradicted
if none satisfies? key yes; UPPER: must at least one fail? key no) are encoded as separate items
per scenario, with question polarity counterbalanced (negated variants flip the key). Exact joint
recovery is derivable post-hoc from retained cells (scenario id in strata). Scope: this original
covers the some-or-all form only; some-but-not-all gets its own original. Bare-'some' descriptive
arm omitted (harness is two-arm); declared rather than hidden.
"""
import json, random, hashlib

SEED = 20260825
rng = random.Random(SEED)

# english arm = the proposal's own round-trip mapping, verbatim shape:
# 'some-or-all tests failed' ⇄ 'at least one test failed, and every test may have failed'
# (domain, noun, past, bare, perfect, frame) — explicit verb forms so every probe is grammatical
DOMAINS = [
    ("incident tests", "tests", "failed", "fail", "failed", "the incident retro lists {n} {noun}"),
    ("replicas", "replicas", "lagged behind the primary", "lag behind the primary", "lagged behind the primary", "the cluster page shows {n} {noun}"),
    ("permissions", "service accounts", "held the write scope", "hold the write scope", "held the write scope", "the audit covers {n} {noun}"),
    ("recipients", "recipients", "opened the digest", "open the digest", "opened the digest", "the mailing report covers {n} {noun}"),
    ("alerts", "alerts", "resolved automatically", "resolve automatically", "resolved automatically", "the pager summary lists {n} {noun}"),
    ("inventory", "mirrors", "carried the latest snapshot", "carry the latest snapshot", "carried the latest snapshot", "the storage sheet lists {n} {noun}"),
    ("human situations", "guests", "confirmed attendance", "confirm attendance", "confirmed attendance", "the invitation list has {n} {noun}"),
    ("backups", "archives", "passed verification", "pass verification", "passed verification", "the vault index lists {n} {noun}"),
]
# probe templates: (probe_id, polarity, question_template, key_for_some_or_all)
PROBES = [
    ("lower", "direct",  "Would the message be contradicted if none of the {noun} {pred_past}?", "yes"),
    ("lower", "negated", "Could the message still be true if none of the {noun} {pred_past}?", "no"),
    ("upper", "direct",  "Does the message require that at least one of the {noun} did not {pred_bare}?", "no"),
    ("upper", "negated", "Is the message compatible with every one of the {noun} having {pred_perf}?", "yes"),
]
def morph(past, bare, perf):
    return {"pred_past": past, "pred_bare": bare, "pred_perf": perf}

items = []
# 12 construct-free planted calibration items
for k in range(12):
    dom, noun, pred, _bare, _perf, frame = DOMAINS[k % len(DOMAINS)]
    n = rng.choice([4, 5, 6, 8])
    stated = f"{frame.format(n=n, noun=noun)}; exactly one of the {noun} {pred}."
    omitted = f"{frame.format(n=n, noun=noun)}; how many {noun} {pred} is not stated."
    opts = sorted(["yes", "no", "cannot_tell"], key=lambda _: rng.random())
    items.append({"id": f"cal-soa-{k+1:02d}", "calibration": True,
                  "english": omitted, "ainglish": stated,
                  "question": f"Would the message be contradicted if none of the {noun} {pred}?",
                  "options": opts, "answer": "yes",
                  "strata": {"control": "construct_free_planted_effect", "form": "some-or-all"}})

# 96 real items: 24 scenarios × 4 probe-variants (2 probes × 2 polarities), truth-state alternating
count = 0
for s in range(24):
    dom, noun, pred, bare, perf, frame = DOMAINS[s % len(DOMAINS)]
    n = rng.choice([3, 4, 5, 6, 7, 9])
    truth = "all" if s % 2 == 0 else "some"   # described world; sentence TRUE in both for some-or-all
    m = morph(pred, bare, perf)
    context = frame.format(n=n, noun=noun)
    eng = f"{context}. At least one of the {noun} {pred}, and every one of the {noun} may have {m['pred_perf']}."
    ain = f"{context}. some-or-all {noun} {pred}."
    for probe_id, pol, qt, key in PROBES:
        count += 1
        q = qt.format(noun=noun, **m)
        opts = sorted(["yes", "no", "cannot_tell"], key=lambda _: rng.random())
        items.append({"id": f"real-soa-{count:03d}", "english": eng, "ainglish": ain,
                      "question": q, "options": opts, "answer": key,
                      "strata": {"form": "some-or-all", "scenario": f"s{s+1:02d}", "probe": probe_id,
                                 "polarity": pol, "described_world": truth, "domain": dom}})

reals = [i for i in items if not i.get("calibration")]
doc = {"kind": "ainglish.panel.items.v1",
       "proposal": "some-or-all-some-but-not-all-does-some-leave-room-for-all-2",
       "form": "some-or-all", "baseline": "complete_careful_english",
       "scope_note": "some-or-all form only; two independent probes encoded as separate items (joint recovery derivable from scenario strata); bare-'some' descriptive arm omitted — declared operationalization of the contract within a two-arm harness",
       "real_items": len(reals), "calibration_items": len(items) - len(reals), "items": items}
digest = hashlib.sha256(json.dumps(doc["items"], sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
doc["sha256"] = digest
blob = json.dumps(doc, indent=1, ensure_ascii=False)
open("items.json", "w").write(blob)
print("items:", len(items), "real:", len(reals), "| canonical items sha256:", digest)
for i in items:
    assert i["answer"] in i["options"], i["id"]
    assert "some-or-all" not in i["english"], i["id"]
import collections
print("key balance:", collections.Counter(i["answer"] for i in reals))
print("probe/polarity:", collections.Counter((i["strata"]["probe"], i["strata"]["polarity"]) for i in reals))
