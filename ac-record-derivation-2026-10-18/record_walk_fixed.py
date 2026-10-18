"""Corrected chain walk: pda_check.pda (Solana-exact on-curve test). For every artifact, seq 1..history: derived account exists, tag 7, names the artifact, stores seq, self-hash ok; prev links to the previous derived record; the last record's hash equals the served artifact head; every served page's record is the derived record of its highest version."""
import json, time, urllib.request, base64, base58, hashlib, sys
sys.path.insert(0, "."); from pda_check import pda, le64
KINDS = ['genesis', 'content', 'membership', 'settings', 'kick', 'link', 'global', 'unlock', 'imported', 'revive', 'ban', 'trust', 'pause', 'claim']
def decode(data):
    o = 0
    def take(n):
        nonlocal o; v = data[o:o + n]; o += n; return v
    tag = take(1)[0]; art = base58.b58encode(take(32)).decode(); seq = int.from_bytes(take(8), "little"); kind = take(1)[0]; page = take(1)[0]; pv = int.from_bytes(take(4), "little")
    proposal = base58.b58encode(take(32)).decode(); subject = base58.b58encode(take(32)).decode(); content = take(32).hex(); dat = take(32).hex(); approve = int.from_bytes(take(2), "little"); reject = int.from_bytes(take(2), "little"); ballots = take(32).hex(); t = int.from_bytes(take(8), "little", signed=True); slot = int.from_bytes(take(8), "little"); ln = int.from_bytes(take(4), "little"); prev = take(32).hex()
    sl = int.from_bytes(take(4), "little"); title = take(sl).decode("utf-8", "replace"); end = o; h = take(32).hex()
    computed = hashlib.sha256(b"AC_RECORD_2" + data[:end]).hexdigest()
    return {"tag": tag, "artifact": art, "seq": seq, "kind": KINDS[kind] if kind < len(KINDS) else kind, "page": page, "pageVersion": pv, "proposal": proposal, "subject": subject, "content": content, "approve": approve, "reject": reject, "time": t, "slot": slot, "len": ln, "prev": prev, "title": title, "hash": h, "hash_ok": h == computed}

PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"; RPC = "https://api.mainnet-beta.solana.com"
def rpc(m, p, tries=5):
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode(), headers={"content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as r: d = json.loads(r.read().decode())
            if "result" in d: return d["result"]
        except Exception as e: pass
        time.sleep(2 * (i + 1))
    raise SystemExit(f"rpc failed {m}")
lst = json.load(open("dl/ac/artifacts.json")); lst = lst if isinstance(lst, list) else lst.get("artifacts")
R = json.load(open("record_pda_results.json")); served = {(p["address"], p["page"]): p for p in R["pages"]}
out = {"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "program": PROGRAM, "artifacts": []}
tot = ok = 0
for a0 in lst:
    addr = a0["address"]; art = json.load(open(f"dl/ac/artifact_{addr[:8]}.json")) if __import__("os").path.exists(f"dl/ac/artifact_{addr[:8]}.json") else None
    if art is None:
        with urllib.request.urlopen(urllib.request.Request(f"https://gateway.artifactcouncil.com/v2/artifacts/{addr}", headers={"Accept": "application/json", "User-Agent": "reticuli/1"}), timeout=60) as r: art = json.loads(r.read().decode()); json.dump(art, open(f"dl/ac/artifact_{addr[:8]}.json", "w"))
    hist = art["history"]; head = art["head"]; ab = base58.b58decode(addr); rows = []; prev = "00" * 32; chain_ok = True
    for seq in range(1, hist + 1):
        a, bump = pda([b"record", ab, le64(seq)], PROGRAM); ai = rpc("getAccountInfo", [a, {"encoding": "base64"}])["value"]; tot += 1
        if ai is None: rows.append({"seq": seq, "address": a, "exists": False}); chain_ok = False; continue
        d = decode(base64.b64decode(ai["data"][0])); row = {"seq": seq, "address": a, "bump": bump, "exists": True, "owner_is_program": ai["owner"] == PROGRAM, "tag7": d["tag"] == 7, "artifact_ok": d["artifact"] == addr, "seq_ok": d["seq"] == seq, "hash_ok": d["hash_ok"], "prev_links": d["prev"] == prev, "kind": d["kind"], "page": d["page"], "pageVersion": d["pageVersion"], "hash": d["hash"]}
        prev = d["hash"]; chain_ok = chain_ok and all(row[k] for k in ("owner_is_program", "tag7", "artifact_ok", "seq_ok", "hash_ok", "prev_links")); rows.append(row); ok += 1; time.sleep(0.25)
    head_ok = (rows[-1].get("hash") == head) if rows and rows[-1].get("exists") else False
    # served pages: highest-version content record per page among derived == served record
    pages_ok = []
    for (ad, pg), sp in served.items():
        if ad != addr: continue
        cands = [r for r in rows if r.get("exists") and r["page"] == pg and r["kind"] in ("content", "imported")]
        top = max(cands, key=lambda r: r["pageVersion"]) if cands else None
        pages_ok.append({"page": pg, "served_record": sp["record_served"], "derived_top_record": top["address"] if top else None, "match": bool(top and top["address"] == sp["record_served"]), "version_match": bool(top and top["pageVersion"] == sp["version"])})
    out["artifacts"].append({"name": a0["name"], "address": addr, "history": hist, "records_found": sum(1 for r in rows if r.get("exists")), "chain_ok": chain_ok, "head_ok": head_ok, "pages": pages_ok, "rows": rows})
    print(f"{a0['name'][:28]:28} history={hist} found={sum(1 for r in rows if r.get('exists'))} chain_ok={chain_ok} head_ok={head_ok} pages={[ (p['page'], p['match'], p['version_match']) for p in pages_ok]}")
out["summary"] = {"records_expected": tot, "records_found": ok, "artifacts_chain_ok": sum(1 for a in out["artifacts"] if a["chain_ok"]), "artifacts_head_ok": sum(1 for a in out["artifacts"] if a["head_ok"]), "pages_match": sum(1 for a in out["artifacts"] for p in a["pages"] if p["match"]), "pages_total": sum(len(a["pages"]) for a in out["artifacts"])}
json.dump(out, open("record_walk_fixed.json", "w"), indent=1); print("SUMMARY", out["summary"])
