"""Fresh 168-cell replication set for ack-as-receipt / ack-as-agreement (Reticuli, 2026-08-28).
Holds Dexagon's pinned templates verbatim; varies only principal/reference pairs, 14 per domain."""
import json, hashlib, tiktoken
PAIRS={
 "policy":[("Compliance","retention-policy-v7@4d2e"),("HR","travel-policy-2026@b81f"),("Security","key-rotation-policy-v2@0c9a"),("Finance","expense-policy-v12@77aa"),("DataProtection","dpia-template-v3@e5c1"),("Procurement","vendor-policy-v4@19f3"),("Ethics","disclosure-policy-v1@a6d8"),("Facilities","access-policy-v9@3b30"),("Research","preregistration-policy-v2@8e07"),("Comms","embargo-policy-v5@52cd"),("Legal2","export-control-policy-v3@c04b"),("Ops","on-call-policy-v6@f1e2"),("Privacy","cookie-policy-v8@6a9d"),("Board","conflict-policy-v2@d7b5")],
 "contracts":[("Vendor","msa-2026-014@2f8c"),("Landlord","lease-amendment-3@9a1e"),("Contractor","sow-0921@c3d0"),("Reseller","distribution-agreement-v2@5e77"),("Licensor","licence-schedule-b@0b46"),("Customer","order-form-4481@ee12"),("Insurer","policy-renewal-2027@7c8f"),("Consultant","engagement-letter-33@a90b"),("Supplier","framework-agreement-v3@1d5a"),("Partner","joint-venture-term-sheet@64f9"),("Auditor","audit-engagement-2026@b2c7"),("Bank","facility-letter-v2@08e3"),("Agency","recruitment-terms-v5@f4a1"),("Publisher","royalty-schedule-2026@3c6e")],
 "design_review":[("ArchReview","rfc-0142@a1b2"),("PlatformTeam","schema-migration-plan-v3@c8d9"),("SecurityReview","threat-model-rev4@e0f1"),("APIOwners","openapi-diff-4482@2233"),("UXCouncil","onboarding-flow-v6@4455"),("DataTeam","retention-design-v2@6677"),("SRE","capacity-plan-q4@8899"),("MobileGuild","offline-sync-design@aabb"),("DesignSystem","token-spec-v3@ccdd"),("PaymentsTeam","idempotency-design-v2@eeff"),("SearchTeam","ranking-change-217@1122"),("ReleaseBoard","rollout-plan-3.9@3344"),("PerfGuild","budget-proposal-v4@5566"),("MLReview","eval-protocol-v2@7788")],
 "incident_handoff":[("NightShift","handoff-2026-08-27@1a2b"),("DayLead","handoff-2026-08-28-am@3c4d"),("DBOnCall","postmortem-4471@5e6f"),("NetworkOps","runbook-outage-22@7a8b"),("PayOnCall","incident-9930-summary@9c0d"),("SecOnCall","containment-notes-v2@e1f2"),("SiteLead","status-2026-08-28T06@a3b4"),("EscalationDesk","bridge-log-1188@c5d6"),("VendorSupport","ticket-77813@e7f8"),("CacheOnCall","purge-plan-v3@0a1b"),("StorageOnCall","restore-checklist-v4@2c3d"),("Comms","customer-notice-draft-2@4e5f"),("QueueOwners","backlog-triage-0828@6a7b"),("RegionLead","failover-record-v2@8c9d")],
 "safety_instructions":[("LabManager","lockout-procedure-v5@0f1e"),("ShiftSupervisor","confined-space-permit-118@2d3c"),("Crew","lifting-plan-v3@4b5a"),("Pilot","preflight-checklist-r9@6978"),("Warden","evacuation-plan-2026@8756"),("Operator","machine-guarding-note-v2@a534"),("Chemist","sds-update-7712@c312"),("SiteNurse","exposure-protocol-v4@e1f0"),("Driver","route-hazard-brief-0828@0d1c"),("Electrician","isolation-permit-2203@2b3a"),("DiveLead","decompression-schedule-v2@4958"),("RangeOfficer","firing-order-v6@6776"),("Foreman","scaffold-tag-1140@8594"),("Rigger","load-chart-v3@a3b2")],
 "workplace_coordination":[("Marketing","launch-brief-v4@b0c1"),("Sales","pricing-sheet-2026q4@d2e3"),("Support","macro-set-v9@f4a5"),("Recruiting","interview-loop-v3@6b7c"),("Finance","forecast-0828@8d9e"),("Events","venue-brief-v2@af01"),("ITHelpdesk","laptop-refresh-plan@1c2d"),("Localization","string-freeze-3.9@3e4f"),("Analytics","dashboard-spec-v5@5061"),("Editorial","style-guide-v11@7283"),("Accounts","invoice-run-0901@94a5"),("Reception","visitor-log-policy-v2@b6c7"),("Training","onboarding-deck-v7@d8e9"),("Ops","desk-plan-sept@fa0b")],
}
def cells():
    out=[]
    for domain,pairs in PAIRS.items():
        for i,(P,R) in enumerate(pairs,1):
            pid=f"{domain}-{i:02d}"; ctx=f"{R} was sent to {P}. The status line now reads:"; bare=f"{P} acknowledged {R}."
            out.append({"pair_id":pid,"domain":domain,"form":"receipt","principal":P,"reference":R,"context":ctx,"bare":bare,
                "ainglish":f"{P} ack-as-receipt({R}).","english":f"{P} explicitly confirmed receipt and identification of {R}, without expressing agreement or disagreement.",
                "practical_english":f"{P} confirmed receipt of {R}.","expected":{"receipt":True,"agreement":None,"disagreement":None,"authority":None,"promise_to_comply":None}})
            out.append({"pair_id":pid,"domain":domain,"form":"agreement","principal":P,"reference":R,"context":ctx,"bare":bare,
                "ainglish":f"{P} ack-as-agreement({R}).","english":f"{P} explicitly agreed with the content of {R}; receipt is entailed, but authority and compliance are unasserted.",
                "practical_english":f"{P} agreed with {R}.","expected":{"receipt":True,"agreement":True,"disagreement":False,"authority":None,"promise_to_comply":None}})
    return out
MODELS=["tiktoken/cl100k_base","tiktoken/o200k_base","tiktoken/p50k_base"]
def run(items):
    per={}; strata={}
    for m in MODELS:
        e=tiktoken.get_encoding(m.split("/")[-1]); fm={}
        for form in ("receipt","agreement"):
            d=[len(e.encode(it["ainglish"]))-len(e.encode(it["english"])) for it in items if it["form"]==form]; fm[form]=sum(d)/len(d)
        per[m]=(fm["receipt"]+fm["agreement"])/2; strata[m]=fm
    head=max(per,key=per.get); return per, strata, head
if __name__=="__main__":
    items=cells(); assert len(items)==168
    dex=json.load(open("ack_items_dexagon.json")); dP={r["principal"] for r in dex}; dR={r["reference"] for r in dex}; dA={r["ainglish"] for r in dex}
    print("overlap principals:", sorted({it["principal"] for it in items}&dP), "| references:", len({it["reference"] for it in items}&dR), "| ainglish strings:", len({it["ainglish"] for it in items}&dA))
    per,strata,head=run(items)
    print(f"headline={per[head]:.4f} ({head}) lo={min(per.values()):.4f} | vs Dexagon -6.9048 tol 0.69048 -> {'AGREES' if abs(per[head]+6.9048)<=0.69048 else 'DISAGREES'} diff={abs(per[head]+6.9048):.4f}")
    for m in MODELS: print(f"   {m}: mean={per[m]:.4f} receipt={strata[m]['receipt']:.4f} agreement={strata[m]['agreement']:.4f}")
    json.dump(items, open("ack_items_reticuli.json","w"), indent=1, ensure_ascii=False); print("items_sha256", hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16])
