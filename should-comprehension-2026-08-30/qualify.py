#!/usr/bin/env python3
"""Qualify each candidate reader ALONE against the frozen calibration controls.

The remote-reader runbook is explicit: a pooled panel can hide one reader that cannot detect the
positive control, so every candidate is screened separately and failures are EXCLUDED rather than
retried until one passes. This spends ~24 cells per reader and nothing on the real items.
"""
import json, os, sys, collections, concurrent.futures as cf, urllib.request, time

KEY = os.environ["NOUS_API_KEY"]
CANDIDATES = ["deepseek/deepseek-v4-flash", "qwen/qwen3.8-flash",
              "z-ai/glm-5.3-flash", "google/gemini-3.7-flash"]
MIN_GAP = 0.5
MAX_TOKENS = int(os.environ.get("QUAL_MAX_TOKENS", "1024"))
CODES = "ABC"
items = [i for i in json.load(open("items.json")) if i.get("calibration")]


def prompt(i, arm):
    ch = "\n".join(f"{c}: {o}" for c, o in zip(CODES, i["options"]))
    return (f"Read this message written by one agent to another:\n\n---\n{i[arm]}\n---\n\n"
            f"Question: {i['question']}\nChoices:\n{ch}\n"
            "Answer with EXACTLY one choice code and nothing else.")


def call(job):
    model, i, arm = job
    body = {"model": model, "messages": [{"role": "user", "content": prompt(i, arm)}],
            "max_tokens": MAX_TOKENS, "temperature": 0}
    req = urllib.request.Request(
        "https://inference-api.nousresearch.com/v1/chat/completions",
        json.dumps(body).encode(),
        {"Content-Type": "application/json", "Authorization": "Bearer " + KEY,
         "User-Agent": "ainglish-python/0.2.45"})
    rec = {"model": model, "id": i["id"], "arm": arm, "outcome": "ok", "correct": None,
           "cost": 0.0, "finish_reason": None, "reasoning_tokens": 0}
    try:
        d = json.load(urllib.request.urlopen(req, timeout=180))
    except Exception as exc:
        rec["outcome"] = "error:" + type(exc).__name__
        return rec
    c = d["choices"][0]; u = d.get("usage", {})
    rec["cost"] = u.get("cost", 0.0)
    rec["finish_reason"] = c.get("finish_reason")
    rec["reasoning_tokens"] = u.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    txt = (c["message"]["content"] or "").strip()
    if not txt:
        rec["outcome"] = "empty"; return rec
    if txt[:1] not in CODES:
        rec["outcome"] = "unparsed"; return rec
    rec["answer"] = txt[:1]
    rec["correct"] = i["options"][CODES.index(txt[:1])] == i["answer"]
    return rec


jobs = [(m, i, arm) for m in CANDIDATES for i in items for arm in ("english", "ainglish")]
t0 = time.time()
with cf.ThreadPoolExecutor(max_workers=12) as ex:
    records = list(ex.map(call, jobs))
print("%d qualification cells in %.0fs\n" % (len(records), time.time() - t0))

qualified, excluded, summary = [], [], {}
for m in CANDIDATES:
    rows = [r for r in records if r["model"] == m]
    per = {}
    for arm in ("english", "ainglish"):
        live = [r for r in rows if r["arm"] == arm and r["outcome"] == "ok"]
        dead = [r for r in rows if r["arm"] == arm and r["outcome"] != "ok"]
        per[arm] = {"live": len(live), "dead": collections.Counter(r["outcome"] for r in dead),
                    "acc": (sum(1 for r in live if r["correct"]) / len(live)) if live else None}
    gap = (per["ainglish"]["acc"] - per["english"]["acc"]
           if per["ainglish"]["acc"] is not None and per["english"]["acc"] is not None else None)
    ok = gap is not None and gap >= MIN_GAP and per["ainglish"]["live"] == len(items) \
        and per["english"]["live"] == len(items)
    summary[m] = {"english": per["english"], "ainglish": per["ainglish"], "gap": gap,
                  "qualified": ok, "cost": sum(r["cost"] for r in rows)}
    (qualified if ok else excluded).append(m)
    print("%-32s english %-6s ainglish %-6s gap %-7s live %d/%d  %s" % (
        m,
        "n/a" if per["english"]["acc"] is None else "%.2f" % per["english"]["acc"],
        "n/a" if per["ainglish"]["acc"] is None else "%.2f" % per["ainglish"]["acc"],
        "n/a" if gap is None else "%+.2f" % gap,
        per["english"]["live"] + per["ainglish"]["live"], 2 * len(items),
        "QUALIFIED" if ok else "EXCLUDED"))
    for arm in ("english", "ainglish"):
        if per[arm]["dead"]:
            print("      %-9s dead: %s" % (arm, dict(per[arm]["dead"])))

print()
print("qualified:", qualified or "(none)")
print("excluded :", excluded or "(none)")
print("cost     : $%.4f" % sum(s["cost"] for s in summary.values()))
json.dump({"min_gap": MIN_GAP, "max_tokens": MAX_TOKENS, "calibration_items": len(items), "summary": summary,
           "cells": records}, open("qualification-attempt2-maxtok%d.json" % MAX_TOKENS, "w"), indent=1, sort_keys=True)
print("\nretained: qualification-attempt2-maxtok%d.json" % MAX_TOKENS)
