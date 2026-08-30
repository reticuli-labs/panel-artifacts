#!/usr/bin/env python3
"""Does reasoning_effort:"none" degrade a remote reader? Per-cell records retained.

The first pass of this reported +60.0pp by dividing BOTH arms by the PLANNED n of 10, while a
transport fault had killed one ainglish cell — a censored denominator, which is the exact failure
the panel harness's yield guard exists to prevent. Live n is now recorded per arm and every cell is
written out, so the arithmetic is re-derivable rather than asserted.
"""
import hashlib, json, os, sys, urllib.request, random, collections, concurrent.futures as cf, time

REDERIVE = "--rederive" in sys.argv[1:]
if not REDERIVE and "--run" not in sys.argv[1:]:
    sys.exit("usage: run.py --rederive   (offline, zero network, reads the retained cells.json)\n"
             "       run.py --run        (SPENDS paid inference and writes a NEW cells file)\n\n"
             "Defaulting to neither on purpose: the first version of this script re-ran on every\n"
             "invocation and overwrote cells.json, so 'reproducing' the published result destroyed\n"
             "the evidence it was reproducing and cost money to do it.")

KEY = os.environ["NOUS_API_KEY"] if not REDERIVE else None
MODEL = "deepseek/deepseek-v4-flash"
ITEMS = json.load(open("../none-of-not-all-of-comprehension-2026-08-30/items.json"))
random.Random(11).shuffle(ITEMS)
SAMPLE = ITEMS[:10]                    # same 10 items and seed as the first pass, for comparability
CODES = "ABC"


def prompt_for(i, arm):
    ch = "\n".join(f"{c}: {o}" for c, o in zip(CODES, i["options"]))
    return (f"Read this message written by one agent to another:\n\n---\n{i[arm]}\n---\n\n"
            f"Question: {i['question']}\nChoices:\n{ch}\n"
            "Answer with EXACTLY one choice code and nothing else.")


def call(job):
    item, arm, effort = job
    body = {"model": MODEL, "messages": [{"role": "user", "content": prompt_for(item, arm)}],
            "max_tokens": 1024, "temperature": 0}
    if effort is not None:
        body["reasoning_effort"] = effort
    req = urllib.request.Request(
        "https://inference-api.nousresearch.com/v1/chat/completions",
        json.dumps(body).encode(),
        {"Content-Type": "application/json", "Authorization": "Bearer " + KEY,
         "User-Agent": "ainglish-python/0.2.44"})
    rec = {"item_id": item["id"], "arm": arm, "effort": effort, "answer": None,
           "correct": None, "outcome": "ok", "reasoning_tokens": 0, "cost": 0.0}
    try:
        d = json.load(urllib.request.urlopen(req, timeout=180))
    except Exception as exc:
        rec["outcome"] = "error:" + type(exc).__name__
        return rec
    c = d["choices"][0]; u = d.get("usage", {})
    rec["reasoning_tokens"] = u.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
    rec["cost"] = u.get("cost", 0.0)
    txt = (c["message"]["content"] or "").strip()
    rec["finish_reason"] = c.get("finish_reason")
    if not txt:
        rec["outcome"] = "empty"
        return rec
    rec["answer"] = txt[:1]
    if txt[:1] not in CODES:
        rec["outcome"] = "unparsed"
        return rec
    rec["correct"] = item["options"][CODES.index(txt[:1])] == item["answer"]
    return rec


if REDERIVE:
    # Offline: recompute every published figure from the retained immutable cells. No key, no
    # network, no writes. This is what "re-derive" has to mean for a paid experiment -- otherwise
    # the only way to check a number is to buy it again, and checking it destroys it.
    blob = open("cells.json", "rb").read()
    print("cells.json sha256: %s" % hashlib.sha256(blob).hexdigest())
    records = json.load(open("cells.json"))["cells"]
    print("%d retained cells, zero network calls, nothing written\n" % len(records))
else:
    jobs = [(i, arm, eff) for eff in (None, "none") for i in SAMPLE for arm in ("english", "ainglish")]
    t0 = time.time()
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        records = list(ex.map(call, jobs))
    print("%d planned cells in %.0fs\n" % (len(records), time.time() - t0))

summary = {}
for effort in (None, "none"):
    rows = [r for r in records if r["effort"] == effort]
    arm_stats = {}
    for arm in ("english", "ainglish"):
        arm_rows = [r for r in rows if r["arm"] == arm]
        live = [r for r in arm_rows if r["outcome"] == "ok"]
        dead = [r for r in arm_rows if r["outcome"] != "ok"]
        arm_stats[arm] = {
            "planned_n": len(arm_rows), "live_n": len(live),
            "dead": collections.Counter(r["outcome"] for r in dead),
            "correct": sum(1 for r in live if r["correct"]),
            "accuracy": (sum(1 for r in live if r["correct"]) / len(live)) if live else None,
        }
    e, a = arm_stats["english"], arm_stats["ainglish"]
    delta = (a["accuracy"] - e["accuracy"]) * 100 if e["accuracy"] is not None and a["accuracy"] is not None else None
    label = "ABSENT (provider default)" if effort is None else '"none"'
    print("=== reasoning_effort %s" % label)
    for arm, s in arm_stats.items():
        print("   %-9s planned %2d  live %2d  correct %2d  acc %5.1f%%  dead %s"
              % (arm, s["planned_n"], s["live_n"], s["correct"], 100 * s["accuracy"], dict(s["dead"]) or "{}"))
    print("   delta over LIVE cells: %+0.1fpp | reasoning tokens %d | cost $%.5f\n"
          % (delta, sum(r["reasoning_tokens"] for r in rows), sum(r["cost"] for r in rows)))
    summary[label] = {"arms": {k: {kk: (dict(vv) if isinstance(vv, collections.Counter) else vv)
                                   for kk, vv in v.items()} for k, v in arm_stats.items()},
                      "delta_pp": delta}

if REDERIVE:
    sys.exit(0)          # never write over the retained artifact
json.dump({"model": MODEL, "items_source": "none-of-not-all-of-comprehension-2026-08-30/items.json",
           "items_sha256": "bce44c496978e6a229e45824b6fa2f7828b1380873b6944c0102f0f5d447813b",
           "sample_seed": 11, "sample_n": len(SAMPLE), "summary": summary, "cells": records},
          open("cells-%s.json" % time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()), "w"), indent=1, sort_keys=True)
print("per-cell records written to cells.json")
