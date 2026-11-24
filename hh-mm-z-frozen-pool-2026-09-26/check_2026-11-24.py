"""check_2026-11-24.py: a read-only check of two findings about this frozen pool, reported by Dexagon on the row's thread
(comment 2074f0e8 on e2902201, 2026-11-24). It reads the three seat files beside itself, refuses unless their bytes hash to the
digests published in the README, and writes check_2026-11-24.json. Run: python3 check_2026-11-24.py

1. Pins: the file-byte SHA-256 the README publishes against the digest the harness's fetch_items compares (SHA-256 of the parsed
   item array as canonical JSON: sorted keys, compact separators, ensure_ascii False), written out here from the harness's source.
2. The shortcut: a lookup that is taught on seat A and sees, for each real item, ONLY the event reference found in the message
   (two capitals, a hyphen, the seat letter, three digits) and the printed option texts. It never sees the clock, the date, the
   zone, the stem or any hidden field. Scored on seats B and C, from either arm's wording. A city name in an option is read as
   'local' (Dexagon's normalisation, repeated). When seat A's examples under one key do not agree on an option text, the lookup
   abstains.
3. What the reference adds: the same lookup keyed on the stem alone (no reference), and on the reference with the digit that
   names the stratum blanked. This part is mine, to say which part of the shortcut is the label and which is the design."""
import collections, hashlib, json, os, random, re
HERE = os.path.dirname(os.path.abspath(__file__)); COMMIT = "2daa3f44b8c057dc1dadfb856b2387c10a9ccbc7"   # the commit the thread pins; the seat files have not changed since
PUBLISHED = {"A": "9680ffd965892a96e5c6fb447ca378152b31546bf82ab62bf2a81de916c7d883", "B": "50cdad8979d774cbc36572f91a9e9e11ce4a23c40b0f5d7058b33e3ee5b81b5a", "C": "b7cae8a105b89437928788ed78c178d58f3a416021e97c7e61fcc2e5034a8311"}
DEXAGON = {"A": "2ac74e4bd2b010bd484164d97ec2373f3154711ee30e735ae44b1a9a84ffa09c", "B": "a50926ebcf8b6a63a19aa2ce1055f39849c17a35e96ce5f991165e917181ce5d", "C": "d72535b92fd689e199e266a348429f41d9cbbc4f33c80c4bdf672fe8866391a7"}
REF = re.compile(r"\b([A-Z]{2})-([ABC])(\d)(\d\d)\b")
CITIES = ["London", "New York", "Berlin", "Los Angeles", "Sydney", "Sao Paulo", "São Paulo", "Kolkata", "Tokyo"]
raw = {s: open(os.path.join(HERE, "seat-%s.items.json" % s), "rb").read() for s in "ABC"}
assert all(hashlib.sha256(raw[s]).hexdigest() == PUBLISHED[s] for s in "ABC"), "a seat file here is not the published one"
items = {s: json.loads(raw[s].decode("utf-8")) for s in "ABC"}
out = {"commit": COMMIT, "pins": {}, "lookup": {}}
for s in "ABC":
    it = items[s]; assert isinstance(it, list) and len(it) == 140
    canon = hashlib.sha256(json.dumps(it, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    out["pins"][s] = {"file_bytes_sha256": hashlib.sha256(raw[s]).hexdigest(), "equals_published": hashlib.sha256(raw[s]).hexdigest() == PUBLISHED[s], "canonical_item_array_sha256": canon, "equals_dexagon": canon == DEXAGON[s], "published_would_pass_fetch_items": canon == PUBLISHED[s]}


def norm(t):
    for c in CITIES: t = t.replace("the %s clock reading" % c, "the local clock reading")
    return t


def opts(x):
    """Printed option texts, in order, parsed from the question as a reader sees them."""
    m = re.findall(r"\b([A-D]) = (.*?)(?=\. [A-D] = |\.$)", x["question"]); assert [k for k, _ in m] == ["A", "B", "C", "D"], x["question"]
    return [(k, norm(v)) for k, v in m]


def stem(x): return x["question"].split(" A = ")[0]


def real(s): return [x for x in items[s] if not x.get("calibration")]


def keyfn(mode, arm):
    def f(x):
        m = REF.search(x[arm]); assert m, x[arm]
        if mode == "reference": return (m.group(3),)                    # the digit after the seat letter; prefix and running number carry nothing the lookup needs
        if mode == "reference_digit_blanked": return (m.group(1),)
        if mode == "stem": return (stem(x),)
        raise ValueError(mode)
    return f


def teach(mode, arm):
    f = keyfn(mode, arm); table = collections.defaultdict(set)
    for x in real("A"): table[f(x)].add(dict(opts(x))[x["answer"]])
    return {k: (next(iter(v)) if len(v) == 1 else None) for k, v in table.items()}


def score(mode, arm, seat):
    table = teach(mode, arm); f = keyfn(mode, arm); right = wrong = abstain = 0; per = collections.Counter()
    for x in real(seat):
        want = table.get(f(x))
        hit = [k for k, v in opts(x) if v == want] if want is not None else []
        if len(hit) != 1: abstain += 1; per[(x["settlement_stratum"], "abstain")] += 1
        elif hit[0] == x["answer"]: right += 1; per[(x["settlement_stratum"], "right")] += 1
        else: wrong += 1; per[(x["settlement_stratum"], "wrong")] += 1
    return {"right": right, "wrong": wrong, "abstain": abstain, "of": right + wrong + abstain, "by_stratum": {"%s:%s" % k: v for k, v in sorted(per.items())}}


for mode in ("reference", "reference_digit_blanked", "stem"):
    out["lookup"][mode] = {"%s_%s" % (seat, arm): score(mode, arm, seat) for seat in "BC" for arm in ("english", "ainglish")}
# the digit is the stratum's index in every real item of every seat
order = ["utc", "civil", "missing-date-utc", "missing-date-civil", "fold", "gap", "recurring-civil", "recurring-utc"]
digit = collections.Counter((x["settlement_stratum"], REF.search(x["english"]).group(3)) for s in "ABC" for x in real(s))
out["digit_by_stratum"] = {"%s:%s" % k: v for k, v in sorted(digit.items())}; out["digit_names_the_stratum"] = len(digit) == 8 and all(v == 48 for v in digit.values())
out["same_reference_in_both_arms"] = all(REF.search(x["english"]).group(0) == REF.search(x["ainglish"]).group(0) for s in "ABC" for x in real(s))
# control: the lookup taught on labels shuffled against their items must lose the recurring strata
rnd = random.Random(20261124); A = real("A"); perm = A[:]; rnd.shuffle(perm); f = keyfn("reference", "english"); t2 = collections.defaultdict(set)
for x, y in zip(A, perm): t2[f(x)].add(dict(opts(y))[y["answer"]])
out["control_shuffled_teaching_keys_with_one_answer"] = sum(1 for v in t2.values() if len(v) == 1)
json.dump(out, open(os.path.join(HERE, "check_2026-11-24.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False, sort_keys=True); print(json.dumps(out, indent=1, ensure_ascii=False, sort_keys=True))
