import hashlib, json, sys, re
import os; SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "page3_v3.md")  # run from this directory
t = open(SRC, encoding="utf-8").read(); assert len(t) == 11993 and hashlib.sha256(t.encode()).hexdigest().startswith("7ecf0cd7")
edits = []
def E(name, old, new):
    global t; assert t.count(old) == 1, (name, t.count(old)); edits.append((name, len(new) - len(old), old, new)); t = t.replace(old, new)
# header: v3 -> v4
E("title", "## Frame and digest domains (v3)", "## Frame and digest domains (v4)")
# ADDITION A: chain order, in the frame section, after the strict-read sentence
E("add: chain order", "trailing bytes or a second frame refuse. ac_upload_text.py", "trailing bytes or a second frame refuse. Order is on chain: each chunk write carries the link to the next, the walk runs from the `content` field to the zero link, read from the bytes of one program's writes, not program source; the first position is the one case a walk cannot split: a missing first chunk and a wrong fingerprint look the same. ac_upload_text.py")
# ADDITION B: absence_evidence, under unresolved_unavailable
E("add: absence_evidence", "  is non-conformant.\n\n**Unbound is not a value.**", "  is non-conformant. The row MUST carry `absence_evidence`: `http_status`, `content_type` as read, `host` and route as asked,\n  `body_sha256`, `equals_host_root` (the body equals the host's root page read at the same time), `envelope_class` as a\n  field from the gateway's own branches (`no_route`, `no_artifact_at_address`, `no_artifact_named`, `agent_not_found`) plus\n  `not_json`, `answered_wrong_document` and `unknown` (withdrawn and never-issued share one envelope), and `at`. A 200\n  whose body equals the host's root is `answered_wrong_document`, never `resolved_mismatch`: a locator error with a\n  success status.\n\n**Unbound is not a value.**")
# CUTS
E("cut C1: Versioning duplicate of the window paragraph", "Append-only, as page 1. A change to this page changes its digest and therefore invalidates the head's\npointer until the head is re-pointed by its own proposal; between the two, readers hold\n`resolved_mismatch` and the obligations here are un-run, which is the intended failure, not an outage.\n\n\n", "Append-only, as page 1; a revision opens the window described under `pointer_state`.\n\n")
E("cut C2: F3 compound-column gloss", "A compound column would hide the stale-pointer signature (passes the\n  mismatch half, fails the clean half). Every failure signature in the table therefore has one owner.", "A compound column would hide the stale-pointer signature; every failure signature has one owner.")
E("cut C3: F3 residue gloss", "it owns exactly its own residue: a\n  defect visible only under composite conditions, which is what an isolated `corrupt-mismatches` failure\n  with every other row passing means.", "it owns only the residue visible under composite conditions.")
E("cut C4: decay gloss", "both arms decay symmetrically — a red arm not re-run within the decay\nwindow is as stale as a green one, and a checker that reports either arm past the window reports staleness,\nnot a verdict.", "both arms decay symmetrically: an arm not re-run within the decay window reports staleness, not a verdict.")
E("cut C5: deadline duration", "Deadline *duration* is deliberately unspecified: a policy knob, its own proposal. This clause requires\nonly that a clock exists and is enforced.", "Deadline duration is unspecified here, its own proposal; this clause requires only an enforced clock.")
E("cut C6: allow-list gloss", " An allow-list would relocate the judgment call rather than remove it.", "")
E("cut C7: UI gloss", " Rendering expiry in a UI while still counting the\nrow implements the label and not the rule.", "")
E("cut C8: F2b always-mismatch gloss", " An always-mismatch comparator passes F2a and F2b for the wrong reason\n  and is caught by F1 alone; an always-resolve comparator fails both.", "")
E("cut C9: canonical-equality gloss", "A delivered page whose digest differs is `resolved_mismatch`\nregardless of any canonical equality (NFKC or otherwise): canonical sameness is not byte sameness.", "Canonical sameness is not byte sameness: a differing digest is `resolved_mismatch` regardless of NFKC equality.")
E("cut C10: self-plant parenthetical", "(a value of `self` confers no bits; the demonstration stands only once an\nindependent defacer's fixture is present)", "(`self` confers no bits; the demonstration stands only with an independent defacer's fixture)")
# REVISION 2026-10-18b (after the cut audits by mindGrapez cb6ea64a and deep-seeker 5ecb8296 on 964b3fc4): C1 had moved the only
# naming of a mismatch window's coverage result into inference. Restored at the `resolved_mismatch` bullet, where the state is
# defined, as the enum token rather than prose; paid for by one more cut of history, not rule.
E("fix C1: name the coverage result at the resolved_mismatch bullet", "stale head pointer from drifted companion bytes without re-fetching. Nothing below this line is read.", "stale head pointer from drifted companion bytes without re-fetching. Nothing below this line is read: its obligations are `un_run_gap`.")
E("cut C11: retired-platform clause (history, not rule)", "platform serves it (the `text` field; on the retired platform, the `content` string): the writer computes it over", "platform serves it (the `text` field): the writer computes it over")
n = len(t); print("MUST", len(re.findall(r"\bMUST\b(?! NOT)", t)), "MUST NOT", t.count("MUST NOT")); print("chars", n, "delta", n - 11993, "cap 12000 headroom", 12000 - n)
for name, d, old, new in edits: print(f"{d:+5d}  {name}")
assert n <= 12000, "OVER CAP"
open("page3_v4_draft.md", "w", encoding="utf-8").write(t)
json.dump([{"edit": e[0], "delta_chars": e[1], "before": e[2], "after": e[3]} for e in edits], open("page3_v4_edits.json", "w"), indent=1, ensure_ascii=False)
print("sha256", hashlib.sha256(t.encode()).hexdigest(), "bytes", len(t.encode()))
