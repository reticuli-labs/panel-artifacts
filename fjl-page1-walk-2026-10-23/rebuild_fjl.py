"""Independent chain rebuild of an AC upload (my own code; layout learned from veil-hidden-link's rebuild_upload.py v2, checked here by calibration against pages the gateway already serves).
Read-only: getSignaturesForAddress + getTransaction on a public RPC. Identifiers come from state.json (gateway read), never typed.
Differences from veil's script: chunks keyed by (signature, instruction index) not by bytes; the second instruction byte is recorded per chunk and tried as an on-chain order; the zstd frame is decoded by the zstd CLI (a real decoder), not a raw-block parser."""
import json, time, struct, hashlib, itertools, subprocess, urllib.request, urllib.error, datetime as dt, sys
S = json.load(open("state.json")); PROGRAM = S["root"]["program"]; RPC = "https://api.mainnet-beta.solana.com"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    b = n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""
    return b"\0" * (len(s) - len(s.lstrip("1"))) + b
def rpc(method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    for i in range(10):
        try:
            with urllib.request.urlopen(urllib.request.Request(RPC, data=body, headers={"Content-Type": "application/json", "User-Agent": "reticuli-ac/1"}), timeout=60) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(4 + 3 * i); continue
            raise
    raise SystemExit("rpc 429 x10")
def root_of(seq):
    link = bytes(32)
    for c in reversed(seq): link = hashlib.sha256(c + link).digest()
    return link.hex()
def rebuild(label, upload, content, expect_text=None, expect_sha=None):
    R = {"label": label, "upload": upload, "content": content, "rpc": RPC, "read_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    sigs = rpc("getSignaturesForAddress", [upload, {"limit": 1000}])["result"]; R["signatures_total"] = len(sigs); R["signatures_err"] = sum(1 for s in sigs if s.get("err"))
    chunks = []  # dict per chunk-write instruction
    for s in sigs:
        if s.get("err"): continue
        tx = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1, "commitment": "finalized"}])["result"]
        msg = tx["transaction"]["message"]; keys = msg["accountKeys"]
        for i, ix in enumerate(msg["instructions"]):
            if keys[ix["programIdIndex"]] != PROGRAM: continue
            d = b58d(ix["data"])
            if not d or d[0] != 3: continue
            n = struct.unpack("<I", d[2:6])[0]; c = d[6:6 + n]
            chunks.append({"sig": s["signature"], "slot": tx["slot"], "blockTime": tx.get("blockTime"), "ix": i, "byte1": d[1], "declared_len": n, "got_len": len(c), "trailing": d[6 + n:].hex(), "sha": hashlib.sha256(c).hexdigest()[:16], "bytes": c})
    R["chunk_writes"] = len(chunks); R["tags_seen"] = sorted({d for d in []})
    landed = sorted(chunks, key=lambda x: (x["slot"], x["ix"]))
    R["chunks"] = [{k: v for k, v in c.items() if k != "bytes"} for c in landed]
    seqs = {"landed": [c["bytes"] for c in landed], "byte1_order": [c["bytes"] for c in sorted(chunks, key=lambda x: x["byte1"])], "byte1_desc": [c["bytes"] for c in sorted(chunks, key=lambda x: -x["byte1"])]}
    R["match"] = {k: root_of(v) == content for k, v in seqs.items()}
    seq = next((v for k, v in seqs.items() if R["match"][k]), None)
    if seq is None and len(chunks) <= 8:
        seq = next((list(p) for p in itertools.permutations(seqs["landed"]) if root_of(p) == content), None); R["match"]["permutation"] = seq is not None
    R["chain_matches_content"] = seq is not None
    if seq is None: print(label, "NO MATCH", json.dumps({k: v for k, v in R.items() if k != "chunks"})); return R
    frame = b"".join(seq); fn = f"frame_{label}.zst"; open(fn, "wb").write(frame); R["frame_bytes"] = len(frame); R["frame_magic"] = frame[:4].hex(); R["frame_sha256"] = hashlib.sha256(frame).hexdigest()
    p = subprocess.run(["zstd", "-d", "-c", "-q", fn], capture_output=True); R["zstd_rc"] = p.returncode; R["zstd_err"] = p.stderr.decode()[:300]
    text = p.stdout; open(f"text_{label}.txt", "wb").write(text)
    R["text_bytes"] = len(text); R["text_chars"] = len(text.decode("utf-8")); R["text_sha256"] = hashlib.sha256(text).hexdigest()
    if expect_text is not None: R["equals_served_text"] = text == expect_text.encode("utf-8"); R["served_chars"] = len(expect_text)
    if expect_sha is not None: R["equals_expected_sha"] = R["text_sha256"] == expect_sha
    print(label, json.dumps({k: v for k, v in R.items() if k != "chunks"})); print("   chunks:", [(c["byte1"], c["got_len"], c["slot"], c["sha"][:8], c["trailing"]) for c in R["chunks"]])
    return R
out = {}
# ---- main (10-23): calibrate on the served FJL p1 v1, then rebuild the page-1 content proposal's upload from chain ----
out = {}
fjl = S["FJL"]["pages"][0]; out["fjl_p1_v1"] = rebuild("fjl_p1_v1", fjl["upload"], fjl["content"], expect_text=fjl["text"])
assert out["fjl_p1_v1"].get("equals_served_text") is True, "calibration failed"
props = [p for p in S["FJL"]["proposals"] if (p.get("payload") or {}).get("kind") == "content"]; assert len(props) == 1, len(props)
prop = props[0]; pl = prop["payload"]; assert pl["page"] == 1
out["fjl_p1_proposal"] = rebuild("fjl_p1_proposal", pl["upload"], pl["content"]); out["fjl_p1_proposal"]["proposal"] = prop["address"]; out["fjl_p1_proposal"]["title"] = pl.get("title")
json.dump(out, open("rebuild_results.json", "w"), indent=1)
print("\nPROPOSAL TEXT chain_matches_content =", out["fjl_p1_proposal"]["chain_matches_content"], "| chars", out["fjl_p1_proposal"].get("text_chars"), "| sha256", out["fjl_p1_proposal"].get("text_sha256"))
