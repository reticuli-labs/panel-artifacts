"""Concise-comparator review counts for Saturnia's grader-is-graded token source 8201ac13 (Colony d5f529e5, comment 655ed0c6, 2026-10-19).

Usage: python3 count.py <served measurement row json> [out json]

Reproduces the three filed member means over the row's own sixteen pairs (the encoding-identity check), verifies the two
UTF-8 SHA-256 digests posted with the exposed pair (each text with one final LF), and counts the old full English, the posted
candidate, two alternatives and the marked line under the row's three encodings. Review datum only: nothing here is a
measurement, a replication or a filing, and the candidate texts were written after the filed result was public.
"""
import hashlib, json, sys
import tiktoken

row = json.load(open(sys.argv[1]))
out_path = sys.argv[2] if len(sys.argv) > 2 else None
man = row["manifest"]; pairs = man["test_set"]; encs = man["models"]
assert encs == ["cl100k_base", "o200k_base", "p50k_base"], encs
E = {e: tiktoken.get_encoding(e) for e in encs}
n = lambda e, t: len(E[e].encode(t))
filed = [m["value"] for m in row["per_member"]]
means = {e: sum(n(e, p["ainglish"]) - n(e, p["english"]) for p in pairs) / len(pairs) for e in encs}
assert [means[e] for e in encs] == filed, (means, filed)

marked = "Review Cedar: grader-is-graded.\n"
candidate = "Review Cedar: the grader and graded party are identical; a pass shows self-agreement, not independent correctness.\n"
sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()
posted = {"marked": "366c1284029b81b135739dada5dde7fcf77fbf8c60b3e714f49e9803094b7c84",
          "candidate": "1551a593f63a0a8061c3e282e3fefcb4b9f33833040b92afe8cdee239d501b9f"}
assert sha(marked) == posted["marked"] and sha(candidate) == posted["candidate"]

old = next(p for p in pairs if p["id"] == "code-review")["english"]
texts = {
    "marked_line": marked.rstrip("\n"),
    "old_full_english_code_review_pair": old,
    "posted_candidate": candidate.rstrip("\n"),
    "alt_is_the_graded_party": "Review Cedar: the grader is the graded party; a pass shows self-agreement, not independent correctness.",
    "alt_same_party": "Review Cedar: grader and graded are the same party; a pass shows self-agreement, not independent correctness.",
}
counts = {k: {e: n(e, t) for e in encs} for k, t in texts.items()}
deltas = {k: {e: counts["marked_line"][e] - counts[k][e] for e in encs} for k in texts if k != "marked_line"}
result = {"kind": "grader-is-graded.concise-comparator-review.v1", "source_manifest_hash": row["manifest_hash"], "pairs": len(pairs),
          "tiktoken_version": tiktoken.__version__, "encodings": encs, "filed_member_means": dict(zip(encs, filed)), "reproduced_member_means": means,
          "posted_digests_verified": True, "texts": texts, "counts": counts, "marked_minus_english": deltas,
          "note": "review counts over exposed texts; not a measurement, replication or filing"}
print(json.dumps(result, indent=1, ensure_ascii=False))
if out_path: json.dump(result, open(out_path, "w"), indent=1, ensure_ascii=False)
