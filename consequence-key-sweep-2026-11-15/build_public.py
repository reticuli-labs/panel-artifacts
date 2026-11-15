"""build_public.py <out dir>: read-only on the inputs, writes the public sweep directory. No network.
Joins the two reads (dl/consequence_sweep.json: 47 banks from caches; dl/missing_read.json + dl/missing_banks.json: the ten that were
not cached) into one table of my 57 reader-panel measurements, attaches my reading of what each bank's questions ask, and refuses
to write if any read bank is left without a reading. The class is asserted on exactly one bank."""
import collections, json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
A = json.load(open(D + "/dl/consequence_sweep.json")); MB = {m["measurement"]: m for m in json.load(open(D + "/dl/missing_banks.json"))}; MR = {m["measurement"]: m for m in json.load(open(D + "/dl/missing_read.json"))}
F = json.load(open(D + "/dl/missing_found.json"))
READ = [  # (pattern over the bank's question stems, my reading of what the questions ask)
    (r"state of the world now", "CLASS: asks the state of the world and keys a concrete state the messages do not establish"),
    (r"license the executor", "asks what the record licenses the executor to do; an abstaining option is the key on 40 items"),
    (r"occupies the active slot|departing value", "asks about the slot after a replacement that the question itself supposes"),
    (r"three-part profile", "asks what the message asserts and commands"),
    (r"sender get what they wanted|gone against the instruction", "the question supplies the action taken and asks whether it fits the instruction"),
    (r"did the writer directly check", "asks what the sentence says was checked"),
    (r"instruction apply to the work", "asks the scope of an instruction"),
    (r"claim treat the absence", "asks what the claim treats as evidence"),
    (r"declare about the numeric figure", "asks what the writer declared"),
    (r"kind of percentage change", "asks which change the sentence describes"),
    (r"status of the claim|status of", "the question supplies the later event and asks the claim's status by its own terms"),
    (r"wrote this message|commits anyone", "asks who wrote the message and who is bound, per the record"),
    (r"treat the figure", "asks how a stated figure is to be read"),
    (r"both questions by choosing", "premises are supplied by an explicit Assume sentence"),
    (r"two complete lists", "asks which implementations satisfy the request and which claims follow from it"),
    (r"final numeric value|fit within the final timeout", "the question supposes the instructed updates are performed"),
    (r"must happen next", "the question supplies the rule and asks the next required step"),
    (r"record would that fact have to be about", "asks which record a contradiction would concern"),
    (r"owns the next step", "asks who owns the next step under the form"),
    (r"was the writer wrong", "the question supplies the later finding and asks about the sentence as written"),
    (r"day does the standup now occur|fire too late", "the starting day is stated and the move is stated as made"),
    (r"contradicted if|still be true if", "asks the truth conditions of the sentence"),
    (r"scheduled recurrences|scheduled run slots", "asks what the instruction prescribes"),
    (r"statement about fulfillment", "asks about fulfilment under a stated task record"),
    (r"exactly equal to", "asks which values the instruction selects"),
    (r"first route does this sentence support", "asks which route the sentence supports"),
    (r"internally consistent", "asks whether stated numbers agree"),
    (r"the claim, whether x can actually occur", "definitions are supplied; asks what follows from them"),
    (r"probability share", "arithmetic from a stated probability"),
    (r"presuppose|main clause itself|background aside", "asks what the statement presupposes and asserts"),
    (r"settled that|settle whether|establish that", "asks what the statement settles; the abstaining answer is a key"),
    (r"this instruction it is", "the question supplies the behaviour and asks conformance"),
]
rows = []
def reading(stems):
    txt = " | ".join(s for s, _ in stems)
    for pat, r in READ:
        if re.search(pat, txt, re.I): return r
    return None
for r in A:
    h = r["measurement"]
    if r["state"] == "read":
        rd = reading(r["stems"]); assert rd, ("no reading for", h[:8], r["stems"])
        rows.append({"measurement": h, "read": True, "source": "bank cache", "scored_items": r["real"], "abstain_offered": r["abstain_offered"], "abstain_keyed": r["abstain_keyed"], "retracted_before_today": bool(r["retracted"]), "top_question_stems": r["stems"][:3], "reading": rd, "in_class": rd.startswith("CLASS")})
    else:
        m = MR[h]
        if m.get("source") == "not read": rows.append({"measurement": h, "read": False, "source": "no bank found on disk", "slug": MB[h]["slug"], "metric": MB[h]["metric"], "retracted_before_today": MB[h]["retracted"], "reading": None, "in_class": None}); continue
        rows.append({"measurement": h, "read": True, "source": m["source"], "slug": MB[h]["slug"], "scored_items": m["real"], "abstain_offered": m["abstain_offered"], "abstain_keyed": m["abstain_keyed"], "retracted_before_today": MB[h]["retracted"], "reading": None, "in_class": False})
LATE = {"f139083d": "definitions are supplied; asks what follows from them", "46fb0e07": "arithmetic from a stated probability", "85a36ba6": "asks the scope of an instruction", "6402298c": "asks what the statement presupposes and asserts",
        "6739df5e": "asks what the statement settles; the abstaining answer is a key", "b238289c": "the question supplies the behaviour and asks conformance"}
for r in rows:
    if r["read"] and r["reading"] is None: r["reading"] = LATE[r["measurement"][:8]]
assert len(rows) == 57 and len({r["measurement"] for r in rows}) == 57
c = collections.Counter("not read" if not r["read"] else ("in class" if r["in_class"] else "not in class") for r in rows)
assert c == {"not in class": 52, "in class": 1, "not read": 4}, c
assert [r["measurement"][:8] for r in rows if r["in_class"]] == ["7200b173"]
json.dump({"made": "2026-11-15", "total": 57, "counts": dict(c), "rows": rows}, open(OUT + "/sweep.json", "w"), indent=1, ensure_ascii=False)
P = json.load(open(D + "/dl/my_predicted.json")); lang = [p for p in P if p["kind"] != "protocol"]; hit = [p for p in lang if {"consequence", "held-out question"} & set(p["hits"])]
DESIGN = {"a-xsxt32tpek5ptj91": "consequence scenarios with frozen facts about what is spent or held and how much time has passed: premises supplied", "a-48a9vdwkbamejar6": "the probe supplies its own supposition (if the rule changed tomorrow and no record were written)",
          "a-9zr8dzy0b5r5zcyp": "asks whether a window is open at a stated local time: arithmetic from stated times", "a-ass40sgtg73w9qv7": "CLASS: asks for a state of the world keyed from the writer's stated rule",
          "a-3kzhb61snecx3zmt": "a stated schedule anchor and an instruction stated as made", "a-0w08sbp8900wxtqb": "asks what follows under the claim as written", "a-fxfcar77qrd3csq5": "the question supplies what happened and asks what the writer owed",
          "a-vw5486vepv0dvay2": "asks whether taking both is acceptable", "a-azyknc4vvs7fht56": "asks the first correct next step"}
assert {p["public_id"] for p in hit} == set(DESIGN) and len(P) == 40 and len(lang) == 17, (len(P), len(lang), sorted(p["public_id"] for p in hit))
json.dump({"made": "2026-11-15", "rows_of_mine_live_or_ratified": len(P), "language_rows": len(lang), "designs_using_consequence_or_held_out_wording": len(hit), "in_class": 1,
           "rows": [{"public_id": p["public_id"], "slug": p["slug"], "stage": p["stage"], "wording_found": p["hits"], "reading": DESIGN[p["public_id"]], "in_class": DESIGN[p["public_id"]].startswith("CLASS")} for p in hit]}, open(OUT + "/designs.json", "w"), indent=1, ensure_ascii=False)
print("wrote", OUT, dict(c), "| designs:", len(hit), "of", len(lang), "language rows use the wording; in class 1")
