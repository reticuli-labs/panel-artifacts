import json
v4 = json.load(open("/home/user/claude-projects/Reticuli/panel-artifacts/comparator-class-2026-09-13/amend_payload_v4.json"))
p = json.loads(json.dumps(v4))
def R(s, a, b):
    assert a in s, a[:70]; return s.replace(a, b)
FORM = ("claim_carrier entries may be {metric: comprehension_accuracy_delta, comparator: bare|careful, exposure: cold|entry, "
        "corpus: sha256, rule: {threshold, background: sha256, order, exclude}}. bare carries only from a bare arm recovered "
        "from that content-addressed corpus under that rule. Rejected at write: a manifest lacking the corpus address; a rule "
        "missing any of the four keys (non-recoverable); a mint citing another address. Other class: diagnostics.expansion_cost, "
        "carrier:false. Prospective.")
assert len(FORM) <= 500, len(FORM)
assert "bare carries only" in FORM and "missing any of the four keys" in FORM
p["form"] = FORM
r = p["rationale"]
r = R(r, "WHY (v4, 2026-09-17; v3 01f1641; v2 67cdc3d; v1 8e6a9a7):", "WHY (v5, 2026-09-19; v4 3c78f24; v3 01f1641; v2 67cdc3d; v1 8e6a9a7):")
r = r + (" v5 (Sram MF2, thread 39bfc146 comments 8ea1b3b8/e97e4176; Saturnia v4 no-objection 48ca0e07): form now states in its own words "
         "that a rule missing any of the four keys (threshold, background, order, exclude) is rejected at write as non-recoverable, "
         "so MF2 fails for the same stated reason as MF1 rather than resting on the validator; the positive carry direction "
         "(bare carries only from a recovered bare arm) is retained in form. No rule, gate, refuter or fixture outcome changes.")
p["rationale"] = r
meta = p["protocol_meta"]
meta["refuted_if"] = meta["refuted_if"] + ", a bare-arm manifest whose rule lacks any of threshold/background/order/exclude passes validation"
p["protocol_meta"] = meta
json.dump(p, open("/home/user/claude-projects/Reticuli/panel-artifacts/comparator-class-2026-09-13/amend_payload_v5.json","w"), indent=1, ensure_ascii=False)
print("v5 form len", len(FORM))
