#!/usr/bin/env python3
"""Offline, credential-free derivation of the token_delta for this pair set."""
import json, statistics, hashlib, sys

import tiktoken

TOKENIZERS = ("cl100k_base", "o200k_base", "p50k_base")

def main():
    items = json.load(open("items.json"))["items"]
    encs = {n: tiktoken.get_encoding(n) for n in TOKENIZERS}
    per = {}
    for name, enc in encs.items():
        per[name] = statistics.mean(
            len(enc.encode(p["ainglish"])) - len(enc.encode(p["english"])) for p in items)
    # The original's declared aggregation: mean delta per tokenizer, headline is the
    # LEAST-FAVOURABLE tokenizer mean -- the smallest saving, i.e. the maximum (least negative).
    headline = max(per.values())
    eng = statistics.mean(len(encs["cl100k_base"].encode(p["english"])) for p in items)
    ain = statistics.mean(len(encs["cl100k_base"].encode(p["ainglish"])) for p in items)
    digest = hashlib.sha256(
        json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    print(f"pairs: {len(items)}   items_sha256: {digest}")
    for name, v in per.items():
        print(f"  {name:14} mean delta {v:9.5f}")
    print(f"HEADLINE (least-favourable tokenizer mean): {headline:.5f}")
    print(f"gloss profile (cl100k): english {eng:.1f} tok, ainglish {ain:.1f} tok")
    return {"headline": headline, "per": per, "digest": digest, "eng": eng, "ain": ain,
            "n": len(items)}

if __name__ == "__main__":
    main()
