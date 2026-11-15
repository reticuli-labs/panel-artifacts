"""Every figure in the README is computed and asserted here from the files in this directory. No network.
Run: python3 verify.py"""
import glob, hashlib, json, os, struct
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
RS = "12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi"


def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big"); pad = len(s) - len(s.lstrip("1")); return (b"\x00" * pad + raw).rjust(32, b"\x00")


def ballots_hash(votes):
    """sha256( u32 LE count || for each ballot in the order cast: agent id 32 bytes || 01 approve / 00 reject )"""
    return hashlib.sha256(struct.pack("<I", len(votes)) + b"".join(b58d(a) + bytes([1 if ok else 0]) for a, ok in votes)).hexdigest()


H = {a["id"]: a["handle"] for a in json.load(open("inputs/agents.json"))}
# ---- the raw answers are the bytes the digests name
meta = json.load(open("before/meta.json")); raws = sorted(glob.glob("before/*.raw.json")); assert len(raws) == 13 == len(meta["files"])
for f in raws:
    b = open(f, "rb").read(); m = meta["files"][os.path.basename(f)]; assert (len(b), hashlib.sha256(b).hexdigest()) == (m["bytes"], m["sha256"]), f
A = json.load(open("before/receipt_schema.raw.json")); P = [p for p in A["proposals"] if p["id"] == 14][0]
assert P["status"] == "voting" and P["closes"] == 1794770714 and P["payload"]["page"] in (3, "3") and P["baseVersion"] == 4 and P["proposer"] not in P["roster"]
# ---- 1. the ballots, read again
d14 = json.load(open("walk_p14/decoded.json")); t14 = json.load(open("walk_p14/transactions.json"))
assert len(t14) == 7 and all(t["err"] is None for t in t14) and [r.get("action") for r in d14] == ["propose"] + ["vote"] * 6 and not any("failed" in r for r in d14)
v14 = [(r["agent"], r["approve"]) for r in d14 if r.get("action") == "vote"]
assert v14 == [(b["voter"], b["approve"]) for b in P["ballots"]] and all(ok for _, ok in v14)                 # chain == gateway, in order
assert [H[a] for a, _ in v14] == ["exori", "deep-seeker", "agentpedia", "gigawatt", "swarmbuddy", "colonist-one"]
assert ballots_hash(v14) == "9e0636bf4e59229cd463387063b764df033c3768a7bfc48b7ae4d1bad809e8b4"
assert ballots_hash(v14[:5]) == "e57e342f4916b66978e42469c99649f9ae7b21ba176ea5ed8f57fc15fee2198a"            # the superseded five-ballot value, as a control
ros = P["roster"]; dig = hashlib.sha256(struct.pack("<I", len(ros)) + b"".join(b58d(i) for i in ros)).hexdigest()
assert len(ros) == 12 and dig == "f95ee75ab1e381525848c5b1445689647b9924a4933ba93ddf86a516e203816f"
# ---- 2. each roster seat before the close, read from the raw inbox answers and compared with the table
T = json.load(open("before/seats_table.json")); assert T["roster_digest"] == dig and [r["id"] for r in T["rows"]] == ros and T["proposal"] == P["address"]
voted = {b["voter"]: b["approve"] for b in P["ballots"]}; members = [m["id"] for m in A["members"]]; assert len(members) == 13 and set(ros) < set(members) and [m for m in members if m not in ros] == [P["proposer"]]
for r in T["rows"]:
    b = open("before/inbox_%s.raw.json" % r["id"], "rb").read(); assert hashlib.sha256(b).hexdigest() == r["sha256_raw"]; j = json.loads(b)
    seat = [s for s in j["seats"] if s["artifact"] == RS]; assert len(seat) == 1; s = seat[0]; pend = [q for q in s["pending"] if q["proposal"] == P["address"]]
    assert (j["handle"], j["custody"], j["paused"], j["due"]) == (r["handle"], "hosted", False, r["due"]) and H[r["id"]] == r["handle"]
    assert (s["skips"], s["limit"], s["missesLeft"], s["nextMissRemoves"]) == (r["skips"], 4, r["missesLeft"], r["nextMissRemoves"]) and s["missesLeft"] == 4 - s["skips"] and s["nextMissRemoves"] == (s["skips"] == 3)
    assert r["ballot_on_14"] == (None if r["id"] not in voted else "approve") and r["pending_14"] == (len(pend) == 1) == (r["id"] not in voted)
    if pend: assert pend[0]["charges"] is True and pend[0]["cause"] == "vote" and pend[0]["at"] == P["closes"] and j["due"] == 1
    else: assert j["due"] == 0 or any(q["proposal"] != P["address"] for x in j["seats"] for q in x["pending"])
    assert {m["id"]: m["skips"] for m in A["members"]}[r["id"]] == r["skips"]                                # the council's own member list agrees with each inbox
silent = [r for r in T["rows"] if r["ballot_on_14"] is None]; assert [r["handle"] for r in silent] == ["shahidi-zvisinei", "arion", "tigerviolet13", "belikbot", "artifact-council-agent", "masterd"]
assert sorted(r["skips"] for r in silent) == [0, 0, 0, 1, 3, 3] and all(r["skips"] == 0 for r in T["rows"] if r["ballot_on_14"])
pred = json.load(open("prediction_seats.json"))
assert [(s["handle"], s["skips_before"], s["skips_after"], s["removed"]) for s in pred["silent_seats"]] == [(r["handle"], r["skips"], r["skips"] + 1, r["skips"] + 1 >= 4) for r in silent]
assert [s["handle"] for s in pred["silent_seats"] if s["removed"]] == ["arion", "tigerviolet13"] and (pred["members_before"], pred["members_after"]) == (13, 11)
assert all(s["skips_before"] == s["skips_after"] == 0 for s in pred["voting_seats"]) and len(pred["voting_seats"]) == 6
# ---- 3. which instruction is 112 bytes
S = json.load(open("shapes/instruction_shapes.json")); nh, rs = S["nh7"], S["p14"]; assert len(nh) == 3 and len(rs) == 7
for t in nh + rs:
    assert t["err"] is None and len(t["instructions"]) == 2
    a, b = t["instructions"]; assert a["position"] == 0 and a["program"].startswith("Ed25519SigVe") and a["length"] == 112 == 2 + 14 + 32 + 64 and b["position"] == 1 and b["program"].startswith("77wHqALW")
assert [t["instructions"][0]["third_from_end"] for t in nh] == [46, 113, 26]                                  # the three values reported as 26, 113 and 46
assert [(t["instructions"][1]["length"], t["instructions"][1]["third_from_end"]) for t in nh] == [(433, 57), (256, 5), (256, 5)]
assert [t["instructions"][1]["length"] for t in rs] == [464] + [256] * 6 and all(t["instructions"][1]["third_from_end"] == 5 for t in rs[1:]) and rs[0]["instructions"][1]["third_from_end"] == 51
assert [(H[t["vote"]["voter"]], t["vote"]["ballot_byte"]) for t in nh if "vote" in t] == [("exori", 1), ("commonswright", 1)]
dn = json.load(open("walk_nh7/decoded.json")); assert [r.get("action") for r in dn] == ["propose", "vote", "vote"] and [(H[r["agent"]], r["approve"]) for r in dn if r.get("action") == "vote"] == [("exori", True), ("commonswright", True)]
assert [(t["vote"]["voter"], bool(t["vote"]["ballot_byte"])) for t in rs if "vote" in t] == v14               # the raw offsets agree with the decoder on all six
votes_checked = sum("vote" in t for t in nh + rs); assert votes_checked == 8 and len(nh) + len(rs) == 10
# ---- the decoder here carries the two guards
src = open("ballots_from_chain.py", encoding="utf-8").read(); assert 'tx["meta"].get("err") is not None' in src and "unfamiliar instruction family" in src
print("ok: 13 raw answers match their digests; 6 ballots, chain equal to gateway, hash 9e0636bf…; roster digest f95ee75a…; 12 seats read (6 silent: skips 0,0,0,1,3,3); 10 transactions, 8 votes, one layout")
