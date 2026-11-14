"""What is left of a proposal once it has resolved? Read-only, public Solana RPC only (no gateway, no key, nothing signed).
Usage: python3 walk_proposal.py <proposal account address> <label>
For the given proposal account: is the account still there (getAccountInfo), which transactions touched it
(getSignaturesForAddress), and for each transaction every top-level instruction: program, the first bytes of its data, its length,
its accounts, plus the log lines. Everything is saved under walk_<label>/; nothing is decoded here beyond that. The decoding of
ballots is done by ballots_from_chain.py from the saved files, so that a wrong guess about a layout costs no second fetch."""
import json, os, sys, time, urllib.request
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
ADDR, LABEL = sys.argv[1], sys.argv[2]; OUT = f"walk_{LABEL}"; os.makedirs(OUT, exist_ok=True)
RPC = "https://api.mainnet-beta.solana.com"
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
assert all(ch in B58 for ch in ADDR) and 32 <= len(ADDR) <= 44


def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big"); pad = len(s) - len(s.lstrip("1")); return b"\x00" * pad + raw


def rpc(method, params, tries=7):
    for i in range(tries):
        try:
            req = urllib.request.Request(RPC, data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(), headers={"Content-Type": "application/json", "User-Agent": "reader/1"})
            r = json.load(urllib.request.urlopen(req, timeout=60))
            if "error" in r: raise RuntimeError(r["error"])
            return r["result"]
        except Exception as e:
            if i == tries - 1: raise
            time.sleep(3 + 4 * i)


ts = lambda t: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(t)) if t else "?"
info = rpc("getAccountInfo", [ADDR, {"encoding": "base64"}]); json.dump(info, open(f"{OUT}/account_info.json", "w"), indent=1)
v = info.get("value")
print("account", ADDR[:8], "| read at", ts(time.time()), "| slot", info["context"]["slot"], "|", "ABSENT (null)" if v is None else "PRESENT owner %s lamports %s data bytes %s" % (v["owner"][:8], v["lamports"], len(__import__("base64").b64decode(v["data"][0]))))
sigs = []; before = None
while True:
    page = rpc("getSignaturesForAddress", [ADDR, {"limit": 1000, **({"before": before} if before else {})}])
    sigs += page
    if len(page) < 1000: break
    before = page[-1]["signature"]
json.dump(sigs, open(f"{OUT}/sigs.json", "w"), indent=1)
print("signatures", len(sigs), "| with an error", sum(1 for s in sigs if s.get("err")))
for s in sorted(sigs, key=lambda s: (s["slot"], s["signature"])):
    f = f"{OUT}/tx_{s['signature'][:10]}.json"
    if os.path.exists(f): tx = json.load(open(f))
    else:
        tx = rpc("getTransaction", [s["signature"], {"encoding": "json", "maxSupportedTransactionVersion": 1}]); json.dump(tx, open(f, "w")); time.sleep(1.3)
    msg = tx["transaction"]["message"]; la = tx["meta"].get("loadedAddresses") or {}
    keys = list(msg["accountKeys"]) + list(la.get("writable") or []) + list(la.get("readonly") or [])
    print(f"\n-- {s['signature'][:10]} slot {s['slot']} {ts(tx.get('blockTime'))} err {s.get('err')} fee payer {keys[0][:6]} signers {msg['header']['numRequiredSignatures']}")
    for ix in msg["instructions"]:
        d = b58d(ix["data"]) if ix["data"] else b""
        print("   ix", keys[ix["programIdIndex"]][:12], "| data", len(d), "B head", d[:12].hex(), "| accounts", [keys[a][:6] for a in ix["accounts"]])
    for l in (tx["meta"].get("logMessages") or []):
        if "Program log" in l or "Program data" in l: print("     ", l[:220])
