import json, urllib.request, collections
S = "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad"
m = json.load(open(f"{S}/they_manifest.json"))
cal = [i for i in m["items"] if i.get("calibration")]
def ask(model, it, arm):
    codes = dict(zip("ABC", it["options"]))
    ch = "\n".join(f"{c}: {o}" for c, o in codes.items())
    prompt = (f"Read this message written by one agent to another:\n\n---\n{it[arm]}\n---\n\n"
              f"Question: {it['question']}\nChoices:\n{ch}\nAnswer with EXACTLY one choice code and nothing else.")
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3072, "temperature": 0, "stream": False}
    r = urllib.request.Request("http://localhost:11434/v1/chat/completions",
                               json.dumps(body).encode(), {"Content-Type": "application/json"})
    d = json.load(urllib.request.urlopen(r, timeout=600))
    return (d["choices"][0]["message"].get("content") or "").strip()[:1]
# Which stratum is the bare arm answerable in? That is the whole question.
score = collections.defaultdict(lambda: {"det": 0, "oth": 0, "n": 0})
for name, model in [("qwen3.6-27b", "qwen3.6:27b"), ("ornith-35b", "hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF:Q4_K_M")]:
    for it in cal:
        number = "one" if "they-one" in it["ainglish"] else "many"
        key = next(c for c, o in zip("ABC", it["options"]) if o == it["answer"])
        a = ask(model, it, "ainglish"); e = ask(model, it, "english")
        s = score[number]; s["n"] += 1; s["det"] += (a == key); s["oth"] += (e == key)
        print(f"  {name:12} {it['id']:6} they-{number:4} key={key}  marked={a!r} bare={e!r}", flush=True)
print("\n=== is the BARE arm answerable, by stratum? ===")
for number in ("one", "many"):
    s = score[number]
    print(f"  they-{number:5} n={s['n']}  marked {s['det']}/{s['n']}  BARE {s['oth']}/{s['n']}"
          f"   gap {(s['det']-s['oth'])/s['n']:+.3f}")
