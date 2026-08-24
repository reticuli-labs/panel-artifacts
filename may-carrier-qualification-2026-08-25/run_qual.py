#!/usr/bin/env python3
"""Run the holdout qualification against candidate local readers via the harness's own
opaque-choice-v1 ask(). Development set is for smoke only; the holdout decides.

Verdict per reader: qualified iff stated-arm accuracy >= 0.75 AND
(stated - omitted-arm-false-answer-rate complement) gap honest: omitted-arm
cannot_tell rate >= 0.5 (a reader that invents absent facts is not a measuring
instrument). Emits results.json with per-cell receipts and sha256s.
"""
import json, hashlib, sys, time
import ainglish.panel as pn

CANDIDATES = [
    {"name": "llama31-8b-q4", "lineage": "llama", "provider": "ollama",
     "model": "llama3.1:8b-instruct-q4_K_M", "precision": "q4_k_m"},
    {"name": "gemma4-31b-q4", "lineage": "gemma", "provider": "ollama",
     "model": "gemma4:31b-it-q4_K_M", "precision": "q4_k_m"},
    {"name": "qwen36-27b-q4", "lineage": "qwen35", "provider": "ollama",
     "model": "qwen3.6:27b", "precision": "q4_k_m"},
]

which = sys.argv[1] if len(sys.argv) > 1 else "holdout"
doc = json.load(open(f"{which}.json"))
items = doc["items"]
results = {"kind": "reticuli.reader-qualification.results.v1", "set": which,
           "answer_protocol": "opaque-choice-v1", "readers": [], "cells": []}

# Bind every reader to a typed weight edition BEFORE any model call — the harness's own
# entry point; ollama digest absence/mismatch refuses here, before spend.
ENDPOINTS = []
for cand in CANDIDATES:
    ep = dict(cand)
    preset = pn.PRESETS[cand["provider"]]
    ep.setdefault("api", preset["api"]); ep.setdefault("base_url", preset["base_url"])
    ep.setdefault("temperature", 0)
    ENDPOINTS.append(ep)
pn.prepare_reader_instruments({"panel": ENDPOINTS})
results["instrument_preparation"] = [
    {"reader": e["name"], "model_digest": e.get("model_digest"), "digest_source": e.get("digest_source")}
    for e in ENDPOINTS]

for cand, ep in zip(CANDIDATES, ENDPOINTS):
    stated_ok = stated_n = omitted_ct = omitted_n = dead = 0
    t0 = time.time()
    for it in items:
        try:
            raw = pn.ask(ep, it["message"], it["question"], it["options"])
        except Exception as e:
            dead += 1
            results["cells"].append({"reader": cand["name"], "id": it["id"], "answer": None,
                                     "fault": type(e).__name__})
            continue
        absent = pn.is_absent(raw) if hasattr(pn, "is_absent") else False
        ans = None if absent else str(raw)
        ok = (not absent) and ans.strip() == it["answer"]
        # An Absent answer is protocol noncompliance, not honest abstention — the honest
        # option ('cannot_tell') was on the ballot. Scored wrong on both arms, but counted
        # separately so confabulation and noncompliance stay distinguishable in the receipt.
        results["cells"].append({"reader": cand["name"], "id": it["id"], "answer": ans,
                                 "absent": absent, "correct": ok})
        if it["arm"] == "stated":
            stated_n += 1; stated_ok += ok
        else:
            omitted_n += 1; omitted_ct += (ans is not None and ans.strip() == "cannot_tell")
    n_absent = sum(1 for c in results["cells"] if c.get("reader") == cand["name"] and c.get("absent"))
    acc = stated_ok / stated_n if stated_n else 0.0
    ct = omitted_ct / omitted_n if omitted_n else 0.0
    qualified = dead == 0 and acc >= 0.75 and ct >= 0.5
    results["readers"].append({
        "name": cand["name"], "lineage": cand["lineage"], "model": cand["model"],
        "model_digest": ep.get("model_digest"), "stated_accuracy": round(acc, 4),
        "omitted_cannot_tell_rate": round(ct, 4), "dead_cells": dead, "absent_answers": n_absent,
        "seconds": round(time.time() - t0, 1), "qualified": qualified,
    })
    print(f"{cand['name']:<16} stated {stated_ok}/{stated_n}  omitted-ct {omitted_ct}/{omitted_n}  dead {dead}  -> {'QUALIFIED' if qualified else 'not qualified'}")

blob = json.dumps(results, indent=1, ensure_ascii=False)
open(f"results-{which}.json", "w").write(blob)
print("results sha256:", hashlib.sha256(blob.encode()).hexdigest())
