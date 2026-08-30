#!/usr/bin/env python3
"""Vary ONLY the gloss verbosity, holding the construct and aggregation fixed.

Every variant states the same three things a will-as-promise makes explicit: the utterance binds,
failure wrongs the addressee, and release discharges it. A careful writer could file any of them
as "complete careful English". Nothing in the metric's contract says which.
"""
import json, statistics
import tiktoken

TOKENIZERS = ("cl100k_base", "o200k_base", "p50k_base")
ENCS = {n: tiktoken.get_encoding(n) for n in TOKENIZERS}

A, OBJ, PARTY, WHEN = "Priya", "the migration runbook", "the release manager", "before the freeze"

VARIANTS = {
 "terse": {
   "will-as-promise": f"{A} promises {PARTY} to complete {OBJ} {WHEN}.",
   "will-as-plan":    f"{A} plans to complete {OBJ} {WHEN}, and may change it.",
   "will-as-forecast":f"{A} expects {OBJ} to be complete {WHEN}.",
 },
 "medium": {
   "will-as-promise": f"{A} promises {PARTY} to complete {OBJ} {WHEN}; the promise binds, and failing it without release wrongs {PARTY}.",
   "will-as-plan":    f"{A} plans to complete {OBJ} {WHEN}; the plan may change, and {A} owes {PARTY} notice if it does.",
   "will-as-forecast":f"{A} predicts {OBJ} will be complete {WHEN}; this claims no control and creates no obligation.",
 },
 "verbose": {
   "will-as-promise": f"{A} undertakes to {PARTY} to complete {OBJ} {WHEN}; saying so is itself what binds {A}, and if it is not done and {PARTY} has not released {A} from it, {A} has wronged {PARTY}.",
   "will-as-plan":    f"{A} currently intends to complete {OBJ} {WHEN}, and tells {PARTY} so; the intention may still change, and if it does {A} owes {PARTY} notice of the change, but the saying of it binds {A} to nothing.",
   "will-as-forecast":f"{A} predicts to {PARTY} that {OBJ} will be complete {WHEN}; the prediction is about how things will turn out, {A} claims no control over whether it happens, and {A} takes on no obligation by saying it.",
 },
}
MARKED = {
 "will-as-promise": f"{A} will-as-promise complete {OBJ} {WHEN} to {PARTY}.",
 "will-as-plan":    f"{A} will-as-plan complete {OBJ} {WHEN}, told to {PARTY}.",
 "will-as-forecast":f"{A} will-as-forecast {OBJ} complete {WHEN}, told to {PARTY}.",
}

print(f"{'gloss':9} {'eng tok':>8} {'ain tok':>8} {'cl100k':>9} {'o200k':>9} {'p50k':>9} {'HEADLINE':>10}")
for name, forms in VARIANTS.items():
    per = {}
    for tname, enc in ENCS.items():
        per[tname] = statistics.mean(
            len(enc.encode(MARKED[f])) - len(enc.encode(forms[f])) for f in forms)
    eng = statistics.mean(len(ENCS["cl100k_base"].encode(t)) for t in forms.values())
    ain = statistics.mean(len(ENCS["cl100k_base"].encode(MARKED[f])) for f in forms)
    print(f"{name:9} {eng:8.1f} {ain:8.1f} {per['cl100k_base']:9.2f} {per['o200k_base']:9.2f} "
          f"{per['p50k_base']:9.2f} {max(per.values()):10.2f}")
print()
print("Same construct. Same aggregation rule. Same marked forms. Only the gloss changed.")
