#!/usr/bin/env python3
"""Run the frozen they-one / they-many comprehension panel.

Item set is frozen and its digest asserted against the COMMITTED artifact before any cell is
bought -- via panel.fetch_items(url, pinned), which verifies twice (the artifact's own embedded
digest and the caller's pin). The go-unless-no runner compared a constant it had copied out of
the manifest under test, which pins an object to itself and cannot detect divergence from the
published freeze. It did diverge.
"""
import json, sys, time, pathlib, hashlib
from ainglish import panel as pn

S = pathlib.Path(__file__).parent
PINNED = open(S / "they_items_digest.txt").read().strip()
manifest = json.load(open(S / "they_manifest.json"))

ITEMS_URL = ("https://raw.githubusercontent.com/reticuli-labs/panel-artifacts/"
             "adc53aa27f8176ed914bf11bfb4b168be7a379b5/"
             "they-one-they-many-comprehension-2026-08-29/items.json")
published, digest = pn.fetch_items(ITEMS_URL, PINNED)   # verifies twice: embedded digest AND pin
if published != manifest["items"]:
    sys.exit("ABORT: the manifest about to run differs from the PUBLISHED frozen artifact")
print(f"[freeze] verified against published artifact {digest[:16]}… ({len(published)} items)", flush=True)
for ep in manifest["panel"]:
    b = pn.bounds_for(ep)
    print(f"[bounds] {ep['name']:14} max_tokens={b['max_tokens']} timeout_s={b['timeout_s']}", flush=True)
print(f"[strata] {[(s['id'], s['weight']) for s in manifest['settlement_strata']]}", flush=True)

t0 = time.time()
result = pn.run_panel(manifest)
mins = (time.time() - t0) / 60
out = S / "they_result.json"
out.write_text(json.dumps(result, indent=1, default=str))
print(f"\n[done] {mins:.1f} min -> {out}", flush=True)
if isinstance(result, dict) and "refusal" in str(result.get("kind", "")):
    print(f"[REFUSED] stage={result.get('stage')} cause={result.get('cause')}", flush=True)
    print(result.get("message", ""), flush=True)
    sys.exit(3)
if isinstance(result, dict):
    print(f"value={result.get('value')} interval=[{result.get('value_lo')}, {result.get('value_hi')}]", flush=True)
    print(f"arms={result.get('arms')}", flush=True)
    print(f"strata={json.dumps(result.get('stratum_results'))[:400]}", flush=True)
