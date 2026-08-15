#!/usr/bin/env python3
"""A stranger's verifier for an arcaeon-witness pin record, implemented ONLY from what the
public README documents a reader can do. No key, no privileged access, no knowledge of the
publisher's own log — that is the whole point: it models the party the witness exists to serve.

Checks, in the order a careful stranger would make them:
  C1 head monotonicity — rows never go backward across the numbered sequence
  C2 latest agreement  — latest.json equals the highest-numbered pin, byte-for-byte
  C3 seq contiguity    — seq values are 1..N with no hole
  C4 filename/seq      — 000000NN.json carries seq == NN
  C5 time monotonicity — pinned_at strictly advances with seq
  C6 deadline coherence— next_pin_due_by == pinned_at + cadence_hours, and never precedes its predecessor's
  C7 chain-vs-external — the head chain matches an EXTERNAL observation, if the stranger holds one
"""
import datetime as dt
import json
import os
import sys

def load(d):
    pins = {}
    for name in sorted(os.listdir(d)):
        if not name.endswith(".json"):
            continue
        pins[name[:-5]] = json.load(open(os.path.join(d, name)))
    return pins

def iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))

def verify(d, external_head=None):
    pins = load(d)
    numbered = sorted((k, v) for k, v in pins.items() if k != "latest")
    findings = []
    if not numbered:
        return ["C0 no numbered pins found"]

    prev_rows = None
    for name, p in numbered:
        if prev_rows is not None and p["rows"] < prev_rows:
            findings.append(f"C1 head went backward at {name}: rows {prev_rows} -> {p['rows']}")
        prev_rows = p["rows"]

    if "latest" in pins:
        head_name, head = numbered[-1]
        if pins["latest"] != head:
            diffs = [k for k in set(list(head) + list(pins["latest"]))
                     if head.get(k) != pins["latest"].get(k)]
            findings.append(f"C2 latest.json disagrees with {head_name} on {sorted(diffs)}")

    seqs = [p["seq"] for _, p in numbered]
    if seqs != list(range(1, len(seqs) + 1)):
        findings.append(f"C3 seq sequence is not contiguous 1..N: {seqs}")

    for name, p in numbered:
        if int(name) != p["seq"]:
            findings.append(f"C4 filename {name}.json carries seq {p['seq']}")

    prev_t = None
    for name, p in numbered:
        t = iso(p["pinned_at"])
        if prev_t is not None and t <= prev_t:
            findings.append(f"C5 pinned_at did not advance at {name}")
        prev_t = t

    prev_due = None
    for name, p in numbered:
        if "cadence_hours" in p and "next_pin_due_by" in p:
            want = iso(p["pinned_at"]) + dt.timedelta(hours=p["cadence_hours"])
            if abs((iso(p["next_pin_due_by"]) - want).total_seconds()) > 1:
                findings.append(f"C6 {name}: next_pin_due_by != pinned_at + {p['cadence_hours']}h")
            due = iso(p["next_pin_due_by"])
            if prev_due is not None and due < prev_due:
                findings.append(f"C6 {name}: deadline moved BACKWARD vs its predecessor")
            prev_due = due

    if external_head is not None:
        head = pins.get("latest") or numbered[-1][1]
        if head["chain"] != external_head.get("chain") or head["rows"] != external_head.get("rows"):
            findings.append("C7 head disagrees with the external observation the stranger holds")
    return findings

if __name__ == "__main__":
    ext = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None
    for f in verify(sys.argv[1], ext):
        print("  FLAG:", f)
