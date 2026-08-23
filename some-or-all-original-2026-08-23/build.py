#!/usr/bin/env python3
"""Assemble the some-or-all / some-but-not-all comprehension item blocks.
Keys are COMPUTED from form semantics (constraints on property-count k over a set of size N),
never hand-typed. Form-lint: question content words must be disjoint from both arms' content
words (stopwords excluded). Outcome-blind: reads no reader output."""
import json, re, sys, hashlib, math
sys.path.insert(0, "/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad/soa")
from banks import SC

YES, NO, CT = "yes", "no", "cannot tell from the statement"
OPTIONS = ["yes", "no", "cannot tell from the statement"]

def bounds(form, n):
    return (1, n) if form == "soa" else (1, n - 1)

def answer(query, form, n):
    """Evaluate a query against the form's constraint 1<=k<=max on set size n."""
    lo, hi = bounds(form, n)
    if query == "exists_nonP_actual":            # is there a member without P?
        return YES if hi < n else CT             # forced iff k<n always; k>=1 always so never 'no'
    if query == "exists_P_actual":               # is there a member with P?
        return YES                               # lo>=1 in both forms
    if query == "allP_actual":                   # is the whole set P?
        if hi < n: return NO
        return CT
    if query == "allP_possible":                 # could the whole set be P, per the claim?
        return YES if hi == n else NO
    if query == "noneP_possible":                # could no member be P?
        return NO                                # lo>=1
    if query == "majority_actual":               # are more than half P?
        need = n // 2 + 1
        if hi < need: return NO
        if lo >= need: return YES
        return CT
    if query == "guarantee_nonP":                # does the claim guarantee a non-P member?
        return YES if hi < n else NO
    if query == "guarantee_P":
        return YES
    if query == "consistent_allP":
        return YES if hi == n else NO
    if query == "contradicted_by_noneP":         # would observing none-P contradict the claim?
        return YES
    if query == "contradicted_by_allP":
        return YES if hi < n else NO
    if query == "settles_count":
        return NO
    if query == "settles_which":
        return NO
    raise ValueError(query)

# (template_key, query, phrasings) — phrasings are functions of scenario s
TEMPLATES = [
 ("O_EXNP", "exists_nonP_actual", [
    lambda s: f"Judging from the statement alone, does {s['ni']} remain {s['loc']}?",
    lambda s: f"Reading just that statement: is {s['ni']} to be found {s['loc']}?",
    lambda s: f"Based purely on the statement, is there {s['ni']} {s['loc']}?"]),
 ("O_EXP", "exists_P_actual", [
    lambda s: f"Going by the statement alone, is there {s['pi']} {s['loc']}?",
    lambda s: f"Taking the statement at face value, does {s['pi']} exist {s['loc']}?"]),
 ("O_ALLP_ACT", "allP_actual", [
    lambda s: f"Per the statement alone, is it the case that {s['sa']}?",
    lambda s: f"Going strictly by the statement, has it come to the point where {s['sa']}?"]),
 ("O_ALLP_POS", "allP_possible", [
    lambda s: f"As far as the statement goes, could it turn out that {s['sa']}?",
    lambda s: f"Reading just the statement, is a situation where {s['sa']} still on the table?"]),
 ("O_NONE_POS", "noneP_possible", [
    lambda s: f"As far as the statement goes, could it be that {s['sn']}?",
    lambda s: f"Per the statement alone, is a situation where {s['sn']} still possible?"]),
 ("O_MAJ", "majority_actual", [
    lambda s: f"Judging from the statement alone, are more than half of the {s['mp']} affected this way?",
    lambda s: f"Going strictly by the statement, does this reach a clear majority of the {s['mp']}?"]),
 ("M_GNP", "guarantee_nonP", [
    lambda s: f"Does the statement, by itself, guarantee that {s['ni']} remains {s['loc']}?",
    lambda s: f"Is the existence of {s['ni']} guaranteed by the statement alone?",
    lambda s: f"Someone needs {s['ni']}. Does the statement settle that they will find it?"]),
 ("M_GP", "guarantee_P", [
    lambda s: f"Does the statement, on its own, guarantee that {s['pi']} exists {s['loc']}?",
    lambda s: f"Is the existence of {s['pi']} settled by the statement alone?"]),
 ("M_CONS_ALLP", "consistent_allP", [
    lambda s: f"Is the statement compatible with a situation where {s['sa']}?",
    lambda s: f"Would it be consistent with the statement if, in fact, {s['sa']}?"]),
 ("M_CONTRA_NONE", "contradicted_by_noneP", [
    lambda s: f"Suppose a later check finds that {s['sn']}. Would that finding contradict the statement?",
    lambda s: f"If it emerged that {s['sn']}, would the statement have been wrong?"]),
 ("M_CONTRA_ALLP", "contradicted_by_allP", [
    lambda s: f"Suppose a later check finds that {s['sa']}. Would that finding contradict the statement?",
    lambda s: f"If it emerged that {s['sa']}, would the statement have been wrong?"]),
 ("M_COUNT", "settles_count", [
    lambda s: f"Does the statement pin down precisely how many of the {s['mp']} are involved?",
    lambda s: f"Can the exact number of affected {s['mp']} be recovered from the statement alone?"]),
 ("M_WHICH", "settles_which", [
    lambda s: f"Does the statement identify specifically which of the {s['mp']} are involved?",
    lambda s: f"Could a reader single out the affected {s['mp']} individually from the statement alone?"]),
]
# per-form allocation over 112 slots (56 scenarios x 2)
ALLOC = [("O_EXNP",14),("O_EXP",10),("O_ALLP_ACT",8),("O_ALLP_POS",10),("O_NONE_POS",8),
         ("O_MAJ",10),("M_GNP",14),("M_GP",8),("M_CONS_ALLP",10),("M_CONTRA_NONE",6),
         ("M_CONTRA_ALLP",6),("M_COUNT",4),("M_WHICH",4)]
assert sum(n for _, n in ALLOC) == 112
TMAP = {k: (q, ph) for k, q, ph in TEMPLATES}

def claims(s, form):
    if form == "soa":
        ain = f"Some-or-all {s['np']} {s['vp']}."
        eng = f"At least one {s['ns']} {s['vs']}, and every {s['ns']} {s['vm']}."
    else:
        ain = f"Some-but-not-all {s['np']} {s['vp']}."
        eng = f"At least one but fewer than all {s['np']} {s['vp']}."
    return ain, eng

STOP = set("""a an the is are was were be been being do does did done have has had having of to in on at by for
with as from into over under after before during this that these those it its it's they them their there here
and or but not no nor so if then than when while would could should shall will can may might must going per
just still yet about alone purely strictly per suppose later finds finding found emerged fact wrong statement
face value reading judging taking based going goes turn turned come comes came point situation case table
whether someone needs settle settled settles guarantee guaranteed pin down precisely exactly recovered reader
single out individually specifically involved affected way clear reach reaches remain remains exist exists
existence compatible consistent contradict contradicted possible possibly half more most many much who whose
what which how could-it new own itself themselves""".split())

def content_words(text):
    toks = re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower().replace("-", " "))
    return {t for t in toks if len(t) >= 3 and t not in STOP}

def lint_item(item):
    qw = content_words(item["question"])
    bad = {}
    for arm in ("english", "ainglish"):
        overlap = qw & content_words(item[arm])
        if overlap: bad[arm] = sorted(overlap)
    return bad

def build_form(form):
    items, lint_fails = [], []
    # deterministic template assignment: spread ALLOC across 112 slots, interleaved by stride
    slots = []
    for tkey, cnt in ALLOC: slots += [tkey] * cnt
    # deterministic shuffle: fixed stride permutation (co-prime with 112)
    perm = [(i * 45) % 112 for i in range(112)]
    assigned = [slots[p] for p in perm]
    counters = {}
    for idx in range(112):
        s = SC[idx % 56]; second_pass = idx >= 56
        tkey = assigned[idx]
        query, phr = TMAP[tkey]
        counters[tkey] = counters.get(tkey, 0)
        phrase = phr[counters[tkey] % len(phr)]; counters[tkey] += 1
        ain, eng = claims(s, form)
        lead = s["lead"]
        NEUTRAL_LOC = ["at this point", "as things stand", "among them", "right now"]
        s = dict(s, loc=NEUTRAL_LOC[(idx % 56) % 4],
                 sa=s["sa"].replace("every ", "each "), sn=s["sn"].replace("every ", "each "),
                 pi=s["pi"].replace("every ", "each "), ni=s["ni"].replace("every ", "each "))
        item = {
            "id": f"{form}-{s['dom'][:3]}-{idx:03d}",
            "english": f"{lead} {eng}",
            "ainglish": f"{lead} {ain}",
            "question": phrase(s),
            "options": OPTIONS,
            "answer": answer(query, form, s["n"]),
            "meta": {"domain": s["dom"], "n": s["n"], "template": tkey, "query": query},
        }
        bad = lint_item(item)
        if bad: lint_fails.append((item["id"], bad, item["question"]))
        items.append(item)
    return items, lint_fails

def report(items, form):
    from collections import Counter
    keys = Counter(i["answer"] for i in items)
    doms = Counter(i["meta"]["domain"] for i in items)
    tmps = Counter(i["meta"]["template"] for i in items)
    print(f"[{form}] n={len(items)} keys={dict(keys)}")
    print(f"      domains={dict(doms)}")
    print(f"      templates={dict(tmps)}")

if __name__ == "__main__":
    all_fail = 0
    for form in ("soa", "sba"):
        items, fails = build_form(form)
        report(items, form)
        # uniqueness
        ids = [i["id"] for i in items]; assert len(set(ids)) == len(ids)
        qs = [(i["english"], i["question"]) for i in items]; assert len(set(qs)) == len(qs), "dup arm+question"
        if fails:
            all_fail += len(fails)
            print(f"  LINT FAILURES ({len(fails)}):")
            for fid, bad, q in fails[:15]:
                print(f"   {fid}: {bad}")
                print(f"      Q: {q[:110]}")
        json.dump(items, open(f"/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad/soa/{form}_items.json", "w"), indent=1, ensure_ascii=False)
    print("TOTAL LINT FAILURES:", all_fail)
