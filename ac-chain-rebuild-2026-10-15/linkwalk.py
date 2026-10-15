"""Verify the hypothesis from rebuild.py: each chunk-write instruction's 32 trailing bytes are the hash-chain link to the NEXT chunk (the last chunk carries 32 zero bytes), i.e. link_i = sha256(chunk_{i+1} + link_{i+1}) and content = sha256(chunk_1 + link_1). Walks from `content` without any order assumption. Re-splits the saved frames by the recorded chunk lengths (landed order matched, so the split is exact)."""
import json, hashlib
R = json.load(open("rebuild_results.json")); out = {}
for label, r in R.items():
    frame = open(f"frame_{label}.zst", "rb").read(); chunks = []; pos = 0
    for c in r["chunks"]:
        chunks.append({"bytes": frame[pos:pos + c["got_len"]], "trailing": bytes.fromhex(c["trailing"]), "slot": c["slot"]}); pos += c["got_len"]
    assert pos == len(frame)
    # link walk from content: at each step find the unique chunk with sha256(chunk + trailing) == link
    link = bytes.fromhex(r["content"]); order = []; pool = list(range(len(chunks))); ok = True
    while True:
        hits = [i for i in pool if hashlib.sha256(chunks[i]["bytes"] + chunks[i]["trailing"]).digest() == link]
        if len(hits) != 1: ok = (link == bytes(32) and not pool); break
        i = hits[0]; order.append(i); pool.remove(i); link = chunks[i]["trailing"]
    walk_pairs = all(hashlib.sha256(chunks[order[k+1]]["bytes"] + chunks[order[k+1]]["trailing"]).digest() == chunks[order[k]]["trailing"] for k in range(len(order) - 1))
    out[label] = {"n": len(chunks), "walk_complete": ok, "order_from_links": order, "order_equals_landed": order == list(range(len(chunks))), "every_trailing_is_next_link": walk_pairs, "last_trailing_zero": chunks[order[-1]]["trailing"] == bytes(32) if order else None, "byte1_values": sorted({c["byte1"] for c in r["chunks"]})}
    print(label, json.dumps(out[label]))
json.dump(out, open("linkwalk_results.json", "w"), indent=1)
