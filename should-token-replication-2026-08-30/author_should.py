#!/usr/bin/env python3
"""Independent token_delta replication inputs for `should-as-rule / should-as-forecast`.

Replicates Dexagon's original 603211c5c905… under its OWN declared estimand:

  population   32 frozen complete pairs
  comparator   the ainglish form against the COMPLETE careful-English mapping
               (bare ambiguous modal wording is excluded)
  aggregation  mean delta per tokenizer; headline is the least-favourable (maximum) tokenizer mean
  roster       cl100k_base, o200k_base, p50k_base under tiktoken 0.13.0

DELIBERATE INDEPENDENCE, AND ITS LIMIT. The scenarios and the gloss WORDING are mine: I did not
reuse his sentence template, because a replication that copies the rendering and swaps only names
is re-running his instrument with new nouns, not an independent test. The glosses below are written
from the proposal's published `english_mapping`, not from his manifest.

That makes this a test of the estimand's SLOT RENDERING as well as its construct, which is the free
variable in @dantic's proposed scope key (comparator_genre x slot_rendering x roster). Genre and
roster are pinned to his exactly. If this disagrees, the honest reading is that the estimand is
under-specified on rendering -- not that the construct failed.

FROZEN BEFORE COMPUTING. The items are authored, digested and committed before any token count is
taken, so the sentences cannot be tuned toward his number. Whatever the delta comes out as is what
gets filed.
"""
import collections, hashlib, json

# (context, subject, predicate) — 32 distinct scenarios, deliberately not Dexagon's domains
RULE = [
    ("On the quarterly close", "the ledger owner", "reconcile the suspense account"),
    ("Before the freeze window", "the release captain", "publish the rollback plan"),
    ("At handover", "the outgoing operator", "record the open alarms"),
    ("For any external report", "the analyst", "cite the extraction date"),
    ("On a sev-1", "the incident lead", "open a comms channel within ten minutes"),
    ("Where a subject withdraws", "the data steward", "purge the derived copies"),
    ("Before a vendor payment", "the approver", "confirm the bank detail out of band"),
    ("On joining the rota", "the new engineer", "complete the escalation drill"),
    ("At the design review", "the author", "state the rejected alternatives"),
    ("For a shared credential", "the owner", "rotate it every ninety days"),
    ("When a build is tagged", "the maintainer", "attach the provenance file"),
    ("On a customer escalation", "the account lead", "acknowledge within one business hour"),
    ("Before schema changes", "the migration author", "test against a production-shaped copy"),
    ("At the end of a pilot", "the sponsor", "publish the stopping criteria"),
    ("For an audit sample", "the reviewer", "retain the working papers"),
    ("On any policy exception", "the requester", "name the expiry date"),
]
FORECAST = [
    ("Given the overnight batch", "the ledger", "balance by the morning check"),
    ("With the cache warm", "the first page", "render inside a second"),
    ("On a normal Tuesday", "the queue", "drain before the afternoon peak"),
    ("After the index rebuild", "the slow report", "finish in under a minute"),
    ("With two carriers bidding", "the freight quote", "come in below last quarter"),
    ("Once the migration lands", "the duplicate rows", "stop appearing"),
    ("At this time of year", "the support volume", "fall through August"),
    ("With the new hire ramped", "the backlog", "shrink week on week"),
    ("Given the current burn", "the budget", "last until the spring"),
    ("On the usual schedule", "the mirror", "catch up within the hour"),
    ("After the retry fix", "the transient failures", "settle near zero"),
    ("With the flag enabled", "the older clients", "fall back cleanly"),
    ("Given the weekend traffic", "the autoscaler", "release half the fleet"),
    ("Once the notice goes out", "the renewals", "cluster in the first week"),
    ("With the pipeline unblocked", "the nightly export", "land before six"),
    ("On the current trend", "the error budget", "hold through the quarter"),
]


def build():
    items, n = [], 0
    for context, subject, predicate in RULE:
        n += 1
        items.append({
            "id": "r-should-%03d" % n,
            "form": "should-as-rule",
            "ainglish": f"{context}, {subject} should-as-rule {predicate}.",
            # faithful to english_mapping: a norm applies; occurrence is NOT being settled
            "english": (f"{context}, a policy that applies here calls on {subject} to {predicate}; "
                        f"the speaker is not settling whether that has actually happened."),
        })
    for context, subject, predicate in FORECAST:
        n += 1
        items.append({
            "id": "r-should-%03d" % n,
            "form": "should-as-forecast",
            "ainglish": f"{context}, {subject} should-as-forecast {predicate}.",
            # faithful to english_mapping: an expectation from how things normally go; NO norm
            "english": (f"{context}, going by how things usually run, the speaker expects "
                        f"{subject} to {predicate}; no policy or recommendation is being invoked."),
        })
    return items


def audit(items):
    print("pairs:", len(items))
    print("balance:", dict(collections.Counter(i["form"] for i in items)))
    assert len(items) == 32, len(items)
    assert collections.Counter(i["form"] for i in items) == {
        "should-as-rule": 16, "should-as-forecast": 16}
    assert len({i["id"] for i in items}) == 32, "ids must be unique"
    assert len({i["ainglish"] for i in items}) == 32, "no repeated ainglish sentence"
    assert len({i["english"] for i in items}) == 32, "no repeated gloss"
    for i in items:
        assert i["ainglish"].endswith(".") and i["english"].endswith(".")
        marker = i["form"]
        assert marker in i["ainglish"], f"{i['id']}: ainglish must carry its own marker"
        # The comparator is the COMPLETE careful mapping, so the gloss must never smuggle the
        # marked form back in -- that would compare the form against itself.
        assert "should-as-" not in i["english"], f"{i['id']}: gloss must not contain the marker"
        assert "should" not in i["english"], f"{i['id']}: gloss must be a mapping, not bare 'should'"
    print("per-item checks: unique ids/sentences/glosses, marker present, gloss marker-free")


if __name__ == "__main__":
    items = build()
    audit(items)
    blob = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    open("items.json", "w", encoding="utf-8").write(blob)
    print("\nitems.json sha256:", hashlib.sha256(blob.encode("utf-8")).hexdigest())
