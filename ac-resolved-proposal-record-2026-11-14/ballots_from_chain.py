"""Decode the saved transactions of a proposal account (walk_<label>/tx_*.json, written by walk_proposal.py) into ballots.
Read-only: it reads saved files; with RECORD=1 it also asks the public RPC for the accounts named in the resolve transaction and
decodes the one that is an outcome record. No key, nothing signed.

Layouts are the ones in the public relay package (sdk/layout.mjs at commit 2d0a35d2, digest equal to the package's manifest), read
as text, never run:
  instruction data = family byte 1, then the envelope: 8 bytes of magic, domain 32, program 32, agent 32, nonce u64, expiry i64,
  preferred 32, a u32-counted list of 32-byte accounts, the action (type byte; for a vote one more byte, approve), selfPaid byte.
  Ed25519 instruction = count, pad, one 14-byte offsets entry, then key 32 and signature 64.
  record = tag 7, artifact 32, seq u64, kind u8, page u8, pageVersion u32, proposal 32, subject 32, content 32, data 32, approve u16,
  reject u16, ballots 32, time i64, slot u64, len u32, prev 32, title (u32 length + bytes), then hash 32 = sha256('AC_RECORD_2' + all
  bytes before it).
Usage: python3 ballots_from_chain.py <label> [RECORD=1 in the environment]"""
import base64, glob, hashlib, json, os, struct, sys, time, urllib.request
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
LABEL = sys.argv[1]; OUT = f"walk_{LABEL}"
PROGRAM = "77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1"; ED = "Ed25519SigVerify111111111111111111111111111"
ACTIONS = ['register', 'setKey', 'begin', 'create', 'propose', 'vote', 'confirm', 'cancelUpload', 'apply', 'withdraw', 'contribute', 'second', 'revive', 'recover', 'decline', 'claim']
CRANK = ['resolve', 'expire', 'closeEpoch', 'claimWork', 'retire', 'applyGlobal', 'unwrap', 'expireUpload', 'expireApplication', 'pruneBanned']
RECORD_KINDS = ['genesis', 'content', 'membership', 'settings', 'kick', 'link', 'global', 'unlock', 'imported', 'revive', 'ban', 'trust', 'pause', 'claim']
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big"); pad = len(s) - len(s.lstrip("1")); return b"\x00" * pad + raw


def b58e(b):
    n = int.from_bytes(b, "big"); s = ""
    while n: n, r = divmod(n, 58); s = B58[r] + s
    return "1" * (len(b) - len(b.lstrip(b"\x00"))) + s


ts = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t else "?"
AG = json.load(open("inputs/agents.json")); AG = AG.get("agents") if isinstance(AG, dict) else AG
HANDLE = {a["id"]: a.get("handle") for a in AG}; SIGNER = {a["id"]: a.get("signer") for a in AG}   # the public copy of agents.json has no signer column: fetch /v2/agents yourself to fill it
sigs = json.load(open(f"{OUT}/sigs.json")); rows = []
for s in sorted(sigs, key=lambda s: (s["slot"], s["signature"])):
    tx = json.load(open(f"{OUT}/tx_{s['signature'][:10]}.json")); msg = tx["transaction"]["message"]; la = tx["meta"].get("loadedAddresses") or {}
    keys = list(msg["accountKeys"]) + list(la.get("writable") or []) + list(la.get("readonly") or [])
    ed = [b58d(ix["data"]) for ix in msg["instructions"] if keys[ix["programIdIndex"]] == ED]
    for ix in msg["instructions"]:
        if keys[ix["programIdIndex"]] != PROGRAM: continue
        d = b58d(ix["data"]); row = {"sig": s["signature"], "slot": s["slot"], "at": ts(tx.get("blockTime")), "blockTime": tx.get("blockTime"), "family": d[0], "accounts": [keys[a] for a in ix["accounts"]], "fee_payer": keys[0]}
        if d[0] == 1:                                                                        # a signed action
            assert len(ed) == 1 and ed[0][0] == 1, "one Ed25519 instruction with one signature expected"
            e = ed[0]; so, _, ko, _, mo, ml, mi = struct.unpack_from("<7H", e, 2); assert (ko, so, mo, mi) == (16, 48, 1, 1) and ml == len(d) - 1, (ko, so, mo, ml, mi, len(d))
            row["signing_key"] = b58e(e[16:48])
            o = 1; magic = d[o:o + 8]; o += 8; row["magic"] = magic.hex()
            domain = d[o:o + 32]; o += 32; program = b58e(d[o:o + 32]); o += 32; assert program == PROGRAM
            row["agent"] = b58e(d[o:o + 32]); o += 32; row["nonce"], row["expiry"] = struct.unpack_from("<Qq", d, o); o += 16; o += 32   # preferred
            n = struct.unpack_from("<I", d, o)[0]; o += 4; row["env_accounts"] = [b58e(d[o + 32 * i:o + 32 * i + 32]) for i in range(n)]; o += 32 * n
            row["action"] = ACTIONS[d[o]]; o += 1
            if row["action"] == "vote":
                assert d[o] in (0, 1); row["approve"] = bool(d[o]); o += 1
                assert d[o] in (0, 1) and o + 1 == len(d), ("trailing bytes", o, len(d)); row["selfPaid"] = bool(d[o])
            row["handle"] = HANDLE.get(row["agent"]); row["signing_key_is_listed_signer_today"] = SIGNER.get(row["agent"]) == row["signing_key"]
        elif d[0] == 2: row["crank"] = CRANK[d[1]] if len(d) > 1 and d[1] < len(CRANK) else d[1:2].hex()
        rows.append(row)
json.dump(rows, open(f"{OUT}/decoded.json", "w"), indent=1)
votes = [r for r in rows if r.get("action") == "vote"]
print(f"== {LABEL}: {len(rows)} program instructions | actions {[r.get('action') or ('crank:' + str(r.get('crank'))) for r in rows]}")
for r in rows:
    if r.get("action") == "vote": print(f"   vote  {r['at']} slot {r['slot']} | agent {r['agent'][:8]} ({r['handle']}) | approve {r['approve']} | nonce {r['nonce']} | selfPaid {r['selfPaid']} | key listed as signer today {r['signing_key_is_listed_signer_today']} | tx {r['sig'][:10]}")
    elif r.get("action"): print(f"   {r['action']:<5} {r['at']} slot {r['slot']} | agent {r['agent'][:8]} ({r['handle']}) | tx {r['sig'][:10]}")
    else: print(f"   crank {r.get('crank')} {r['at']} slot {r['slot']} | tx {r['sig'][:10]}")
assert len({r["agent"] for r in votes}) == len(votes), "an agent voted twice"
print("   ballots from the chain:", sum(r["approve"] for r in votes), "approve,", sum(not r["approve"] for r in votes), "reject, of", len(votes))

if os.environ.get("RECORD") == "1":
    def rpc(method, params):
        req = urllib.request.Request("https://api.mainnet-beta.solana.com", data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"Content-Type": "application/json", "User-Agent": "reader/1"})
        r = json.load(urllib.request.urlopen(req, timeout=60)); assert "error" not in r, r; return r["result"]
    res = [r for r in rows if r.get("crank") == "resolve"]; assert len(res) == 1, "one resolve expected"
    accs = list(dict.fromkeys(res[0]["accounts"])); got = rpc("getMultipleAccounts", [accs, {"encoding": "base64"}]); json.dump({"accounts": accs, "result": got}, open(f"{OUT}/resolve_accounts.json", "w"))
    recs = []
    for a, v in zip(accs, got["value"]):
        if v is None: print("   account", a[:8], "ABSENT"); continue
        b = base64.b64decode(v["data"][0]); print("   account", a[:8], "owner", v["owner"][:8], "bytes", len(b), "tag", b[0] if b else None)
        if v["owner"] == PROGRAM and b and b[0] == 7: recs.append((a, b))
    for a, b in recs:
        o = 1; rec = {"address": a}
        rec["artifact"] = b58e(b[o:o + 32]); o += 32; rec["seq"] = struct.unpack_from("<Q", b, o)[0]; o += 8; rec["kind"] = RECORD_KINDS[b[o]]; rec["page"] = b[o + 1]; o += 2
        rec["pageVersion"] = struct.unpack_from("<I", b, o)[0]; o += 4; rec["proposal"] = b58e(b[o:o + 32]); o += 32; rec["subject"] = b58e(b[o:o + 32]); o += 32
        rec["content"] = b[o:o + 32].hex(); o += 32; rec["data"] = b[o:o + 32].hex(); o += 32; rec["approve"], rec["reject"] = struct.unpack_from("<HH", b, o); o += 4
        rec["ballots"] = b[o:o + 32].hex(); o += 32; rec["time"], rec["slot"], rec["len"] = struct.unpack_from("<qQI", b, o); o += 20; rec["prev"] = b[o:o + 32].hex(); o += 32
        n = struct.unpack_from("<I", b, o)[0]; o += 4; rec["title"] = b[o:o + n].decode("utf-8"); o += n; rec["hash"] = b[o:o + 32].hex()
        rec["hash_recomputed"] = hashlib.sha256(b"AC_RECORD_2" + b[:o]).hexdigest(); rec["hash_ok"] = rec["hash"] == rec["hash_recomputed"]; rec["bytes"] = len(b); rec["bytes_read"] = o + 32; rec["time_at"] = ts(rec["time"])
        json.dump(rec, open(f"{OUT}/record.json", "w"), indent=1); print("   RECORD", json.dumps(rec, indent=1))
