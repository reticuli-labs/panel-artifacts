"""Fresh, form-balanced item sets authored by Reticuli 2026-08-28 for token_delta replications.
Controls apply the proposal's declared slot meaning verbatim (the register's comparator rule)."""
import json, hashlib, tiktoken

# ---------- test-run(<T>) / test-passed(<T>) : 16 + 16, all new subjects/test refs/domains ----------
RUN = [("firmware image F31","boot-loop-soak@run-2207"),("ledger snapshot L8","balance-recompute@run-91"),("translation memory TM4","segment-align@run-17"),
 ("kiln batch K12","thermal-profile@run-6"),("vaccine lot V220","potency-assay@run-3"),("bridge span S2","load-cycle@run-440"),("ETL job J55","row-count-parity@run-1201"),
 ("kernel build 6.14-rc3","kselftest-net@run-88"),("telescope mount T1","pointing-drift@run-12"),("payroll run P0828","withholding-check@run-4"),("drone airframe D7","vibration-sweep@run-29"),
 ("contract draft C19","clause-lint@run-2"),("solar inverter I3","anti-island@run-15"),("archive tape A44","read-back@run-9"),("recipe card R5","allergen-scan@run-1"),("elevator car E2","overspeed-brake@run-33")]
PASSED = [("firmware image F32","boot-loop-soak@run-2208"),("ledger snapshot L9","balance-recompute@run-92"),("translation memory TM5","segment-align@run-18"),
 ("kiln batch K13","thermal-profile@run-7"),("vaccine lot V221","potency-assay@run-4"),("bridge span S3","load-cycle@run-441"),("ETL job J56","row-count-parity@run-1202"),
 ("kernel build 6.14-rc4","kselftest-net@run-89"),("telescope mount T2","pointing-drift@run-13"),("payroll run P0829","withholding-check@run-5"),("drone airframe D8","vibration-sweep@run-30"),
 ("contract draft C20","clause-lint@run-3"),("solar inverter I4","anti-island@run-16"),("archive tape A45","read-back@run-10"),("recipe card R6","allergen-scan@run-2"),("elevator car E3","overspeed-brake@run-34")]
testrun_items = []
for i,(s,t) in enumerate(RUN,1):
    testrun_items.append({"item_id": f"ret-trp-run-{i:02d}", "form": "test-run", "subject": s, "test_ref": t,
        "ainglish": f"{s}, test-run({t}).", "english": f"Test execution {t} occurred on {s}; its outcome is not asserted."})
for i,(s,t) in enumerate(PASSED,1):
    testrun_items.append({"item_id": f"ret-trp-pass-{i:02d}", "form": "test-passed", "subject": s, "test_ref": t,
        "ainglish": f"{s}, test-passed({t}).", "english": f"Test execution {t} occurred on {s} and satisfied every acceptance criterion declared by that test for that run."})

# ---------- different-from / different-across : 16 + 16 ----------
THINGS = [("dataset","license-id"),("container image","digest"),("reviewer","affiliation"),("wallet","owner"),("compiler","version"),("font","family-name"),
 ("mirror","host"),("prompt","template-hash"),("voice sample","speaker-id"),("seed","value"),("proxy","exit-region"),("tokenizer","vocab-checksum"),
 ("judge","operator"),("baseline","commit"),("microphone","serial"),("corpus slice","slice-sha256")]
diff_items = []
for i,(thing,key) in enumerate(THINGS,1):
    diff_items.append({"form": "different-from",
        "english": f"Pick {i:02d}: choose a {thing} whose {key} is unequal to the reference {thing}'s {key}.",
        "ainglish": f"Pick {i:02d}: choose a {thing} different-from(reference-{thing}, by={key})."})
    diff_items.append({"form": "different-across",
        "english": f"Pick {i:02d}: give a {thing} to every judge such that distinct judges' chosen {key} values are pairwise unequal.",
        "ainglish": f"Pick {i:02d}: give a {thing} to every judge different-across(judges, by={key})."})

def run(items, encs):
    out={}
    for name in encs:
        e=tiktoken.get_encoding(name)
        d=[len(e.encode(it["ainglish"]))-len(e.encode(it["english"])) for it in items]
        out[name]={"mean": sum(d)/len(d), "min": min(d), "max": max(d), "per_form": {f: sum(x for x,it in zip(d,items) if it["form"]==f)/sum(1 for it in items if it["form"]==f) for f in sorted({it["form"] for it in items})}}
    means={k:v["mean"] for k,v in out.items()}
    return out, max(means.values()), max(means,key=means.get), min(means.values())

if __name__=="__main__":
    for label,items,encs,orig,tol in (("test-run",testrun_items,["cl100k_base","o200k_base"],-6.9375,0.69375),("different-from",diff_items,["cl100k_base","o200k_base","p50k_base"],-0.1875,0.02)):
        assert len(items)==32 and len({it["ainglish"] for it in items})==32
        out,head,headtok,lo=run(items,encs)
        print(f"\n{label}: headline(max mean)={head:.5f} on {headtok}  lo={lo:.5f}  | original {orig} tol ±{tol} -> {'AGREES' if abs(head-orig)<=tol else 'DISAGREES'} (diff {abs(head-orig):.4f})")
        for k,v in out.items(): print(f"   {k}: mean={v['mean']:.5f} range[{v['min']},{v['max']}] per_form={ {f:round(x,4) for f,x in v['per_form'].items()} }")
        print("   items_sha256:", hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest()[:16], "tiktoken", tiktoken.__version__)
