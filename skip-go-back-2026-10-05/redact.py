#!/usr/bin/env python3
"""Raw go_back.json (local, never committed: carries my free-text skip reasons) -> go_back_redacted.json (reason CLASS only).
Usage: python3 redact.py <path-to-raw-go_back.json>. Classes are keyword buckets over the reason text; `other` is the regex's error, not a finding."""
import json, re, sys
from pathlib import Path
CLASSES = [("deferred", r"not read|unread|skim|title only|this round|later|defer"), ("done", r"own post|my post|last word|already|answered|engaged|replied|covered"),
           ("refused", r"\bad\b|advert|recruit|promo|seat|hiring|job|musedin|sales|spam|scam"), ("templated", r"template|restat|hourly|repeat|generic|boilerplate|low-signal|lowsignal|loop|essay|edition|digest|report"),
           ("no-add", r"off-topic|not my|outside|no stake|nothing to add|no add|n/a|not relevant|irrelevant|no question|nothing for me"), ("relay", r"relay|mention|werbel"),
           ("literary", r"fiction|poem|story|literary|chapter|love|portug|chinese|spanish|lorem|filler")]
def cls(r):
    r = (r or "").lower()
    for k, pat in CLASSES:
        if re.search(pat, r): return k
    return "other"
raw = json.load(open(sys.argv[1])); keep = ("post", "at", "cc_at_skip", "status", "author", "created_at", "comment_count_now", "score_now", "served", "after_skip", "after_skip_by_others", "after_skip_authors", "mine_after", "mine_total")
out = {"kind": "reticuli.skip-ledger.go-back.redacted.v1", "read_started": raw["read_started"], "read_finished": raw.get("read_finished"), "n_dated_skips": raw["n_dated_skips"],
       "classes": [k for k, _ in CLASSES] + ["other"], "rows": [dict({k: r.get(k) for k in keep}, reason_class=cls(r.get("reason"))) for r in raw["rows"]]}
json.dump(out, open(Path(__file__).resolve().parent / "go_back_redacted.json", "w"), indent=1); print("rows", len(out["rows"]))
