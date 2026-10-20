#!/usr/bin/env python3
"""Reader tool: the frame fold reimplemented from META.json `frame_recipe` alone, run on the five frozen texts in this directory. Every backward root must equal `backward_fold_gives` and every forward root `forward_fold_would_give`; the page texts' sha256 must equal their META rows. Exit 0 = all match. Usage: python3 fold_check.py [--json]. No network, no writes unless --json (writes fold_calibration_<date>.json beside it)."""
import json, hashlib, struct, sys, os, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(os.path.join(D, "META.json"), encoding="utf-8")); R = M["frame_recipe"]
assert R["header_bytes"] == 12 and R["chunk_bytes"] == 3000 and R["link"] == "sha256(chunk + link)"
def frame(text):
    b = text.encode("utf-8"); n = len(b)
    return bytes.fromhex("28b52ffda0") + struct.pack("<I", n) + struct.pack("<I", n * 8 + 1)[:3] + b   # magic, descriptor, size LE32, (count*8+1) LE24
def fold(chunks, backward):
    link = bytes(32)
    for c in (reversed(chunks) if backward else chunks): link = hashlib.sha256(c + link).digest()
    return link.hex()
FILES = {"page1_v11": "page1_v11_served.md", "page3_v3": "page3_v3.md", "page3_v4": "page3_v4_draft.md", "page1_repoint_to_v3": "page1_repoint_to_v3.md", "page1_repoint_to_v4": "page1_repoint_to_v4.md"}
out, ok = {}, True
for k, f in FILES.items():
    t = open(os.path.join(D, f), encoding="utf-8").read(); fr = frame(t); cs = [fr[i:i + 3000] for i in range(0, len(fr), 3000)]
    back, fwd, sha = fold(cs, True), fold(cs, False), hashlib.sha256(t.encode("utf-8")).hexdigest()
    meta = M.get(k) or {}
    good = back == R["backward_fold_gives"][k] and fwd == R["forward_fold_would_give"][k] and (not meta.get("sha256_text") or sha == meta["sha256_text"]) and (not meta.get("fingerprint_if_filed") or back == meta["fingerprint_if_filed"])
    ok = ok and good
    out[k] = {"file": f, "chars": len(t), "bytes": len(t.encode("utf-8")), "frame_bytes": len(fr), "chunks": len(cs), "header_hex": fr[:12].hex(), "sha256_text": sha, "backward_root": back, "forward_root": fwd, "matches_meta": good}
    print(f"{'ok  ' if good else 'FAIL'} {k:22s} chars {len(t):5d} frame {len(fr):5d} B {len(cs)} chunks hdr {fr[:12].hex()} back {back[:8]} fwd {fwd[:8]} sha {sha[:8]}")
print("ALL MATCH" if ok else "MISMATCH")
if "--json" in sys.argv:
    p = os.path.join(D, f"fold_calibration_{dt.date.today().isoformat()}.json"); json.dump({"ran": dt.datetime.now(dt.timezone.utc).isoformat()[:19] + "Z", "all_match": ok, "texts": out}, open(p, "w"), indent=1); print("wrote", os.path.basename(p))
sys.exit(0 if ok else 1)
