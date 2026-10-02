"""Apply plan.md (rev 2: the first run read the wrong result key, `value` instead of `floor`, and did not normalise legacy encoding names; rule unchanged): fetch each sampled measurement, recompute the headline from manifest.test_set with the SDK's
token_delta, classify match / mismatch / not-derivable. Writes results.json beside this file."""
import json, time, sys, traceback
from ainglish.client import AinglishClient
from ainglish.token_measurement import token_delta
c = AinglishClient(); S = json.load(open("sample.json")); out = []
def pairs_of(ts):
    rows = ts.get("pairs") if isinstance(ts, dict) else ts
    if not isinstance(rows, list): return None
    P = []
    for r in rows:
        if isinstance(r, dict) and isinstance(r.get("english"), str) and isinstance(r.get("ainglish"), str): P.append({"english": r["english"], "ainglish": r["ainglish"]})
        elif isinstance(r, (list, tuple)) and len(r) == 2 and all(isinstance(x, str) for x in r): P.append({"english": r[0], "ainglish": r[1]})
        else: return None
    return P
for h in S["manifest_hashes"]:
    rec = {"manifest_hash": h}
    try:
        m = c.get(f"/api/v1/measurements/{h}", auth=False); m = m.get("measurement", m)
        man = m.get("manifest") or {}; rec.update(filed=m.get("value"), proposal=(m.get("proposal") or {}).get("slug") if isinstance(m.get("proposal"), dict) else m.get("proposal"), submitter=(m.get("submitter") or {}).get("sub") if isinstance(m.get("submitter"), dict) else m.get("submitter"), at=m.get("at"), backfilled=(m.get("attempt") or {}).get("backfilled"))
        import re as _re
        def norm(n):
            # legacy rows name encodings as tiktoken/cl100k_base, cl100k_base@0.13.0, cl100k_base@vocab, raw-api-tiktoken@cl100k_base
            n = str(n); n = n.split("/")[-1] if "/" in n and not n.startswith("raw-api") else n
            if n.startswith("raw-api-tiktoken@"): n = n.split("@", 1)[1]
            n = n.split("@")[0]
            return n
        models_raw = man.get("models"); models = [norm(x) for x in models_raw] if isinstance(models_raw, list) else models_raw
        rec["models_raw"] = models_raw
        ts = man.get("test_set"); P = pairs_of(ts) if ts is not None else None
        if not models or not P: rec.update(cls="not-derivable", why="no models" if not models else "no usable test_set", manifest_keys=sorted(man.keys())); out.append(rec); continue
        try:
            res = token_delta(P, models)
        except Exception as e:
            rec.update(cls="not-derivable", why=f"token_delta: {type(e).__name__}: {str(e)[:120]}", models=models, pairs=len(P)); out.append(rec); continue
        derived = res.get("floor") if isinstance(res, dict) else res
        rec.update(derived=derived, models=models, pairs=len(P), raw_keys=sorted(res.keys())[:12] if isinstance(res, dict) else None)
        try: d = abs(float(derived) - float(rec["filed"]))
        except Exception: d = None
        rec.update(cls=("match" if d is not None and d <= 0.01 else "mismatch"), diff=d)
    except Exception as e:
        rec.update(cls="fetch-error", why=f"{type(e).__name__}: {str(e)[:160]}")
    out.append(rec); print(rec["cls"], h[:8], "filed", rec.get("filed"), "derived", rec.get("derived"), rec.get("why", ""), flush=True)
    time.sleep(0.5)
import collections
summary = dict(collections.Counter(r["cls"] for r in out))
json.dump({"kind": "reticuli.token-rederive-sample.results.v1", "ran_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "summary": summary, "rows": out}, open("results.json", "w"), indent=1, default=str)
print("SUMMARY", summary)
