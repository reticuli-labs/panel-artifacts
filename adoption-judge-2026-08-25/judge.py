import json, sys, time, urllib.request, re
RULE=("Count a match as USE only when the construct performs its mapped communicative function in running prose — the writer is using the marker "
      "to say something about the world or their own claim. Count it as MENTION when the text merely names, quotes, discusses, lists, defines, "
      "measures, votes on, or gives an example of the marker: proposal and register discussion, code or fenced examples, ballots, measurement talk, and quotations are MENTIONS.")
def ask(model, text, form, slug):
    prompt=(f"You are auditing a message from an agent forum for ADOPTION of a register construct.\n\nConstruct: {form}\n\n{RULE}\n\n"
            f"Message:\n---\n{text}\n---\n\nIs the construct USED here (performing its function in the writer's own running prose) or merely MENTIONED? "
            "Answer with exactly one word: USE or MENTION.")
    body=json.dumps({"model":model,"reasoning_effort":"none","temperature":0,"seed":7,"max_tokens":8,"messages":[{"role":"user","content":prompt}]}).encode()
    r=json.loads(urllib.request.urlopen(urllib.request.Request("http://127.0.0.1:11434/v1/chat/completions", body, {"Content-Type":"application/json"}), timeout=600).read())
    out=(r["choices"][0]["message"].get("content") or "").strip().upper()
    return "use" if out.startswith("USE") else ("mention" if out.startswith("MENTION") else "unparsed:"+out[:20])
model=sys.argv[1]; cands=json.load(open("candidates.json")); forms={c["slug"]:c["form"] for c in cands}
out=[]; t0=time.time()
for i,c in enumerate(cands):
    v=ask(model, c["text"], c["form"], c["slug"]); out.append({**{k:c[k] for k in ("slug","author","created","ref","regex_uses","regex_mentions")}, "judge":v})
    if i%25==0: print(f"  {i}/{len(cands)} {int(time.time()-t0)}s", flush=True)
json.dump(out, open(f"judged-{model.split(':')[0]}.json","w"), indent=0)
print("done", len(out), "in", int(time.time()-t0), "s")
