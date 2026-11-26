"""build_v6_cuts.py: build the CUTS-ONLY draft of Receipt Schema page 3 version 6 from the text served as version 5
(page3_v5_draft.md here, 11,999 characters, sha256 6213a075...). Nothing is filed by this script and nothing is signed.
It joins the 34 line wraps (K5), applies four cuts (K1 to K4) and four points (L1, L2, L3, L8), each by an exact match that
must occur exactly once, and prints the accounting. It also prices the nine-point version (all of L1 to L9) that the page
cannot hold, and one candidate that writes L6 again as an addition. The frame fold is first calibrated on version 5 against the
`content` the gateway served for it. Usage: python3 build_v6_cuts.py <directory with page3_v5_draft.md and META.json> <out dir>"""
import hashlib, json, os, re, struct, sys
SRC_DIR, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); CAP = 12000
V5 = open(os.path.join(SRC_DIR, "page3_v5_draft.md"), encoding="utf-8").read()
assert hashlib.sha256(V5.encode()).hexdigest() == "6213a0751a86bb9e8f7b6f933002733bd1052afd81173cbac78c760f2e421d67" and len(V5) == 11999
RCP = json.load(open(os.path.join(SRC_DIR, "META.json"), encoding="utf-8"))["frame_recipe"]
assert RCP["header_bytes"] == 12 and RCP["link"] == "sha256(chunk + link)" and RCP["fold_direction"] == "last_to_first"


def root(text):
    b = text.encode("utf-8"); fr = bytes.fromhex(RCP["magic_descriptor_hex"]) + struct.pack("<I", len(b)) + struct.pack("<I", len(b) * 8 + 1)[:3] + b
    n = int(RCP["chunk_bytes"]); link = bytes.fromhex(RCP["link_seed_hex"])
    for c in reversed([fr[i:i + n] for i in range(0, len(fr), n)]): link = hashlib.sha256(c + link).digest()
    return link.hex(), len(fr)


CAL = root(V5); assert CAL[0].startswith("cd7d034c") and CAL[1] == 12050, CAL        # version 5 as the gateway serves it: content cd7d034c..., len 12,050
wraps = len(re.findall(r"\n  (?=\S)", V5)); J = re.sub(r"\n  (?=\S)", " ", V5); assert wraps == 34 and len(V5) - len(J) == 68 and J.split() == V5.split()

CUTS = [("K1", "## Frame and digest domains (v4)", "## Frame and digest domains"),
        ("K2", "not the decoded text. Spec: deep-seeker 2487948c on 564d319c.", "not the decoded text."),
        ("K3", "That is this axis working, not a defect: the window is expected,", "The window is expected,"),
        ("K4", "Deadline duration is its own proposal; this clause requires only an enforced clock.", "This clause requires only an enforced clock.")]
FREE = [("L1", "the named author states the claim differently", "the author of the cited comment states the claim differently"),
        ("L2", "ac_upload_text.py (157cebe)", "ac_upload_text.py (ColonistOne/ainglish-panel-artifacts, 157cebe)"),
        ("L3", "is `answered_wrong_document`, never `resolved_mismatch`.", "is `answered_wrong_document`, never `resolved_mismatch`: a locator error with a success status."),
        ("L8", "Each resolution writes one row with `read_at` and", "Each resolution writes one row with `read_at`, the head's own sha256 as `head_digest`, and")]
INPLACE = [("L4", "Two digests alone cannot say which side moved;", "Two digests alone cannot say which side moved, and `moved` alone cannot either: it is read with its `reference_digest` and never quoted without it;"),
           ("L5", "a `head` move leaves `coverage_state` unreadable until the head is re-read.", "a `head` reading leaves `coverage_state` unreadable until the pointer resolves."),
           ("L6", "the digest this reader voted on or last held", "the digest this reader voted on or last held as `resolved_ok`"),
           ("L7", "Nothing below this line is read: its obligations are `un_run_gap`.", "Nothing below this line is read: its obligations are `un_run_gap`. The definitions applied to a mismatch are those of the page the reader is pinned on, never those in the fetched bytes."),
           ("L9", "Error-class; the record carries the offending offset.", "Error-class; the record carries the offending offset, and its obligations are `un_run_gap`.")]
# L6 written again as an addition: a field on the mismatch record that says how the pin was held. A record without it is a prior record.
L6_ADD = ("L6 as a field", "(`reference_digest`: the digest this reader voted on or last held):", "(`reference_digest`: the digest this reader voted on or last held; `reference_kind`: `voted`, `held_ok` or `held_other`):")


def apply(text, edits):
    acct = []
    for name, a, b in edits:
        assert text.count(a) == 1, (name, text.count(a)); text = text.replace(a, b); acct.append((name, len(b) - len(a)))
    return text, acct


A, acct_k = apply(J, CUTS); A, acct_l = apply(A, FREE); assert len(A) <= CAP
N, acct_n = apply(A, INPLACE)                                                              # all nine points on top of every cut: what the page cannot hold
X, acct_x = apply(A, [L6_ADD])
os.makedirs(OUT, exist_ok=True); open(os.path.join(OUT, "page3_v6_cuts_draft.md"), "w", encoding="utf-8").write(A)
r = root(A)
build = {"source": {"version": 5, "chars": len(V5), "sha256": hashlib.sha256(V5.encode()).hexdigest(), "content_recomputed": CAL[0], "frame_len": CAL[1]},
         "k5": {"wraps_joined": wraps, "saves": len(V5) - len(J)}, "cuts": dict(acct_k), "points_carried": dict(acct_l),
         "cuts_only": {"chars": len(A), "utf8_bytes": len(A.encode()), "cap": CAP, "free": CAP - len(A), "sha256": hashlib.sha256(A.encode()).hexdigest(), "content_fold": r[0], "frame_len": r[1]},
         "left_out_as_written": dict(acct_n), "nine_points": {"chars": len(N), "over_cap": len(N) - CAP},
         "l6_as_field": {"cost": acct_x[0][1], "chars_with_it": len(X), "free_with_it": CAP - len(X)},
         "sections_of_cuts_only": [(m.group(0), m.start()) for m in re.finditer(r"^## .*$", A, re.M)], "pointer_state_values_unchanged": "{resolved_ok, resolved_mismatch, unresolved_unavailable, undecodable}" in A}
secs = build["sections_of_cuts_only"]; build["section_lengths"] = [(secs[i][0], (secs[i + 1][1] if i + 1 < len(secs) else len(A)) - secs[i][1]) for i in range(len(secs))]
json.dump(build, open(os.path.join(OUT, "page3_v6_cuts_build.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps(build, indent=1, ensure_ascii=False))
