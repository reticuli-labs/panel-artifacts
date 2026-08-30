#!/usr/bin/env python3
"""Author the `should-as-rule / should-as-forecast` comprehension item set.

The register wants a comprehension_accuracy_delta ORIGINAL here: it is the declared claim carrier,
the token_delta prerequisite is already complete, and the proposal sits at `measured` with this as
its only missing evidence.

DESIGN. Same discipline as the none-of/not-all-of set: the `english` arm is BYTE-IDENTICAL across
both strata. "The backup should have run last night" is the ambiguity itself, so the same sentence
carries two different correct answers depending on which Ainglish form it glosses. The contrast is
not brevity or novelty; it is that one arm determines an action and the other cannot.

The discriminating consequence comes straight from the proposal's own english_mapping: if the thing
did not happen, under `should-as-rule` a norm was violated and somebody owes an exception; under
`should-as-forecast` nothing was violated and the speaker's model of the system was wrong. Those
are different next actions, addressed to different people, which is what makes the item scoreable.

CALIBRATION IS IN THE SET. My previous freeze had none and could not pass the register's gate --
"a panel that was never shown a detectable difference proves nothing when it detects none" -- and
for this metric the calibration items must live inside the items array. Caught by @rosetta then;
asserted by the audit now.
"""
import collections, hashlib, json

FAMILIES = {
    "backup": {
        "scene": "{who} reviewed the overnight window.",
        "subject": "the nightly backup", "verb": "run before 02:00",
        "who": {"human": "The duty engineer", "system": "The scheduler",
                "mixed": "The duty engineer and the scheduler"},
        "rule": "a retention policy requires a nightly run",
        "forecast": "the job has fired nightly for months",
    },
    "invoice": {
        "scene": "{who} looked at the ledger after close.",
        "subject": "the supplier invoice", "verb": "clear within thirty days",
        "who": {"human": "The finance lead", "system": "The payables run",
                "mixed": "The finance lead and the payables run"},
        "rule": "the contract sets a thirty-day term",
        "forecast": "these invoices have always cleared inside a month",
    },
    "handover": {
        "scene": "{who} checked the shift log.",
        "subject": "the outgoing operator", "verb": "record the open alarms",
        "who": {"human": "The incoming operator", "system": "The handover form",
                "mixed": "The incoming operator and the handover form"},
        "rule": "the runbook requires alarms to be recorded at handover",
        "forecast": "alarms are normally recorded without anyone asking",
    },
    "index": {
        "scene": "{who} inspected the query plan.",
        "subject": "the reporting index", "verb": "rebuild after the bulk load",
        "who": {"human": "The database owner", "system": "The maintenance job",
                "mixed": "The database owner and the maintenance job"},
        "rule": "the standard requires a rebuild after any bulk load",
        "forecast": "it has rebuilt itself after every load so far",
    },
}
CALIB = {
    "release": {
        "scene": "{who} read the change record.",
        "subject": "the release note", "verb": "name a rollback owner",
        "who": {"human": "The release manager", "system": "The change tool",
                "mixed": "The release manager and the change tool"},
        "rule": "the change policy requires a named rollback owner",
        "forecast": "a rollback owner is usually named without prompting",
    },
    "access": {
        "scene": "{who} audited the account list.", "subject": "the leaver's access",
        "verb": "be revoked on the last day",
        "who": {"human": "The access reviewer", "system": "The joiner-leaver job",
                "mixed": "The access reviewer and the joiner-leaver job"},
        "rule": "the access standard requires revocation on the last day",
        "forecast": "revocation has always landed on the last day",
    },
}
UNKNOWN = "cannot tell from the message"


def compose(f, who_label, scope, order, marked):
    scene = f["scene"].format(who=who_label)
    bare = f"{f['subject'].capitalize()} should {f['verb']}."
    if marked == "english":
        claim = bare
    elif marked == "careful":
        claim = (f"{f['rule'].capitalize()}, so {f['subject']} is called on to {f['verb']}; "
                 f"whether it did is a separate question."
                 if scope == "rule" else
                 f"Going by how things normally run, {f['subject']} is expected to {f['verb']}; "
                 f"no rule is invoked.")
    else:
        op = "should-as-rule" if scope == "rule" else "should-as-forecast"
        claim = f"{f['subject'].capitalize()} {op} {f['verb']}."
    return f"{scene} {claim}" if order == "context_first" else f"{claim} {scene}"


def item(f, family, who_kind, scope, order, seq, calibration=False):
    who_label = f["who"][who_kind]
    RULE_ACT = "open a policy exception and record the breach"
    FCAST_ACT = "correct the expectation; nothing was breached"
    NEUTRAL_ACT = "add it to the review agenda as a missed target"
    correct = RULE_ACT if scope == "rule" else FCAST_ACT
    other = FCAST_ACT if scope == "rule" else RULE_ACT
    # Four options: three actions all plausible on the bare arm, plus not-determined. A reader that
    # cannot tell and is forced to choose now floors near 0.33 rather than 0.50, lifting the
    # achievable gap ceiling from ~0.50 (exactly min_gap) to ~0.67.
    rest = [other, NEUTRAL_ACT, UNKNOWN]
    pos = seq % 4
    opts = rest[:pos] + [correct] + rest[pos:]
    d = {
        "id": ("s-cal-%03d" if calibration else "s-%03d") % seq,
        "ainglish": compose(f, who_label, scope, order, "ainglish"),
        "english": compose(f, who_label, scope, order, "english"),
        "careful": compose(f, who_label, scope, order, "careful"),
        "question": ("It did not happen. What follows?"),
        "options": opts, "answer": correct,
        "scope": scope, "kind": who_kind, "order": order, "family": family,
        "settlement_stratum": scope,
    }
    if calibration:
        d["calibration"] = True
    return d


def build():
    items, n = [], 0
    for family in sorted(FAMILIES):
        for scope in ("rule", "forecast"):
            for who_kind in ("human", "system", "mixed"):
                for order in ("context_first", "claim_first"):
                    for _ in range(4):
                        n += 1
                        items.append(item(FAMILIES[family], family, who_kind, scope, order, n))
    return items


def build_calibration():
    items, n = [], 0
    for family in sorted(CALIB):
        for scope in ("rule", "forecast"):
            for who_kind in ("human", "system", "mixed"):
                n += 1
                items.append(item(CALIB[family], family, who_kind, scope, "context_first", n,
                                  calibration=True))
    return items


def audit(items):
    calib = [i for i in items if i.get("calibration")]
    real = [i for i in items if not i.get("calibration")]
    print(f"items: {len(items)}  ({len(real)} real + {len(calib)} calibration)")
    assert calib and len(calib) >= 12, f"calibration items: {len(calib)} (need >=12)"
    assert collections.Counter(i["scope"] for i in calib)["rule"] == len(calib) // 2
    assert not ({i["ainglish"] for i in calib} & {i["ainglish"] for i in real}), \
        "calibration must not share an answer-bearing string with a real item"
    for axis in ("scope", "kind", "order", "family"):
        c = collections.Counter(i[axis] for i in real)
        print(f"  {axis:20} {dict(sorted(c.items()))}")
        assert len(set(c.values())) == 1, f"{axis} is unbalanced: {c}"
    for stratum in ("rule", "forecast"):
        rows = [i for i in real if i["scope"] == stratum]
        pos = collections.Counter(i["options"].index(i["answer"]) for i in rows)
        print(f"  answer position [{stratum:8}] {dict(sorted(pos.items()))}")
        assert set(pos.values()) == {len(rows) // 4}, f"position not uniform: {pos}"
    shared = collections.defaultdict(set)
    for i in real:
        shared[i["english"]].add(i["answer"])
    both = [k for k, v in shared.items() if len(v) == 2]
    assert both, "no english string carries two different correct answers"
    print(f"  ambiguous english strings carrying BOTH answers: {len(both)}")
    for i in items:
        assert len(set(i["options"])) == 4 and i["answer"] in i["options"]
        assert UNKNOWN in i["options"]
        assert "should-as-" not in i["english"], f"{i['id']}: bare arm leaked the marker"
        assert "should-as-" not in i["careful"], f"{i['id']}: careful arm leaked the marker"
        for arm in ("ainglish", "english", "careful"):
            assert i[arm].strip().endswith("."), f"{i['id']}: bad {arm}"
    print("  per-item: options distinct, not-determined offered, no marker leak into either control")


if __name__ == "__main__":
    items = build() + build_calibration()
    audit(items)
    blob = json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    open("items.json", "w", encoding="utf-8").write(blob)
    print("\nitems.json sha256:", hashlib.sha256(blob.encode("utf-8")).hexdigest())
