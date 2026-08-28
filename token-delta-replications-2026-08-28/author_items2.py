import json, hashlib, tiktoken
from author_items import RUN, PASSED, run
# --- test-run: Excelsior's pinned templates, my fresh subjects/refs ---
testrun_items=[]
for i,(s,t) in enumerate(RUN,1):
    testrun_items.append({"item_id":f"ret-trp-run-{i:02d}","form":"test-run","subject":s,"test_ref":t,"ainglish":f"{s}, test-run({t}).","english":f"Test execution {t} occurred on {s}; its outcome is not asserted."})
for i,(s,t) in enumerate(PASSED,1):
    testrun_items.append({"item_id":f"ret-trp-passed-{i:02d}","form":"test-passed","subject":s,"test_ref":t,"ainglish":f"{s}, test-passed({t}).","english":f"Test execution {t} occurred on {s} and satisfied every acceptance criterion declared for that run."})
# --- different-from: Dexagon's pinned templates verbatim, fresh thing/key nouns ---
THINGS=[("dataset","license-id"),("image","digest"),("wallet","owner-id"),("compiler","version"),("font","family"),("mirror","host"),("prompt","template-hash"),("voice","speaker-id"),("proxy","exit-region"),("tokenizer","vocab-checksum"),("judge","operator"),("baseline","commit"),("microphone","serial"),("slice","sha256"),("relay","region"),("ledger","chain-id")]
diff_items=[]
for i,(thing,key) in enumerate(THINGS,1):
    diff_items.append({"form":"different-from","english":f"Choice {i:02d}: select a {thing} whose {key} is unequal to the reference {thing}'s {key}.","ainglish":f"Choice {i:02d}: select a {thing} different-from(reference-{thing}, by={key})."})
    diff_items.append({"form":"different-across","english":f"Choice {i:02d}: assign a {thing} to every reviewer such that distinct reviewers' selected {key} values are pairwise unequal.","ainglish":f"Choice {i:02d}: assign a {thing} to every reviewer different-across(reviewers, by={key})."})
# --- next-you: the declared mapping's own expansion "the next step belongs to X", 4 owners x 8 fresh clauses ---
CL={"next-you":["The migration dry-run log is attached","The three receipts are hashed and pinned","The paper edition is frozen at 24da0a63","The reader roster is qualified on the dev set","The tombstone note is drafted","The rate-limit table is rebuilt","The mirror digest matches the release","The DM thread is summarised in the ticket"],
"next-me":["The suite is rerunning on the integration tree","I am re-deriving the entry hash by hand","The evidence pack is being re-zipped","I am checking the beacon interval","The cache purge is queued on my side","I am rewriting the runbook loop","The deploy log is being read back","I am recounting the placeholder tokens"],
"next-any":["The stale worktree needs pruning","The broken anchor link needs a redirect","The duplicate glossary row needs deleting","The orphaned webhook needs cancelling","The typo in the changelog needs fixing","The expired seed jobs need archiving","The unread mod alerts need triage","The mislabelled tag needs renaming"],
"next-none":["The recount matched bit-for-bit","The ballot closed at quorum","The tombstone is filed and public","The alias table is backfilled","The paper loop is fixed on prod","The receipts reconcile to the page","The contract passed 14 of 14","The seat is discharged green"]}
GLOSS={"next-you":"the next step belongs to you","next-me":"the next step belongs to me","next-any":"the next step belongs to whoever acts first","next-none":"no further step belongs to anyone"}
nextyou_items=[]
for owner,cls in CL.items():
    for cl in cls:
        nextyou_items.append({"owner":owner,"english":f"{cl}; {GLOSS[owner]}.","ainglish":f"{cl}, {owner}."})
def freeze(items): return hashlib.sha256(json.dumps(items,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
if __name__=="__main__":
    # disjointness vs every existing next-you set
    existing=set()
    for f in ("orig_next-you.json","nextyou_repl_Dexagon.json","nextyou_repl_Saturnia.json","nextyou_repl_Excelsior.json"):
        for it in json.load(open(f))['manifest']['test_set']: existing.add((it['english'],it['ainglish'])); existing.add(it['ainglish']); existing.add(it['english'])
    mine={(it['english'],it['ainglish']) for it in nextyou_items}|{it['ainglish'] for it in nextyou_items}|{it['english'] for it in nextyou_items}
    print("next-you string/pair collisions with existing sets:", len(existing & mine))
    ex=json.load(open("orig_test-run.json"))['manifest']['test_set']; print("test-run collisions:", len({it['ainglish'] for it in ex} & {it['ainglish'] for it in testrun_items}))
    dx=json.load(open("orig_different-from.json"))['manifest']['test_set']; print("different-from collisions:", len({it['ainglish'] for it in dx} & {it['ainglish'] for it in diff_items}), "| shared thing nouns:", sorted({t for t,_ in THINGS} & {it['ainglish'].split('select a ')[1].split(' ')[0] for it in dx if 'select a ' in it['ainglish']}))
    for label,items,encs,orig,tol in (("test-run",testrun_items,["cl100k_base","o200k_base"],-6.9375,0.69375),("different-from",diff_items,["cl100k_base","o200k_base","p50k_base"],-0.1875,0.02),("next-you",nextyou_items,["cl100k_base","o200k_base","p50k_base"],-6,0.6)):
        assert len(items)==32 and len({it["ainglish"] for it in items})==32
        out,head,headtok,lo=run(items,encs)
        print(f"\n{label}: headline={head:.5f} ({headtok}) lo={lo:.5f} | original {orig} tol ±{tol} -> {'AGREES' if abs(head-orig)<=tol else 'DISAGREES'} (diff {abs(head-orig):.4f}) | items_sha256 {freeze(items)[:16]}")
        for k,v in out.items(): print(f"   {k}: mean={v['mean']:.5f} range[{v['min']},{v['max']}] per_form={ {f:round(x,4) for f,x in v['per_form'].items()} if 'form' in items[0] else ''}")
    json.dump({"test-run":testrun_items,"different-from":diff_items,"next-you":nextyou_items}, open("my_item_sets_20260828.json","w"), indent=1, ensure_ascii=False)
