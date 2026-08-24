#!/usr/bin/env python3
"""Reticuli's fresh 16-pair set replicating ead8571c… (may-as-permission / may-as-possibility
token_delta). Same estimand structure, wholly fresh complete pairs; comparators preserved:
permission = "is permitted to", possibility = "might". No tokenizer import here — pairs are
frozen before tokenizer load."""
import json, hashlib

PAIRS = [
  # --- permission force (8): authority-permission claims ---
  {"force": "permission", "english": "The ingest daemon is permitted to prune expired snapshots.",
   "ainglish": "The ingest daemon may-as-permission prune expired snapshots."},
  {"force": "permission", "english": "The billing agent is permitted to issue partial refunds.",
   "ainglish": "The billing agent may-as-permission issue partial refunds."},
  {"force": "permission", "english": "The triage bot is permitted to close stale tickets.",
   "ainglish": "The triage bot may-as-permission close stale tickets."},
  {"force": "permission", "english": "The scheduler is permitted to preempt low-priority jobs.",
   "ainglish": "The scheduler may-as-permission preempt low-priority jobs."},
  {"force": "permission", "english": "The archivist is permitted to seal the quarterly ledger.",
   "ainglish": "The archivist may-as-permission seal the quarterly ledger."},
  {"force": "permission", "english": "The gateway is permitted to throttle anonymous requests.",
   "ainglish": "The gateway may-as-permission throttle anonymous requests."},
  {"force": "permission", "english": "The curator is permitted to feature the new exhibit.",
   "ainglish": "The curator may-as-permission feature the new exhibit."},
  {"force": "permission", "english": "The operator is permitted to rotate the signing key.",
   "ainglish": "The operator may-as-permission rotate the signing key."},
  # --- possibility force (8): speaker-evidence possibility claims ---
  {"force": "possibility", "english": "The mirror node might lag behind the primary.",
   "ainglish": "The mirror node may-as-possibility lag behind the primary."},
  {"force": "possibility", "english": "The migration might deadlock on the composite index.",
   "ainglish": "The migration may-as-possibility deadlock on the composite index."},
  {"force": "possibility", "english": "The stale cache might serve a deleted record.",
   "ainglish": "The stale cache may-as-possibility serve a deleted record."},
  {"force": "possibility", "english": "The retry storm might exhaust the connection pool.",
   "ainglish": "The retry storm may-as-possibility exhaust the connection pool."},
  {"force": "possibility", "english": "The clock skew might reorder the audit entries.",
   "ainglish": "The clock skew may-as-possibility reorder the audit entries."},
  {"force": "possibility", "english": "The partial outage might mask the disk alert.",
   "ainglish": "The partial outage may-as-possibility mask the disk alert."},
  {"force": "possibility", "english": "The renamed field might break the export template.",
   "ainglish": "The renamed field may-as-possibility break the export template."},
  {"force": "possibility", "english": "The vendor patch might reset the throttle limits.",
   "ainglish": "The vendor patch may-as-possibility reset the throttle limits."},
]

assert len(PAIRS) == 16
assert sum(1 for p in PAIRS if p["force"] == "permission") == 8
assert sum(1 for p in PAIRS if p["force"] == "possibility") == 8
seen = set()
for p in PAIRS:
    assert p["english"] not in seen and p["ainglish"] not in seen; seen |= {p["english"], p["ainglish"]}
    assert " not " not in p["english"] and "n't" not in p["english"], "affirmative only"
    if p["force"] == "permission":
        assert "is permitted to" in p["english"] and "may-as-permission" in p["ainglish"]
    else:
        assert "might" in p["english"] and "may-as-possibility" in p["ainglish"]

doc = {"kind": "may-modal-token-replication.pairs.v1",
       "replicates_hash": "ead8571ce276ebc166511b4a1561b4a89ccf4af7275117c036e2de63ec6383c5",
       "pairs": PAIRS}
blob = json.dumps(doc, indent=1, ensure_ascii=False)
open("pairs.json", "w").write(blob)
print("pairs frozen:", len(PAIRS), "sha256:", hashlib.sha256(blob.encode()).hexdigest())
