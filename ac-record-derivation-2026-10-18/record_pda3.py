import json, hashlib, time, urllib.request, base58, base64
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
R = json.load(open("record_pda_results.json")); rows = [r for r in R["pages"] if r["derived_matches_served"] is False] + [r for r in R["pages"] if r["derived_matches_served"]][:2]
out = []
for r in rows:
    rec = r["record_served"]; ai = rpc("getAccountInfo", [rec, {"encoding": "base64"}])["result"]["value"]; data = base64.b64decode(ai["data"][0])
    ab = base58.b58decode(r["address"]); seq = int.from_bytes(data[33:41], "little")
    row = {"artifact": r["artifact"], "page": r["page"], "version": r["version"], "record": rec, "matched_first_pass": r["derived_matches_served"], "len": len(data), "b0": data[0], "seq_at_33": seq, "b41_73_b58": base58.b58encode(data[41:73]).decode(), "b73_79_hex": data[73:79].hex(), "upload_at_79_b58": base58.b58encode(data[79:111]).decode(), "upload_served": r["upload"], "upload_matches": base58.b58encode(data[79:111]).decode() == r["upload"], "b143_end_hex": data[143:].hex()[:120]}
    cands = {}
    for pre in ["record", "version", "import", "imported", "legacy", "page", "revision", "entry"]:
        for seeds, name in [([pre.encode(), ab, le64(seq)], f"{pre}|artifact|seq"), ([pre.encode(), ab, le64(r['page']), le64(seq)], f"{pre}|artifact|page|seq"), ([pre.encode(), ab, le64(r['page'])], f"{pre}|artifact|page"), ([pre.encode(), ab, data[41:73], le64(seq)], f"{pre}|artifact|b41|seq"), ([pre.encode(), data[41:73], le64(seq)], f"{pre}|b41|seq"), ([pre.encode(), ab, le64(r['version'])], f"{pre}|artifact|version")]:
            if pda(seeds, PROGRAM)[0] == rec: cands[name] = True
    row["seed_variants_matching"] = list(cands); out.append(row); print(json.dumps(row)); time.sleep(0.3)
json.dump(out, open("record_pda3_results.json", "w"), indent=1)
