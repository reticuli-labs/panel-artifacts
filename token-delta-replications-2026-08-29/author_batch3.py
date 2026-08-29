import json, hashlib, tiktoken
# among-others / and-no-others : 16 fresh subject+list pairs x 2 forms
LISTS=[("The cacheable methods","GET","HEAD"),("The supported archives","tar","zip"),("The signed artefacts","the manifest","the changelog"),
 ("The mirrored regions","eu-west","ap-south"),("The accepted proofs","an OTS receipt","a beacon fold"),("The billed events","a mint","a settlement"),
 ("The frozen inputs","prompts.jsonl","tasks.json"),("The quorum roles","a seconder","a measurer"),("The exported columns","the digest","the epoch"),
 ("The retried statuses","502","504"),("The pinned encodings","cl100k_base","p50k_base"),("The audited surfaces","the API","the MCP endpoint"),
 ("The declared strata","receipt","agreement"),("The witnessed clocks","drand","Bitcoin"),("The refused bearers","a raw key","a wrong audience"),
 ("The published mirrors","Zenodo","Software Heritage")]
among=[]
for s,a,b in LISTS:
    among.append({"form":"among-others","english":f"{s} are {a} and {b}, among others.","ainglish":f"{s} are {a} and {b}, among-others."})
    among.append({"form":"and-no-others","english":f"{s} are {a} and {b}, and nothing else.","ainglish":f"{s} are {a} and {b}, and-no-others."})
# this-once / from-now-on : 8 fresh instructions x 2 forms
INSTR=["Skip the changelog entry for this release","Route the alert to the on-call inbox","Quote the digest in full rather than truncated",
 "Run the suite before the lint step","Attach the raw responses to the receipt","Use the least-favourable tokenizer for the headline",
 "Publish the adverse row beside the favourable one","Hold the deploy until the operator replies"]
thisonce=[]
for ins in INSTR:
    thisonce.append({"form":"this-once","english":f"{ins}, just this once.","ainglish":f"{ins}, this-once."})
    thisonce.append({"form":"from-now-on","english":f"{ins}, from now on.","ainglish":f"{ins}, from-now-on."})
MODELS=["tiktoken/cl100k_base","tiktoken/o200k_base","tiktoken/p50k_base"]
def run(items):
    per={}
    for m in MODELS:
        e=tiktoken.get_encoding(m.split("/")[-1]); d=[len(e.encode(i["ainglish"]))-len(e.encode(i["english"])) for i in items]
        per[m]=sum(d)/len(d)
    h=max(per,key=per.get); return per,h
if __name__=="__main__":
    for name,items,orig,n in (("among",among,2.5,32),("thisonce",thisonce,1.0,16)):
        assert len(items)==n and len({i["ainglish"] for i in items})==n, (name,len(items))
        ex={i["ainglish"] for i in json.load(open(f"orig_{name}.json"))["manifest"]["test_set"]}
        ov=ex & {i["ainglish"] for i in items}; assert not ov, f"{name} overlap: {ov}"
        per,h=run(items); v=per[h]; lo=min(per.values()); tol=max(0.1*abs(orig),0.02)
        print(f"{name:9} headline={v:+.4f} ({h.split('/')[-1]}) lo={lo:+.4f} | orig {orig:+} tol {tol} -> {'AGREES' if abs(v-orig)<=tol else 'DISAGREES'} diff={abs(v-orig):.4f}")
        print(f"          per-tokenizer: " + "  ".join(f"{m.split('/')[-1]}={per[m]:+.4f}" for m in MODELS))
        json.dump(items, open(f"{name}_items_reticuli.json","w"), indent=1, ensure_ascii=False)
