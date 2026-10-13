"""Re-derive every token_delta measurement on only-if (a-d82xg4af61f3hxy0) from its served manifest (onlyif/m_<hash12>.json =
GET /api/v1/measurements/<hash>) with tiktoken; headline = max over tokenizer strata of the per-stratum mean of (ainglish - english)."""
import json, glob, tiktoken
encs = {n: tiktoken.get_encoding(n) for n in ("cl100k_base", "o200k_base", "p50k_base")}
out = {"tiktoken": tiktoken.__version__, "rows": []}
for f in sorted(glob.glob("onlyif/m_*.json")):
    d = json.load(open(f)); mani = d.get("manifest") or {}; ts = mani.get("test_set") or []
    strata = {}
    for mname in mani.get("models") or []:
        key = mname.split("/")[-1]
        if key not in encs: continue
        e = encs[key]; deltas = [len(e.encode(p["ainglish"])) - len(e.encode(p["english"])) for p in ts]
        strata[key] = sum(deltas) / len(deltas)
    out["rows"].append({"hash": d.get("manifest_hash"), "submitter": (d.get("submitter") or {}).get("name"), "filed": d.get("value"), "is_replication": d.get("is_replication"),
                        "settlement_eligible": d.get("settlement_eligible"), "counts_toward_verdict": d.get("counts_toward_verdict"), "n_pairs": len(ts), "strata": strata,
                        "rederived_headline": max(strata.values()) if strata else None, "models": mani.get("models"), "at": d.get("at")})
json.dump(out, open("onlyif/rederive.json", "w"), indent=1)
for r in out["rows"]: print(r["submitter"], r["filed"], r["rederived_headline"], r["n_pairs"], {k: round(v, 4) for k, v in r["strata"].items()}, r["settlement_eligible"], r["counts_toward_verdict"])
