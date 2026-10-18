"""For the four artifacts whose served page record does not derive: walk seq 1..history through the SDK's own rule (records(): recordAddress(artifact, seq) for seq in 1..history), read and decode every derived account (layout.mjs decodeRecord), check each self-hash, and compare the content fingerprints with the served pages."""
import json, hashlib, time, urllib.request, base58, base64, struct
from nacl.bindings import crypto_core_ed25519_is_valid_point as on_curve
PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"; RPC = "https://api.mainnet-beta.solana.com"
KINDS = ['genesis', 'content', 'membership', 'settings', 'kick', 'link', 'global', 'unlock', 'imported', 'revive', 'ban', 'trust', 'pause', 'claim']
def pda(seeds):
    pb = base58.b58decode(PROGRAM)
    for bump in range(255, -1, -1):
        h = hashlib.sha256(b"".join(seeds) + bytes([bump]) + pb + b"ProgramDerivedAddress").digest()
        if not on_curve(h): return base58.b58encode(h).decode()
def le64(n): return n.to_bytes(8, "little")
def rpc(m, p):
    req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r: return json.loads(r.read().decode())
def decode(data):
    o = 0
    def take(n):
        nonlocal o; v = data[o:o + n]; o += n; return v
    tag = take(1)[0]; art = base58.b58encode(take(32)).decode(); seq = int.from_bytes(take(8), "little"); kind = take(1)[0]; page = take(1)[0]; pv = int.from_bytes(take(4), "little")
    proposal = base58.b58encode(take(32)).decode(); subject = base58.b58encode(take(32)).decode(); content = take(32).hex(); dat = take(32).hex(); approve = int.from_bytes(take(2), "little"); reject = int.from_bytes(take(2), "little"); ballots = take(32).hex(); t = int.from_bytes(take(8), "little", signed=True); slot = int.from_bytes(take(8), "little"); ln = int.from_bytes(take(4), "little"); prev = take(32).hex()
    sl = int.from_bytes(take(4), "little"); title = take(sl).decode("utf-8", "replace"); end = o; h = take(32).hex()
    computed = hashlib.sha256(b"AC_RECORD_2" + data[:end]).hexdigest()
    return {"tag": tag, "artifact": art, "seq": seq, "kind": KINDS[kind] if kind < len(KINDS) else kind, "page": page, "pageVersion": pv, "proposal": proposal, "subject": subject, "content": content, "approve": approve, "reject": reject, "time": t, "slot": slot, "len": ln, "prev": prev, "title": title, "hash": h, "hash_ok": h == computed}
R = json.load(open("record_pda_results.json")); lst = json.load(open("dl/ac/artifacts.json")); lst = lst if isinstance(lst, list) else lst.get("artifacts")
hist = {a["address"]: a.get("history") for a in lst}
bad_arts = sorted({r["address"] for r in R["pages"] if r["derived_matches_served"] is False}); served = {(r["address"], r["page"]): r for r in R["pages"]}
out = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "artifacts": []}
for addr in bad_arts:
    ab = base58.b58decode(addr); rows = []
    for seq in range(1, (hist[addr] or 0) + 1):
        a = pda([b"record", ab, le64(seq)]); ai = rpc("getAccountInfo", [a, {"encoding": "base64"}])["result"]["value"]
        if ai is None: rows.append({"seq_derived": seq, "address": a, "exists": False}); continue
        d = decode(base64.b64decode(ai["data"][0])); d.update({"seq_derived": seq, "address": a, "exists": True, "seq_stored_equals_derived": d["seq"] == seq})
        sp = served.get((addr, d["page"])); d["is_served_record_for_its_page"] = (sp["record_served"] == a) if sp else None; d["content_equals_served_page_content"] = (sp["content"] == d["content"]) if sp else None
        rows.append(d); time.sleep(0.3)
    # the served, non-deriving record itself
    extra = []
    for r in R["pages"]:
        if r["address"] == addr and r["derived_matches_served"] is False:
            ai = rpc("getAccountInfo", [r["record_served"], {"encoding": "base64"}])["result"]["value"]; d = decode(base64.b64decode(ai["data"][0])); d.update({"address": r["record_served"], "served_for_page": r["page"]}); extra.append(d)
    out["artifacts"].append({"address": addr, "name": next(r["artifact"] for r in R["pages"] if r["address"] == addr), "history": hist[addr], "derived_chain": rows, "served_non_deriving_records": extra})
    print(f"\n#### {addr[:8]} history={hist[addr]}")
    for d in rows: print(json.dumps({k: d.get(k) for k in ("seq_derived", "exists", "seq", "kind", "page", "pageVersion", "hash_ok", "is_served_record_for_its_page", "content_equals_served_page_content", "slot")}), d.get("address", "")[:8] if d.get("exists") else "")
    for d in extra: print("SERVED non-deriving:", json.dumps({k: d.get(k) for k in ("served_for_page", "seq", "kind", "page", "pageVersion", "hash_ok", "slot", "prev")}), d["address"][:8])
json.dump(out, open("record_pda4_results.json", "w"), indent=1)
