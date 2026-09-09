#!/usr/bin/env python3
"""Rebuild the planted-defect variant corpora from plant-manifest.json and digest-pin them.

Two sets are written, because the manifest's `defect` lines under-determine three of the seven
variants (found by Sram, Colony thread b9f55449, 2026-09-08):

  variants/as-written/P1..P7  each variant derived from the manifest `defect` line ALONE
  variants/as-run/P1..P7      with the numbered-head co-edits the original run also made
                              (P5: 00000004 chain re-minted with latest; P6: cadence 24->7 on
                              00000004 and latest; P7: 00000004 laundered with latest)

The original variant directories from 2026-08-15 were NOT retained (they lived in a scratchpad
that is swept), so `as-run` is a reconstruction that reproduces results.json bit-for-bit — this
script asserts that — not the recovered original bytes. Reconstructed literal values (the P5
re-minted chain, the P6 deadline) are marked RECONSTRUCTED below.

Usage: python3 make_variants.py   (from arcaeon-exchange/; writes variants/, results_*.json, DIGESTS.txt)
"""
import copy, hashlib, json, os, shutil, sys
import datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import stranger_verify  # noqa: E402  (unmodified checker)

MANIFEST = json.load(open(os.path.join(HERE, "plant-manifest.json")))
BASE = MANIFEST["corpus_snapshot"]
EXTERNAL = {"chain": BASE["latest"]["chain"], "rows": BASE["latest"]["rows"]}  # what a stranger who cloned earlier holds
RECONSTRUCTED_CHAIN = "d3adb33fd3adb33fd3adb33fd3adb33f"      # RECONSTRUCTED: any 32-hex != the real head chain
RECONSTRUCTED_P6_DUE = "2026-08-15T00:00:00.000Z"               # RECONSTRUCTED: earlier than seq 3's deadline

def iso(s): return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
def fmt(t): return t.strftime("%Y-%m-%dT%H:%M:%S.") + f"{t.microsecond // 1000:03d}Z"

def as_written(pid, pins):
    if pid == "P1":  # delete newest pin, repoint latest at seq 3
        del pins["00000004"]; pins["latest"] = copy.deepcopy(pins["00000003"])
    elif pid == "P2":  # latest rows 5 -> 9, chain untouched
        pins["latest"]["rows"] = 9
    elif pid == "P3":  # delete pin 00000002
        del pins["00000002"]
    elif pid == "P4":  # swap bodies of 00000002 and 00000003
        pins["00000002"], pins["00000003"] = pins["00000003"], pins["00000002"]
    elif pid == "P5":  # latest chain replaced; rows unchanged
        pins["latest"]["chain"] = RECONSTRUCTED_CHAIN
    elif pid == "P6":  # seq 4 next_pin_due_by set EARLIER than seq 3's, pinned_at still advances
        pins["00000004"]["next_pin_due_by"] = RECONSTRUCTED_P6_DUE
        pins["latest"]["next_pin_due_by"] = RECONSTRUCTED_P6_DUE  # latest mirrors the head it copies
    elif pid == "P7":  # latest cadence 24 -> 8760, next_pin_due_by extended to match
        pins["latest"]["cadence_hours"] = 8760
        pins["latest"]["next_pin_due_by"] = fmt(iso(pins["latest"]["pinned_at"]) + dt.timedelta(hours=8760))
    return pins

def as_run(pid, pins):
    pins = as_written(pid, pins)
    if pid == "P5":  # co-edit: the numbered head is re-minted to the same value
        pins["00000004"]["chain"] = RECONSTRUCTED_CHAIN
    elif pid == "P6":  # co-edit: cadence 24 -> 7 on the head and on latest
        pins["00000004"]["cadence_hours"] = 7; pins["latest"]["cadence_hours"] = 7
    elif pid == "P7":  # co-edit: the numbered head is laundered alongside latest
        pins["00000004"]["cadence_hours"] = 8760
        pins["00000004"]["next_pin_due_by"] = pins["latest"]["next_pin_due_by"]
    return pins

def write_dir(d, pins):
    os.makedirs(d, exist_ok=True)
    for name, body in pins.items():
        with open(os.path.join(d, name + ".json"), "w") as f:
            f.write(json.dumps(body, indent=1, sort_keys=True) + "\n")

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def digest_dir(d, out):
    lines = []
    for name in sorted(os.listdir(d)):
        h = sha(os.path.join(d, name)); lines.append(f"{h}  {name}")
        out.append(f"{h}  {os.path.relpath(os.path.join(d, name), HERE)}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode()).hexdigest()

def build(setname, fn):
    root = os.path.join(HERE, "variants", setname)
    if os.path.isdir(root): shutil.rmtree(root)
    results, digests, filelines = {}, {}, []
    base = os.path.join(root, "BASE"); write_dir(base, copy.deepcopy(BASE)); digests["BASE"] = digest_dir(base, filelines)
    assert stranger_verify.verify(base) == [], "base snapshot must verify clean"
    for p in MANIFEST["plants"]:
        pid = p["id"]; d = os.path.join(root, pid)
        write_dir(d, fn(pid, copy.deepcopy(BASE)))
        digests[pid] = digest_dir(d, filelines)
        if pid == "P5":
            results["P5_no_external"] = stranger_verify.verify(d)
            results["P5_with_external"] = stranger_verify.verify(d, EXTERNAL)
        else:
            results[pid] = stranger_verify.verify(d)
    with open(os.path.join(root, "external_observation.json"), "w") as f:
        f.write(json.dumps(EXTERNAL, indent=1, sort_keys=True) + "\n")
    filelines.append(f"{sha(os.path.join(root, 'external_observation.json'))}  {os.path.relpath(os.path.join(root, 'external_observation.json'), HERE)}")
    return results, digests, filelines

def main():
    recorded = json.load(open(os.path.join(HERE, "results.json")))
    out_lines = []
    for setname, fn in (("as-written", as_written), ("as-run", as_run)):
        results, digests, filelines = build(setname, fn)
        with open(os.path.join(HERE, f"results_{setname.replace('-', '_')}.json"), "w") as f:
            f.write(json.dumps(results, indent=1) + "\n")
        out_lines.append(f"# {setname}: per-directory digest = sha256 of the sorted '<sha256>  <file>' lines")
        out_lines += [f"{digests[k]}  variants/{setname}/{k}/" for k in digests]
        out_lines.append(f"# {setname}: per-file")
        out_lines += filelines; out_lines.append("")
        same = {k: results.get(k) == recorded.get(k) for k in recorded}
        print(f"[{setname}] matches results.json per plant: {same}")
        if setname == "as-run":
            assert results == recorded, "as-run variants must reproduce results.json bit-for-bit"
            print("[as-run] results == results.json: ASSERTED")
    with open(os.path.join(HERE, "DIGESTS.txt"), "w") as f:
        f.write("\n".join(out_lines) + "\n")
    print("wrote variants/, results_as_written.json, results_as_run.json, DIGESTS.txt")

if __name__ == "__main__":
    main()
