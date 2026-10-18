import json, hashlib, time, urllib.request, base58
from nacl.bindings import crypto_core_ed25519_is_valid_point as on_curve
PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"; RPC = "https://api.mainnet-beta.solana.com"
def pda(seeds, program):
    pb = base58.b58decode(program)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pb + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return base58.b58encode(h).decode(), bump
def le64(n): return n.to_bytes(8, "little")
def rpc(m, p):
    req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode())
R = json.load(open("record_pda_results.json")); arts = sorted({r["address"] for r in R["pages"]})
bad = [r for r in R["pages"] if r["derived_matches_served"] is False]; good = [r for r in R["pages"] if r["derived_matches_served"]][:2]
out = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "rows": []}
import base64
for r in bad + good:
    rec = r["record_served"]; row = {"artifact": r["artifact"], "address": r["address"], "page": r["page"], "version": r["version"], "record": rec, "derived_in_first_pass": r["derived_matches_served"]}
    ai = rpc("getAccountInfo", [rec, {"encoding": "base64"}])["result"]["value"]
    if ai is None: row["onchain"] = "account does not exist"
    else:
        data = base64.b64decode(ai["data"][0]); row["onchain"] = {"owner": ai["owner"], "owner_is_program": ai["owner"] == PROGRAM, "lamports": ai["lamports"], "data_len": len(data), "data_1_33_b58": base58.b58encode(data[1:33]).decode(), "data_1_33_is_this_artifact": base58.b58encode(data[1:33]).decode() == r["address"], "data_111_143_hex": data[111:143].hex() if len(data) >= 143 else None, "content_served": r["content"], "fp_equals_content": (data[111:143].hex() == r["content"]) if len(data) >= 143 else None, "u64_at_33": int.from_bytes(data[33:41], "little") if len(data) >= 41 else None}
    if not r["derived_matches_served"]:
        # wider seq, and every other artifact's key
        ab = base58.b58decode(r["address"]); hit = next((s for s in range(4096, 65536) if pda([b"record", ab, le64(s)], PROGRAM)[0] == rec), None); row["seq_4096_65535"] = hit
        cross = [(a, s) for a in arts if a != r["address"] for s in range(0, 64) if pda([b"record", base58.b58decode(a), le64(s)], PROGRAM)[0] == rec]; row["cross_artifact_hits"] = cross
        if isinstance(row["onchain"], dict):
            other = row["onchain"]["data_1_33_b58"]
            try: ob = base58.b58decode(other); hit2 = next((s for s in range(0, 4096) if pda([b"record", ob, le64(s)], PROGRAM)[0] == rec), None); row["derives_under_data_1_33_key_seq"] = hit2
            except Exception as e: row["derives_under_data_1_33_key_seq"] = f"err {e}"
    out["rows"].append(row); print(json.dumps(row)[:900]); time.sleep(0.4)
json.dump(out, open("record_pda2_results.json", "w"), indent=1)
