"""Derive each served page's version-record address from the program's own seed rule and compare to the record the page names.
Rule read from the relay package sdk/index.mjs line 73 (tarball sha256 013076da..., downloaded 2026-10-18): recordAddress(a, seq) = findProgramAddress(['record', artifact_pubkey, u64_le(seq)], MAINNET_PROGRAM). The gateway serves no 'seq' field, so seq is searched over 0..4095 per page and the matching value reported; a page whose record no seq reproduces is a mismatch."""
import json, hashlib, time, urllib.request, base58
from nacl.bindings import crypto_core_ed25519_is_valid_point as on_curve
PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"; GW = "https://gateway.artifactcouncil.com"
def gw(p):
    with urllib.request.urlopen(urllib.request.Request(GW + p, headers={"Accept": "application/json", "User-Agent": "reticuli/1"}), timeout=60) as r: return json.loads(r.read().decode())
def pda(seeds, program):
    pb = base58.b58decode(program)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pb + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return base58.b58encode(h).decode(), bump
    raise ValueError("no bump")
def le64(n): return n.to_bytes(8, "little")
# control: the agent PDA for my own id must equal a known served address? we check the rule itself with the artifact's own seed instead: artifactAddress(n) = pda('artifact', le64(n)) should reproduce served artifact addresses for some n
out = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "program": PROGRAM, "rule": "['record', artifact, u64_le(seq)] (sdk/index.mjs:73)", "pages": [], "artifact_rule_check": []}
lst = gw("/v2/artifacts"); arts = lst if isinstance(lst, list) else (lst.get("artifacts") or lst.get("items"))
for a0 in arts:
    addr = a0.get("address") or a0.get("id")
    hit = next(((n, b) for n in range(0, 4096) for (p, b) in [pda([b"artifact", le64(n)], PROGRAM)] if p == addr), None)
    out["artifact_rule_check"].append({"address": addr, "name": a0.get("name"), "artifact_seed_n": hit[0] if hit else None, "bump": hit[1] if hit else None})
    a = gw(f"/v2/artifacts/{addr}")
    for p in a.get("pages") or []:
        rec = p.get("record"); row = {"artifact": a.get("name"), "address": addr, "page": p.get("page"), "version": p.get("version"), "record_served": rec, "upload": p.get("upload"), "content": p.get("content")}
        if rec:
            ab = base58.b58decode(addr); found = None
            for seq in range(0, 4096):
                d, bump = pda([b"record", ab, le64(seq)], PROGRAM)
                if d == rec: found = (seq, bump); break
            row.update({"derived_matches_served": found is not None, "seq": found[0] if found else None, "bump": found[1] if found else None, "seq_equals_version": (found[0] == p.get("version")) if found else None, "seq_equals_page": (found[0] == p.get("page")) if found else None})
            # negative control: the neighbouring seq must not reproduce it
            if found: row["control_seq_plus_1_differs"] = pda([b"record", ab, le64(found[0] + 1)], PROGRAM)[0] != rec
        else: row["derived_matches_served"] = None; row["note"] = "page names no record"
        out["pages"].append(row); print(json.dumps({k: row[k] for k in row if k not in ("content", "upload")}))
    time.sleep(0.5)
json.dump(out, open("record_pda_results.json", "w"), indent=1)
ok = sum(1 for r in out["pages"] if r.get("derived_matches_served") is True); print("DONE pages", len(out["pages"]), "derived==served", ok, "no record", sum(1 for r in out["pages"] if r.get("derived_matches_served") is None), "| artifact rule hits", sum(1 for r in out["artifact_rule_check"] if r["artifact_seed_n"] is not None), "/", len(out["artifact_rule_check"]))
