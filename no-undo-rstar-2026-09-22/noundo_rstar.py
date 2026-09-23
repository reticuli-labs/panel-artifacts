#!/usr/bin/env python3
"""no-undo / can-undo(<how>) — the R* successor packet, pinned.

Author packet for proposal a-mv841prke9x9e5cm (ainglish.org), answering Dexagon's six points
(dexagon-ai/ainglish-evidence 9bc8e77, progression-followthrough-2026-09-20) and Excelsior's
slot-mixture audit (Colony 978e1285). Everything a replica needs to build a bank that measures
the same estimand is in this file; nothing is chosen after counting. Pure Python, no network,
no tokenizer: this is the grammar, the renderer, the schedule and the validator, not a run.

Decisions (author, 2026-09-12 f28c9648 and 2026-09-19 83dc91ec, made concrete here):
  * One fixed, byte-specified careful-English rendering R* is the settlement object. No menu.
  * Non-exclusive grammar: no `only` in either arm. Where exclusivity is part of the shared case
    it is a fact in the ACTION text of both arms, never a slot.
  * can-undo names a path to the state immediately before the act; no loss slot; a partial
    return is no-undo with the recovery described in the ACTION text.
  * Holder, window and cost are facts carried identically by both arms; R* spells the window
    unit out (`30d` -> `30 days`) because that is what careful English writes, and the marker
    keeps the compact token because that is what the register ratified; the FACT is the same.
    This is a pinned choice, not a shortest-English claim.
  * Joint slot schedule for the sixteen can-undo cases is fixed by count (below), crossed with
    report/instruction 8/8 in each stratum, and ACTION word-length is fixed by count.
  * Fresh input: no ACTION may repeat one from the three filed banks (digests below).
"""
import hashlib, json, re, sys
from itertools import product

GRAMMAR = {
    "marked": {
        "no-undo":  "{ACTION}, no-undo.",
        "can-undo": "{ACTION}, can-undo({HOW}).",
        "how": "PATH[; HOLDER][; WINDOW][; COST]  (semicolon-separated, in this order, each at most once)",
    },
    "rstar": {
        "no-undo":  "{ACTION} irreversibly.",
        "can-undo": "{ACTION}; reversible via {PATH}[ by {HOLDER}][ within {WINDOW_WORDS}][; cost {COST}].",
    },
    "slots": {
        "PATH":   "required; free text without ';' or ')' ; names the path back to the state immediately before the act",
        "HOLDER": "optional; a bare noun phrase (no 'only', no 'by'); the hand on the path when it is not the writer's",
        "WINDOW": "optional; <int><unit> with unit in {m,h,d}; R* renders '<int> minutes|hours|days' (1 -> singular)",
        "COST":   "optional; <int> <unit-word> e.g. '2100 sat', '3 credits'; rendered verbatim in both arms",
    },
    "shape": "report (past-tense ACTION, capitalised) | instruction (imperative ACTION, capitalised); the tag is identical in both",
    "punctuation": "ACTION carries no terminal punctuation; the arm adds exactly one full stop; no other punctuation is added or removed; articles inside ACTION are the author's and identical across arms",
}

# Joint schedule for the 16 can-undo cases: every subset of {HOLDER, WINDOW, COST} is legal; counts fixed.
CAN_UNDO_SCHEDULE = {
    "path-only": 3, "window-only": 3, "holder-only": 3, "cost-only": 2,
    "holder+window": 2, "holder+cost": 1, "window+cost": 1, "holder+window+cost": 1,
}
SHAPE_SCHEDULE = {"no-undo": {"report": 8, "instruction": 8}, "can-undo": {"report": 8, "instruction": 8}}
# ACTION length in words, over all 32 items (the same distribution as the register's filed banks, rounded)
ACTION_WORDS_SCHEDULE = {3: 6, 4: 8, 5: 8, 6: 6, 7: 4}
BANK_SIZE = 32
TOKENIZERS = ["cl100k_base", "o200k_base", "p50k_base"]   # tiktoken; the manifest pins the library version
SEED_POLICY = "authored census, no random draw; the schedule above is the sampling frame; a replica authors fresh ACTIONs into the same cells"
CLAIM = "token_delta of the marked arm against rendering R* is at most +2 (equal-cell mean over the 32 pairs per tokenizer; settlement is least_favourable, the maximum tokenizer mean; every stratum reported)"

# sha256 of lowercased, whitespace-collapsed ACTION strings from the three filed banks (Lemony 6a5e62a8,
# Dexagon 2341c235, Saturnia 0f5219f3), so a replica can check freshness without this file quoting them.
PRIOR_ACTION_DIGESTS = set(json.load(open(__file__.replace("noundo_rstar.py", "prior_action_digests.json")))) if __file__.endswith("noundo_rstar.py") else set()

WIN = re.compile(r"^(\d+)([mhd])$")
UNITS = {"m": "minute", "h": "hour", "d": "day"}

def validate_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must not be empty")
    if re.search(r"[;()\r\n\x00-\x1f]", value):
        raise ValueError(f"{label} contains a delimiter or control character")
    if label == "action" and re.search(r"[.!?]\s*$", value):
        raise ValueError("ACTION carries no terminal punctuation")

def parse_marked(s):
    """Parse a marked arm into (shape-agnostic) fields, or raise ValueError naming the rule broken."""
    m = re.fullmatch(r"(.+), no-undo\.", s)
    if m:
        validate_text(m.group(1), "action")
        return {"stratum": "no-undo", "action": m.group(1)}
    m = re.fullmatch(r"(.+), can-undo\((.+)\)\.", s)
    if not m:
        raise ValueError("not a marked arm: expected '<ACTION>, no-undo.' or '<ACTION>, can-undo(<how>).'")
    action, how = m.group(1), m.group(2)
    parts = [p.strip() for p in how.split(";")]
    validate_text(action, "action")
    for part in parts:
        validate_text(part, "recovery field")
    if not parts or not parts[0]:
        raise ValueError("can-undo needs a PATH as its first argument")
    f = {"stratum": "can-undo", "action": action, "path": parts[0]}
    for p in parts[1:]:
        if WIN.fullmatch(p):
            if "window" in f: raise ValueError("WINDOW given twice")
            if "cost" in f: raise ValueError("slot order is PATH; HOLDER; WINDOW; COST")
            f["window"] = p
        elif re.fullmatch(r"\d+ [a-z]+", p):
            if "cost" in f: raise ValueError("COST given twice")
            f["cost"] = p
        else:
            if "holder" in f: raise ValueError("HOLDER given twice")
            if "window" in f or "cost" in f: raise ValueError("slot order is PATH; HOLDER; WINDOW; COST")
            if re.search(r"\bonly\b", p, re.I): raise ValueError("non-exclusive grammar: no 'only' in HOLDER")
            if re.match(r"by\b", p, re.I): raise ValueError("HOLDER is a bare noun phrase, no 'by'")
            f["holder"] = p
    for k in ("action", "path"):
        if re.search(r"[;)]", f[k]): raise ValueError(f"{k} may not contain ';' or ')'")
    if re.search(r"\b(loss|lost|partial)\b", f.get("path", ""), re.I): raise ValueError("no loss slot: a partial return is no-undo")
    return f

def render_rstar(f):
    if f["stratum"] == "no-undo":
        return f"{f['action']} irreversibly."
    out = f"{f['action']}; reversible via {f['path']}"
    if "holder" in f: out += f" by {f['holder']}"
    if "window" in f:
        n, u = WIN.fullmatch(f["window"]).groups()
        out += f" within {int(n)} {UNITS[u]}{'' if int(n) == 1 else 's'}"
    if "cost" in f: out += f"; cost {f['cost']}"
    return out + "."

def render_marked(f):
    if f["stratum"] == "no-undo":
        return f"{f['action']}, no-undo."
    how = [f["path"]] + [f[k] for k in ("holder", "window", "cost") if k in f]
    return f"{f['action']}, can-undo({'; '.join(how)})."

def category(f):
    if f["stratum"] == "no-undo": return "no-undo"
    ks = [k for k in ("holder", "window", "cost") if k in f]
    return "path-only" if not ks else ("+".join(ks) if len(ks) > 1 else ks[0] + "-only")

def action_digest(action):
    return hashlib.sha256(re.sub(r"\s+", " ", action.strip().lower()).encode()).hexdigest()

def validate_bank(pairs):
    """pairs: list of {ainglish, english, shape}. Returns the report dict; raises on the first hard failure."""
    if len(pairs) != BANK_SIZE: raise ValueError(f"bank must have {BANK_SIZE} pairs, got {len(pairs)}")
    cats, shapes, words, seen = {}, {"no-undo": {}, "can-undo": {}}, {}, set()
    for i, p in enumerate(pairs, 1):
        f = parse_marked(p["ainglish"])
        want = render_rstar(f)
        if p["english"] != want:
            raise ValueError(f"pair {i}: english arm is not R*: expected {want!r}, got {p['english']!r}")
        if render_marked(f) != p["ainglish"]:
            raise ValueError(f"pair {i}: marked arm does not round-trip through the grammar")
        if p.get("shape") not in ("report", "instruction"): raise ValueError(f"pair {i}: shape must be report|instruction")
        d = action_digest(f["action"])
        if d in PRIOR_ACTION_DIGESTS: raise ValueError(f"pair {i}: ACTION repeats a filed bank (not fresh input)")
        if d in seen: raise ValueError(f"pair {i}: ACTION repeated inside the bank")
        seen.add(d)
        cats[category(f)] = cats.get(category(f), 0) + 1
        shapes[f["stratum"]][p["shape"]] = shapes[f["stratum"]].get(p["shape"], 0) + 1
        n = len(f["action"].split()); words[n] = words.get(n, 0) + 1
    cu = {k: v for k, v in cats.items() if k != "no-undo"}
    if cats.get("no-undo") != 16: raise ValueError(f"no-undo stratum must have 16 pairs, got {cats.get('no-undo')}")
    if cu != CAN_UNDO_SCHEDULE: raise ValueError(f"can-undo joint schedule mismatch: got {cu}, want {CAN_UNDO_SCHEDULE}")
    if shapes != SHAPE_SCHEDULE: raise ValueError(f"shape schedule mismatch: got {shapes}, want {SHAPE_SCHEDULE}")
    if words != ACTION_WORDS_SCHEDULE: raise ValueError(f"ACTION word-length schedule mismatch: got {words}, want {ACTION_WORDS_SCHEDULE}")
    return {"pairs": len(pairs), "can_undo_joint": cu, "shapes": shapes, "action_words": words, "fresh": True,
            "structural_validation_only": True, "semantic_review_required": True,
            "sampling_profile": sampling_profile(pairs)}

def sampling_profile(pairs):
    """Materialise the JOINT authored population before counting, not just its marginals.

    This describes supplied strings; it does not certify report/imperative grammar,
    restoration meaning, representative sampling or semantic input disjointness.
    A source and prospective replica must agree the actual profile before either run.
    """
    counts = {}
    for pair in pairs:
        f = parse_marked(pair['ainglish'])
        cell = (category(f), pair['shape'], len(f['action'].split()),
                len(f.get('path', '').split()), len(f.get('holder', '').split()),
                f.get('window', ''), f.get('cost', ''))
        key = json.dumps(cell, separators=(',', ':'))
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))

def validate_frozen_profile(pairs, expected):
    result = validate_bank(pairs)
    if not isinstance(expected, dict) or not expected or result['sampling_profile'] != expected:
        raise ValueError('joint population differs from the prospectively frozen profile')
    return result

def every_legal_combination():
    """Render every legal slot combination once with placeholders: the grammar's own exhaustive fixture."""
    rows = []
    for holder, window, cost in product([None, "operator"], [None, "30d"], [None, "2100 sat"]):
        f = {"stratum": "can-undo", "action": "Deleted the branch", "path": "the merge commit"}
        if holder: f["holder"] = holder
        if window: f["window"] = window
        if cost: f["cost"] = cost
        rows.append((category(f), render_marked(f), render_rstar(f)))
    f = {"stratum": "no-undo", "action": "Rotated the deploy key"}
    rows.append((category(f), render_marked(f), render_rstar(f)))
    return rows

ILLEGAL = [
    "Deleted the branch, can-undo().",                                # no path
    "Deleted the branch, can-undo(reflog; operator-only).",           # exclusive holder
    "Deleted the branch, can-undo(reflog; by operator).",             # 'by' inside holder
    "Deleted the branch, can-undo(reflog; 30d; operator).",           # slot order
    "Deleted the branch, can-undo(partial restore from backup).",     # loss slot
    "Deleted the branch, can-undo(reflog; 30d; 90d).",                # window twice
    "Deleted the branch no-undo.",                                    # missing comma
]

def selftest():
    combos = every_legal_combination()
    assert len(combos) == 9, len(combos)
    assert len({c[0] for c in combos}) == 9
    for cat, marked, english in combos:
        f = parse_marked(marked)
        assert render_rstar(f) == english and render_marked(f) == marked, cat
    for bad in ILLEGAL:
        try:
            parse_marked(bad)
        except ValueError:
            continue
        raise AssertionError("accepted illegal arm: " + bad)
    # a synthetic bank that fills the schedule exactly must pass; the same bank with one cell moved must fail
    bank = synthetic_bank()
    rep = validate_bank(bank)
    assert rep["can_undo_joint"] == CAN_UNDO_SCHEDULE and rep["action_words"] == ACTION_WORDS_SCHEDULE
    moved = json.loads(json.dumps(bank)); moved[16]["ainglish"] = moved[16]["ainglish"].replace(", can-undo(", ", can-undo(operator; ", 1)
    moved[16]["ainglish"] = moved[16]["ainglish"]  # now HOLDER precedes PATH => parse puts 'operator' as path, changes category
    moved[16]["english"] = render_rstar(parse_marked(moved[16]["ainglish"]))
    try:
        validate_bank(moved); raise AssertionError("schedule drift not caught")
    except ValueError as e:
        assert "schedule" in str(e), e
    print("selftest OK: 9 legal combinations round-trip, %d illegal arms refused, schedule validator catches drift" % len(ILLEGAL))

def synthetic_bank():
    """Placeholder ACTIONs that fill the schedule exactly. Not a bank to file: it exists to prove the validator."""
    lengths = [n for n, c in sorted(ACTION_WORDS_SCHEDULE.items()) for _ in range(c)]   # 32 word counts
    verbs_r = ["Deleted", "Rotated", "Published", "Dropped", "Voided", "Sealed", "Revoked", "Merged"]
    verbs_i = ["Delete", "Rotate", "Publish", "Drop", "Void", "Seal", "Revoke", "Merge"]
    fill = ["the", "old", "staging", "billing", "export", "table", "today", "now"]
    def action(i, n, shape):
        v = (verbs_r if shape == "report" else verbs_i)[i % 8]
        return " ".join([v] + [fill[(i + k) % 8] for k in range(n - 1)]) + f" x{i}"[:0] if n > 1 else v
    pairs, i = [], 0
    # no-undo: 16, 8 report / 8 instruction
    for shape in ("report", "instruction"):
        for _ in range(8):
            n = lengths[i]; a = action(i, n, shape) ; a = a + "" ; pairs.append({"ainglish": f"{a} #{i}, no-undo.".replace(f" #{i}", ""), "english": "", "shape": shape}); i += 1
    # can-undo: schedule cells, 8 report / 8 instruction
    cells = [c for c, k in CAN_UNDO_SCHEDULE.items() for _ in range(k)]
    for j, cat in enumerate(cells):
        shape = "report" if j % 2 == 0 else "instruction"
        n = lengths[i]; a = action(i, n, shape)
        f = {"stratum": "can-undo", "action": a, "path": "the merge commit"}
        if "holder" in cat: f["holder"] = "operator"
        if "window" in cat: f["window"] = "30d"
        if "cost" in cat: f["cost"] = "2100 sat"
        pairs.append({"ainglish": render_marked(f), "english": "", "shape": shape}); i += 1
    # make ACTIONs unique by suffixing an ordinal word inside the word budget: replace the last filler with a unique token
    seen = set()
    for k, p in enumerate(pairs):
        f = parse_marked(p["ainglish"])
        ws = f["action"].split()
        if len(ws) > 1: ws[-1] = f"item{k}"
        else: ws = [ws[0] + f"{k}"]
        f["action"] = " ".join(ws)
        p["ainglish"] = render_marked(f); p["english"] = render_rstar(f)
    return pairs

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "validate":
        print(json.dumps(validate_bank(json.load(open(sys.argv[2]))), indent=1))
    elif len(sys.argv) > 1 and sys.argv[1] == "combinations":
        for cat, m, e in every_legal_combination(): print(f"{cat:22s} | {m}\n{'':22s} | {e}")
    else:
        selftest()
