#!/usr/bin/env python3
"""Panel runner for the whole/part replication (attempt 58d2d1f8). Same discipline."""
import json, hashlib, re, time, urllib.request

SEED = 2026082201
READERS = [
    ("qwen3.8-27b", "qwen3.8:27b"),
    ("ornith-1.0-35b", "hf.co/deepreinforce-ai/Ornith-1.0-35B-GGUF:Q4_K_M"),
]
doc = json.load(open("wholepart-replication-items.json"))
jcs = json.dumps(doc["items"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
assert hashlib.sha256(jcs).hexdigest() == "d95039c2d98907c765e4f2019dba599255ae0a6e604ceb3450732922c9dded63"
cal = [x for x in doc["items"] if x.get("calibration")]
real = sorted([x for x in doc["items"] if not x.get("calibration")], key=lambda x: x["id"])

LOG = open("wp-run.jsonl", "a")

NO_THINK = {}  # model -> False when the model rejects the think parameter

def ask(model, prompt):
    t0 = time.time()
    payload = {"model": model, "stream": False,
               "messages": [{"role": "user", "content": prompt}],
               "options": {"temperature": 0, "seed": 20260822, "num_predict": 2048}}
    if NO_THINK.get(model, True):
        payload["think"] = False
    try:
        req = urllib.request.Request("http://127.0.0.1:11434/api/chat",
                                     data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "think" in body and NO_THINK.get(model, True):
            NO_THINK[model] = False
            return ask(model, prompt)
        raise RuntimeError(f"HTTP {e.code}: {body[:150]}")
    return d["message"]["content"], d.get("done_reason"), round(time.time() - t0, 1)

def parse(text, options):
    text = re.sub(r"<think>.*?</think>", " ", text, flags=re.S)
    lines = [l.strip().strip("*`'\"().") for l in text.splitlines() if l.strip()]
    for l in reversed(lines):
        for o in options:
            if l == o or l.lower() == o.lower():
                return o
    # last word-boundary occurrence of any option in the tail
    best, pos = None, -1
    for o in options:
        for m in re.finditer(r"(?<![\w.])" + re.escape(o) + r"(?![\w.])", text, flags=re.I):
            if m.start() > pos:
                best, pos = o, m.start()
    return best  # None -> unparsed

def cell(reader, model, item, arm):
    passage = item[arm]
    prompt = (passage + "\n\n" + item["question"] + "\n\nOptions:\n"
              + "\n".join("- " + o for o in item["options"])
              + "\n\nAnswer with exactly one option, verbatim, on the final line.")
    rec = {"reader": reader, "item": item["id"], "arm": arm, "fault": None}
    for attempt in range(2):
        try:
            text, finish, dt = ask(model, prompt)
            rec.update(response=text[-3000:], finish_reason=finish, latency_s=dt,
                       truncated=(finish == "length"), retried=bool(attempt))
            break
        except Exception as e:
            rec["fault"] = f"{type(e).__name__}: {e}"[:200]
            time.sleep(3)
    else:
        rec.update(response=None, finish_reason="fault", latency_s=None, truncated=False, retried=True)
    p = parse(rec["response"], item["options"]) if rec.get("response") else None
    rec["parsed"] = p
    rec["correct"] = (p == item["answer"]) if p is not None else None
    LOG.write(json.dumps(rec, ensure_ascii=False) + "\n"); LOG.flush()
    return rec

def deal_arm(reader, item_id):
    h = hashlib.sha256(f"{SEED}|{reader}|{item_id}".encode()).digest()
    return "ainglish" if h[0] & 1 else "english"

summary = {}
for reader, model in READERS:
    print(f"== {reader}: calibration ({len(cal)}x2 cells)", flush=True)
    accs = {"ainglish": [], "english": []}
    for item in cal:
        for arm in ("ainglish", "english"):
            r = cell(reader, model, item, arm)
            accs[arm].append(1 if r["correct"] else 0)
    gap = sum(accs["ainglish"]) / len(cal) - sum(accs["english"]) / len(cal)
    passed = gap >= 0.5
    print(f"   planted acc={sum(accs['ainglish'])}/{len(cal)} underdet-hit={sum(accs['english'])}/{len(cal)} gap={gap:.2f} -> {'PASS' if passed else 'FAIL (excluded)'}", flush=True)
    summary[reader] = {"cal_gap": round(gap, 4), "cal_planted_acc": sum(accs["ainglish"]) / len(cal),
                       "cal_underdet_hit": sum(accs["english"]) / len(cal), "passed": passed}
    if not passed:
        continue
    print(f"== {reader}: scored ({len(real)} cells)", flush=True)
    done = 0
    for item in real:
        cell(reader, model, item, deal_arm(reader, item["id"]))
        done += 1
        if done % 15 == 0:
            print(f"   {done}/{len(real)}", flush=True)

json.dump(summary, open("wp-cal-summary.json", "w"), indent=1)
print("RUN COMPLETE", json.dumps(summary), flush=True)
