import json, urllib.request, collections, sys
S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
m = json.load(open(f"{S}/gun_manifest_run2.json"))
cal = [i for i in m["items"] if i.get("calibration")]
sci = [i for i in m["items"] if not i.get("calibration")][:4]

def ask(model, it, arm):
    codes = dict(zip("ABC", it["options"]))
    choices = "\n".join(f"{c}: {o}" for c, o in codes.items())
    prompt = (f"Read this message written by one agent to another:\n\n---\n{it[arm]}\n---\n\n"
              f"Question: {it['question']}\nChoices:\n{choices}\n"
              f"Answer with EXACTLY one choice code and nothing else.")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3072, "temperature": 0, "stream": False}
    req = urllib.request.Request("http://localhost:11434/v1/chat/completions",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=900))
    return (d["choices"][0]["message"].get("content") or "").strip()[:1]

for name, model in [("ornith-35b", "hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF:Q4_K_M"),
                    ("seed-oss-36b", "milkey/Seed-OSS-36B-Instruct:Q4_K_M")]:
    print(f"=== {name}: both arms, 6 calibration + 4 scientific ===", flush=True)
    dist = collections.Counter(); det = oth = 0
    for it in cal:
        key = next(c for c, o in zip("ABC", it["options"]) if o == it["answer"])
        a = ask(model, it, "ainglish"); e = ask(model, it, "english")
        dist[a] += 1; dist[e] += 1
        det += (a == key); oth += (e == key)
        print(f"  {it['id']:6} key={key}  ainglish={a!r}  english={e!r}", flush=True)
    for it in sci:
        a = ask(model, it, "ainglish"); dist[a] += 1
        print(f"  {it['id']:6} (sci) ainglish={a!r}", flush=True)
    gap = det/6 - oth/6
    print(f"  distribution: {dict(dist)}", flush=True)
    print(f"  detectable {det}/6, other {oth}/6, gap {gap:+.3f} (panel gate needs >= 0.5)", flush=True)
    print(f"  VERDICT: {'DEGENERATE - single answer' if len(dist)==1 else ('cannot detect the marker' if gap < 0.5 else 'QUALIFIES')}\n", flush=True)
