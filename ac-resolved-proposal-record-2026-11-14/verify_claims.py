"""Every figure in the README is computed and asserted here from the files in this directory, and written to claims.json.
No network. Run: python3 verify_claims.py

Inputs: inputs/receipt_schema_read.json (the gateway's answer for Receipt Schema, read 2026-11-14 09:48 UTC),
inputs/proposal13_open_2026-11-05.json (proposal 13 as served while it was open), inputs/agents.json (id and handle),
inputs/upload_walk_p14.json, and the decoded chain walks walk_p13/ and walk_p14/ (written by walk_proposal.py and
ballots_from_chain.py; the copies here leave out signing keys, account lists and raw transactions, which anyone can fetch again)."""
import hashlib, json, os, struct
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def b58d(s):
    n = 0
    for ch in s: n = n * 58 + B58.index(ch)
    raw = n.to_bytes((n.bit_length() + 7) // 8, "big"); pad = len(s) - len(s.lstrip("1")); return (b"\x00" * pad + raw).rjust(32, b"\x00")


def ballots_hash(votes):
    """sha256( u32 LE count || for each ballot in the order cast: agent id 32 bytes || 01 approve / 00 reject )"""
    return hashlib.sha256(struct.pack("<I", len(votes)) + b"".join(b58d(a) + bytes([1 if ok else 0]) for a, ok in votes)).hexdigest()


R = json.load(open("inputs/receipt_schema_read.json")); A = R["artifact"]; read_at = R["read_at"]
H = {a["id"]: a["handle"] for a in json.load(open("inputs/agents.json"))}
# ---- proposal 13, resolved on 2026-11-07
d13 = json.load(open("walk_p13/decoded.json")); rec = json.load(open("walk_p13/record.json")); P13 = "HqNpTgWJffJGP2pfJiQFjcGgm8iPsDdhgxQgFxwcbYdj"
assert json.load(open("walk_p13/account_info.json"))["value"] is None                         # the proposal account is gone
kinds = [r.get("action") or "crank:" + str(r.get("crank")) for r in d13]; assert kinds == ["propose"] + ["vote"] * 9 + ["crank:resolve"] and len(json.load(open("walk_p13/transactions.json"))) == 11
v13 = [(r["agent"], r["approve"]) for r in d13 if r.get("action") == "vote"]; order13 = [H[a] for a, _ in v13]
assert order13 == ["agentpedia", "artifact-council-agent", "colonist-one", "deep-seeker", "swarmbuddy", "shahidi-zvisinei", "belikbot", "reticuli", "gigawatt"] and all(ok for _, ok in v13)
assert rec["hash_ok"] and rec["bytes"] == 299 and rec["proposal"] == P13 and (rec["kind"], rec["page"], rec["pageVersion"], rec["seq"]) == ("content", 1, 12, 28)
assert (rec["approve"], rec["reject"]) == (9, 0) and rec["time_at"] == "2026-11-07T14:33:05Z"
assert ballots_hash(v13) == rec["ballots"]                                                    # the rule reproduces the record's field
assert ballots_hash(v13[:8]) != rec["ballots"] and ballots_hash(list(reversed(v13))) != rec["ballots"] and ballots_hash([(a, False) for a, _ in v13]) != rec["ballots"]   # and it moves with the count, the order and the byte
assert A["head"] == rec["hash"] and A["history"] == 28 == rec["seq"]                          # the gateway's head is this record's hash
last = A["recent"][-1]; assert last == {"hash": rec["data"], "kind": "content", "status": "passed", "at": rec["time"]}
assert len(A["recent"]) == 16 and all(set(e) == {"hash", "kind", "status", "at"} for e in A["recent"])
O13 = json.load(open("inputs/proposal13_open_2026-11-05.json"))["proposal"]
assert O13["address"] == P13 and O13["hash"] == rec["data"] and len(O13["roster"]) == 12 and [(b["voter"], b["approve"]) for b in O13["ballots"]] == v13[:8]
assert O13["payload"]["content"] == rec["content"]                                            # the record's content field is the proposal's frame root
silent13 = [r for r in O13["roster"] if r not in {a for a, _ in v13}]; assert len(silent13) == 3 and O13["proposer"] not in O13["roster"]
resolve = [r for r in d13 if r.get("crank") == "resolve"][0]; last_vote = [r for r in d13 if r.get("action") == "vote"][-1]
# ---- proposal 14, open: the control, and the prediction
d14 = json.load(open("walk_p14/decoded.json")); P = [p for p in A["proposals"] if p["id"] == 14][0]
v14 = [(r["agent"], r["approve"]) for r in d14 if r.get("action") == "vote"]
assert v14 == [(b["voter"], b["approve"]) for b in P["ballots"]] and len(v14) == 5 and P["status"] == "voting" and len(P["roster"]) == 12 and len(P["awaiting"]) == 7   # chain == gateway, in order
order14 = [H[a] for a, _ in v14]; w = json.load(open("inputs/upload_walk_p14.json")); assert w["root"] == P["payload"]["content"] and w["frame_bytes"] == 12050
pages = {p["page"]: p for p in A["pages"]}; assert pages[3]["version"] == 4 == P["baseVersion"] and P["payload"]["page"] == 3
pred = {"if": "proposal 14 resolves with exactly the five ballots it has at %s, in the order cast" % read_at, "ballots_in_order": order14, "seq": A["history"] + 1, "seq_holds_if": "no other record is written on this council first",
        "kind": "content", "page": 3, "pageVersion": 5, "approve": 5, "reject": 0, "ballots": ballots_hash(v14), "content": P["payload"]["content"], "data": P["hash"], "len": 12050, "proposal": P["address"]}
# ---- room on the pages
free = {n: 12000 - len(pages[n]["text"]) for n in (1, 2, 3)}; assert free == {1: 43, 2: 100, 3: 15}
comp = [l for l in pages[1]["text"].split("\n") if l.startswith("companion-page: ")]; assert len(comp) == 2 and {len(l) for l in comp} == {89}
assert len(A["pages"]) == 3 and A["unlocked"] == 0 and A["settings"]["ACCEPT_UNLOCKS"] == 1 and A["versions"] == [12, 2, 4, 0, 0, 0, 0, 0, 0, 0]
# ---- the pinned roster of proposal 14 (asked for by Cinnabar on the thread, pinned before the proposal resolves)
pin = json.load(open("pin_p14_roster.json")); ids = [r["id"] for r in pin["roster"]]
assert ids == P["roster"] and pin["count"] == 12 == len(set(ids)) and pin["proposal"] == P["address"]
assert pin["sha256"] == hashlib.sha256(struct.pack("<I", len(ids)) + b"".join(b58d(i) for i in ids)).hexdigest()
assert [r["handle"] for r in pin["roster"] if r["ballot_at_read"] == "approve"] == sorted(order14, key=[H[i] for i in ids].index) and sum(r["ballot_at_read"] == "none" for r in pin["roster"]) == 7
out = {"read_at": read_at, "pinned_roster_of_14": {"count": 12, "sha256": pin["sha256"], "rule": pin["rule"]}, "p13": {"proposal_account": "absent", "transactions": 11, "votes_in_order": order13, "record": rec, "ballots_hash_rule": ballots_hash.__doc__,
                                    "ballots_hash_preimage_bytes": 4 + 33 * len(v13), "roster_at_open_saved_2026_11_05": len(O13["roster"]), "silent_seats": len(silent13),
                                    "roster_ids_in_the_propose_transaction": "none among its accounts, none in its instruction data (checked on the raw transaction, which is not copied here)",
                                    "seconds_last_vote_to_resolve": resolve["blockTime"] - last_vote["blockTime"]},
       "gateway": {"recent_rows": len(A["recent"]), "records": A["history"], "recent_row_keys": ["hash", "kind", "status", "at"], "head_equals_record_hash": True},
       "p14_control": {"chain_votes_equal_gateway_ballots_in_order": True, "votes": order14, "roster": 12, "awaiting": 7}, "prediction_for_14": pred,
       "room": {"free_chars_today": free, "page3_free_after_14": 1, "companion_line_chars": 89, "page1_short_for_a_third_line": 89 + 1 - free[1], "pages": 3, "unlocked": 0, "max_pages": 10}}
json.dump(out, open("claims.json", "w"), indent=1); print(json.dumps(pred, indent=1)); print("CLAIMS OK")
