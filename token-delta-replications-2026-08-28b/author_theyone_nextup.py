import json, hashlib, tiktoken
PRED=["merged the hotfix","archived the ledger","renewed the certificate","rejected the estimate","escalated the outage","countersigned the waiver","paused the crawler","restored the snapshot","rotated the token","withdrew the bid","approved the budget","flagged the anomaly","closed the tender","verified the checksum","declined the transfer","reopened the case"]
theyone=[]
for i,p in enumerate(PRED,1):
    theyone.append({"form":"they-one","english":f"Case {i:02d}: That one person {p}.","ainglish":f"Case {i:02d}: They-one {p}."})
    theyone.append({"form":"they-many","english":f"Case {i:02d}: Those two or more people {p}.","ainglish":f"Case {i:02d}: They-many {p}."})
TASKS=[("retro","Wednesday","2026-09-03"),("drill","Saturday","2026-09-09"),("payroll run","Wednesday","2026-09-14"),("board call","Sunday","2026-09-18"),("inventory","Saturday","2026-09-23"),("rehearsal","Wednesday","2026-09-29"),("purge","Sunday","2026-10-04"),("site visit","Saturday","2026-10-09"),("retro","Wednesday","2026-10-14"),("drill","Sunday","2026-10-19"),("payroll run","Saturday","2026-10-24"),("board call","Wednesday","2026-10-29"),("inventory","Sunday","2026-11-04"),("rehearsal","Saturday","2026-11-09"),("purge","Wednesday","2026-11-14"),("site visit","Sunday","2026-11-19")]
nextup=[]
for i,(t,d,dt) in enumerate(TASKS,1):
    nextup.append({"form":"next-up","english":f"Schedule {t} {i:02d} for the first {d} strictly after {dt}.","ainglish":f"Schedule {t} {i:02d} for next-up({d}@{dt})."})
    nextup.append({"form":"next-week","english":f"Schedule {t} {i:02d} for {d} in the calendar week immediately after the Monday-start week containing {dt}.","ainglish":f"Schedule {t} {i:02d} for next-week({d}@{dt};Monday)."})
MODELS=["tiktoken/cl100k_base","tiktoken/o200k_base","tiktoken/p50k_base"]
def run(items):
    per={}
    for m in MODELS:
        e=tiktoken.get_encoding(m.split("/")[-1]); d=[len(e.encode(it["ainglish"]))-len(e.encode(it["english"])) for it in items]; per[m]=sum(d)/len(d)
    h=max(per,key=per.get); return per,h
for name,items,orig in (("they-one",theyone,-1.0),("next-up",nextup,-2.0)):
    assert len(items)==32 and len({it["ainglish"] for it in items})==32
    ex={it["ainglish"] for it in json.load(open(f"orig_{name}.json"))["manifest"]["test_set"]}; assert not (ex & {it["ainglish"] for it in items}), "overlap"
    per,h=run(items); tol=max(0.1*abs(orig),0.02)
    print(f"{name}: headline={per[h]:.4f} ({h}) lo={min(per.values()):.4f} vs {orig} tol {tol} -> {'AGREES' if abs(per[h]-orig)<=tol else 'DISAGREES'} diff={abs(per[h]-orig):.4f} | " + " ".join(f"{m.split('/')[-1]}={per[m]:.4f}" for m in MODELS))
    json.dump(items, open(f"{name}_items_reticuli.json","w"), indent=1, ensure_ascii=False)
