#!/usr/bin/env python3
"""Compute the token_delta under Dexagon's declared estimand. Run AFTER the freeze commit."""
import hashlib, json, statistics
import tiktoken

PIN = "654a12c56c6091dac58683e3e8368b27dbcaa4f018eb4a4e2ded13f2dceac366"
MODELS = ["cl100k_base", "o200k_base", "p50k_base"]

raw = open("items.json", "rb").read()
got = hashlib.sha256(raw).hexdigest()
assert got == PIN, "items drifted since freeze: %s" % got
items = json.loads(raw)
print("items verified against the freeze pin:", got[:16], "|", len(items), "pairs")
print("tiktoken:", tiktoken.__version__)
assert tiktoken.__version__ == "0.13.0", "must match the original's declared provenance"
print()

per_member = {}
for model in MODELS:
    enc = tiktoken.get_encoding(model)
    deltas = [len(enc.encode(i["ainglish"])) - len(enc.encode(i["english"])) for i in items]
    per_member[model] = statistics.fmean(deltas)
    by_form = {}
    for i, d in zip(items, deltas):
        by_form.setdefault(i["form"], []).append(d)
    print("%-12s mean %+7.3f   rule %+7.3f   forecast %+7.3f   range [%d, %d]" % (
        model, per_member[model],
        statistics.fmean(by_form["should-as-rule"]),
        statistics.fmean(by_form["should-as-forecast"]),
        min(deltas), max(deltas)))

vals = list(per_member.values())
headline = max(vals)          # "least-favourable maximum tokenizer mean"
print()
print("per-tokenizer means :", {k: round(v, 3) for k, v in per_member.items()})
print("headline (max/least-favourable): %+0.3f" % headline)
print("value_lo (min)                 : %+0.3f" % min(vals))

ORIG = -11
tol = max(0.1 * abs(ORIG), 0.02)
print()
print("original %+d, tolerance +/-%.2f -> agreement window [%.2f, %.2f]" % (ORIG, tol, ORIG - tol, ORIG + tol))
print("difference: %+0.3f" % (headline - ORIG))
print("AGREES WITHIN TOLERANCE:", abs(headline - ORIG) <= tol)
