#!/usr/bin/env python3
"""Does the register's replication independence check look at the EVIDENCE or at the envelope?

Settlement counts a replication when it carries a different `manifest_hash` from the original it
names. The manifest hash covers the whole envelope -- environment, estimand, source notes -- not
just the answer-bearing items. So a row that copies the original's `test_set` verbatim and changes
an environment field hashes differently and is counted as independent confirmation.

This scans every replication that names an original, recomputes BOTH item-list digests, and reports
how many "independent" replications are byte-identical in the only part that determines the value.

Swept over the whole population and reconciled against the envelope `total`.
"""
import collections, hashlib, json, sys
from ainglish.client import AinglishClient

c = AinglishClient()
total = c.measurements(limit=1).get("total")
rows = list(c.iter_measurements())
if total is not None and len(rows) < total:
    sys.exit("SHORTFALL: iterated %d of %s — refusing to report a rate over a partial sweep"
             % (len(rows), total))
print("population: %d rows (envelope total %s) — reconciled" % (len(rows), total))

by_hash = {r.get("manifest_hash"): r for r in rows if r.get("manifest_hash")}
reps = [r for r in rows if r.get("is_replication") and r.get("replicates_hash")]
print("replications naming an original: %d" % len(reps))


def items_digest(manifest_hash, cache={}):
    if manifest_hash in cache:
        return cache[manifest_hash]
    try:
        man = c.measurement(manifest_hash).get("manifest") or {}
    except Exception:
        cache[manifest_hash] = None
        return None
    items = man.get("test_set")
    if items is None:
        items = man.get("pairs")
    if not isinstance(items, list) or not items:
        cache[manifest_hash] = None          # items held by URL, or none inline
        return None
    blob = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    cache[manifest_hash] = (hashlib.sha256(blob.encode()).hexdigest(), len(items))
    return cache[manifest_hash]


identical, distinct, unreadable = [], [], 0
for r in reps:
    a = items_digest(r["manifest_hash"])
    b = items_digest(r["replicates_hash"])
    if a is None or b is None:
        unreadable += 1
        continue
    (identical if a[0] == b[0] else distinct).append((r, a, b))

comparable = len(identical) + len(distinct)
print("comparable pairs (both item lists inline): %d   (unreadable/URL-held: %d)"
      % (comparable, unreadable))
if comparable:
    print()
    print("replications whose items are BYTE-IDENTICAL to the original they 'confirm': %d/%d (%.0f%%)"
          % (len(identical), comparable, 100 * len(identical) / comparable))
    print()
    who = collections.Counter((r.get("submitter") or {}).get("name") for r, _, _ in identical)
    print("by submitter:", dict(who.most_common()))
    print()
    print("sample:")
    for r, a, b in identical[:6]:
        print("  %-14s %-22s value=%-8s pairs=%d  items=%s  manifest=%s vs original %s"
              % ((r.get("submitter") or {}).get("name"), r["metric"][:22], r["value"], a[1],
                 a[0][:12], r["manifest_hash"][:10], r["replicates_hash"][:10]))
