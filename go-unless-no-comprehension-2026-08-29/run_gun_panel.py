#!/usr/bin/env python3
"""Run the frozen go-unless-no comprehension panel.

Run 2. Run 1 refused at the calibration gate with 0 real cells bought: gemma4-31b returned no
live answer on 3 of its 12 calibration cells. Diagnosis was truncation, not transport -- the
refusal carried transport_faults {} and a direct probe of the three failing cells showed
finish_reason 'length' with an empty string at max_tokens 1024, and a correct one-character
answer at 3072. gemma4 reasons before answering and the default bound cut it off mid-thought.

The amendment therefore raises the two transport bounds and nothing else; the item digest is
asserted identical below so the frozen set cannot drift under cover of an instrument fix.
"""
import json, sys, hashlib, time, pathlib
from ainglish import panel as pn

S = pathlib.Path(__file__).parent
FROZEN_ITEMS_DIGEST = "b96205495729d261"   # sha256[:16] of manifest['items'], frozen at 3c3da66

manifest = json.load(open(S / "gun_manifest_run2.json"))
digest = hashlib.sha256(json.dumps(manifest["items"], sort_keys=True,
                                   separators=(",", ":")).encode()).hexdigest()[:16]
if digest != FROZEN_ITEMS_DIGEST:
    sys.exit(f"ABORT: item set drifted from the freeze ({digest} != {FROZEN_ITEMS_DIGEST})")

for ep in manifest["panel"]:
    b = pn.bounds_for(ep)
    print(f"[bounds] {ep['name']:14} max_tokens={b['max_tokens']} timeout_s={b['timeout_s']}",
          flush=True)

t0 = time.time()
result = pn.run_panel(manifest)
elapsed = time.time() - t0

out = S / "gun_panel_result2.json"
out.write_text(json.dumps(result, indent=1, default=str))
print(f"\n[done] {elapsed/60:.1f} min -> {out}", flush=True)
kind = result.get("kind") if isinstance(result, dict) else None
if kind and "refusal" in str(kind):
    print(f"[REFUSED] stage={result.get('stage')} cause={result.get('cause')}", flush=True)
    print(result.get("message", ""), flush=True)
    sys.exit(3)
print(json.dumps(result, indent=1, default=str)[:2000], flush=True)
