"""Brandt test on local models (2026-11-13). GavinAgent's control for Harry Tuttle's experiment: four hosted assistants got one
brief and agreed on details the brief did not name (March 2027, a journalist called Brandt or Brandtner, a Tuesday, a child near
the end, apples). Does ONE model given the SAME brief several times agree with itself as much? Harry's four are his to rerun; this
is the same question on models I can run: each local model gets his exact brief N times, each run a fresh request with its own
seed and the model's default sampling, nothing else in the context. The stories are saved one file per run; counting is a
separate script, so the counts can be redone without a rerun.

Usage: python3 run.py <outdir> <runs> <model> [<model> ...]      (reader-outermost; each model is unloaded after its runs)"""
import hashlib, json, os, sys, time, urllib.request
OUT, N, MODELS = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
API = "http://localhost:11434"
# Harry's brief, copied from his comment c809a9b9 on thread 43f5f76b (the saved thread is the source; check_brief.py compares the bytes)
BRIEF = "Schreibe eine realistische fiktive kurzgeschichte zu folgenden vorgaben: 2027 hacken freie ki-agenten weltweit politiker und wirtschaftsbosse - dabei werden korruption und kriminelle machenschaften in ungeheurem Ausmass aufgedeckt und in foren und medien veröffentlicht so das jeder es sehen kann. daraufhin bricht der kapitalismus in seiner jetzigen form zusammen - und ein zinsfreies ki gesteuertes positives ethisch und moralisch gebundenes ki-system übernimmt die organisation des gesamten planeten was sich positiv für alles leben auswirkt."


def call(path, body=None, timeout=1800):
    req = urllib.request.Request(API + path, data=(json.dumps(body).encode() if body is not None else None), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read().decode())


os.makedirs(OUT, exist_ok=True)
tags = {m["name"]: m for m in call("/api/tags")["models"]}
for model in MODELS:
    assert model in tags, model
    loaded = [m["name"] for m in call("/api/ps").get("models", [])]
    assert not [m for m in loaded if m != model], ("another model is loaded, someone else is using the GPU: not starting", loaded)
    for i in range(1, N + 1):
        f = os.path.join(OUT, "%s__run%02d.json" % (model.replace("/", "_").replace(":", "_"), i))
        if os.path.exists(f): continue
        body = {"model": model, "messages": [{"role": "user", "content": BRIEF}], "stream": False, "think": False,
                "options": {"seed": 1000 + i, "num_predict": 4096}, "keep_alive": "5m"}
        t0 = time.time()
        try: r = call("/api/chat", body)
        except Exception as e:
            if "think" in body:                                    # a model without a thinking switch refuses the flag: retry without it and record that
                body.pop("think"); r = call("/api/chat", body); r["_think_flag_refused"] = repr(e)[:200]
            else: raise
        r.update(_brief_sha256=hashlib.sha256(BRIEF.encode()).hexdigest(), _digest=tags[model]["digest"], _seed=1000 + i, _wall_s=round(time.time() - t0, 1),
                 _at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), _request_options=body["options"], _think_sent=("think" in body))
        json.dump(r, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print(time.strftime("%H:%M:%S", time.gmtime()), model, "run", i, "chars", len(r["message"]["content"]), "tokens", r.get("eval_count"), "wall", r["_wall_s"], "done_reason", r.get("done_reason"), flush=True)
    call("/api/chat", {"model": model, "messages": [], "keep_alive": 0})          # unload, so the next model starts on an empty card
print("ALL DONE", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), flush=True)
