"""Outside challenge cases for Excelsior's multiplier-plus-comparative checker (v1.0.0, frozen 2026-11-11), written by the author of
the proposal it is built from (a-cjgt374hndvt1jqa). 16 pairs, 32 sentences. Each pair shares its multiplier and differs in one phrase.
Labels follow the proposal's registered text: a multiplier attached to a comparative is refused (warn); an iteration count and a
multiplier attached to the quantity are not (leave alone). Written after reading the rule, so these are adversarial cases, not a
sample of ordinary writing and not an estimate of anything. The bank is frozen (file + sha256) BEFORE either rule is run on it:
`python3 build_and_run.py freeze` writes the bank and refuses to overwrite; `python3 build_and_run.py run <the checker's 64 cases as JSON>`
reads the bank back, checks the port of the rule against those 64 published cases (24 / 7 / 8 / 25), and runs both rules."""
import collections, hashlib, json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)); BANK = os.path.join(D, "outside_pairs_v1.json")
PAIRS = [
 # group "iteration": the same multiplier phrase counts extra attempts in one sentence and compares two quantities in the other
 ("iteration", "We retried the upload 3 times more before it went through.", "The upload failed 3 times more often than the download."),
 ("iteration", "She knocked two times more and then left.", "She knocked two times more loudly than before."),
 ("iteration", "Run the migration 4 times more to clear the queue.", "The migration ran 4 times longer than the backup."),
 ("iteration", "The alarm rang five times more during the night.", "The alarm rang five times more often than last week."),
 ("iteration", "Press the button 2x more to reset it.", "The new button registers 2x more presses than the old one."),
 ("iteration", "He asked 10 times more, and got no answer.", "He asked 10 times more questions than she did."),
 ("iteration", "The job was restarted twice more on Friday.", "The job was twice more likely to fail on Friday than on Thursday."),
 ("iteration", "Try three times more, then call support.", "Support calls are three times more common than chat requests."),
 # group "attachment": the same quantities, the multiplier attached to the quantity in one sentence and to a comparative in the other
 ("attachment", "B logged twenty times as many errors as A.", "B logged twenty times more errors than A."),
 ("attachment", "The cache is one and a half times as large as the index.", "The cache is one and a half times larger than the index."),
 ("attachment", "Throughput is 2.5× the June rate.", "Throughput is 2.5× higher than the June rate."),
 ("attachment", "The queue holds a hundred times as many jobs as the buffer.", "The queue holds a hundred times more jobs than the buffer."),
 ("attachment", "Latency is 3 times as high as the baseline.", "Latency is 3 times higher than the baseline."),
 ("attachment", "The archive is a third the size of the source.", "The archive is 3 times smaller than the source."),
 ("attachment", "The new index is twelve times as fast as the old one.", "The new index is twelve-fold faster than the old one."),
 ("attachment", "The west wing uses half as much power as the east wing.", "The west wing uses two times less power than the east wing."),
]


def bank():
    rows = []
    for i, (group, leave, warn) in enumerate(PAIRS, 1):
        rows.append({"id": "O%02da" % i, "pair": i, "group": group, "text": leave, "expected_warning": False})
        rows.append({"id": "O%02db" % i, "pair": i, "group": group, "text": warn, "expected_warning": True})
    return rows


def compact(rows): return json.dumps(rows, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


# Excelsior's v1.0.0 scan(), ported from the page's own source; the port is checked against his 64 published cases before use.
N = r"(?:[0-9]+(?:\.[0-9]+)?|one|two|three|four|five|six|seven|eight|nine|ten)"
V1 = re.compile(r"\b(?:" + N + r"\s*(?:times|[x×]|-?fold)|[x×]\s*" + N + r"|twice|thrice)\s+(?:more|fewer|less|faster|slower|higher|lower|larger|smaller|greater|better|increase|decrease)\b", re.I)
def v1(t): return bool(V1.search(re.sub(r"```[\s\S]*?```|`[^`\n]*`|https?://\S+", lambda m: " " * len(m.group(0)), t)))
REGISTERED = ["(?i)times more", "(?i)times fewer", "(?i)times less"]          # the row's form_constraints.forbid, as served
def registered(t): return any(re.search(p, t) for p in REGISTERED)


if sys.argv[1:] == ["freeze"]:
    assert not os.path.exists(BANK), "the bank is frozen already"
    rows = bank(); assert len(rows) == 32 and len({r["text"] for r in rows}) == 32
    open(BANK, "wb").write(compact(rows)); print("frozen", len(rows), "sentences, sha256", hashlib.sha256(compact(rows)).hexdigest())
elif sys.argv[1:2] == ["run"] and len(sys.argv) == 3:
    raw = open(BANK, "rb").read(); rows = json.loads(raw); assert raw == compact(bank()), "the bank on disk is not the bank in this file"
    his = json.load(open(sys.argv[2], encoding="utf-8"))      # the checker's 64 published cases, saved from its page as a JSON list
    assert hashlib.sha256(compact(his)).hexdigest() == "5a7c4f97911a32f7476cff95d22a9736ac3d5450480da2380e54e216c042e091", "these are not the 64 cases the checker's page pins"
    got = collections.Counter((x["expected_warning"], v1(x["text"])) for x in his)
    assert (got[(True, True)], got[(False, True)], got[(True, False)], got[(False, False)]) == (24, 7, 8, 25), "the port does not reproduce the page's published counts"
    out = {"bank_sha256": hashlib.sha256(raw).hexdigest(), "rules": {}, "rows": []}
    for name, f in (("v1", v1), ("registered", registered)):
        r = {}
        for g in ("iteration", "attachment", "all"):
            sel = [x for x in rows if g == "all" or x["group"] == g]
            r[g] = {"claims_warned": sum(1 for x in sel if x["expected_warning"] and f(x["text"])), "claims": sum(1 for x in sel if x["expected_warning"]),
                    "controls_warned": sum(1 for x in sel if not x["expected_warning"] and f(x["text"])), "controls": sum(1 for x in sel if not x["expected_warning"])}
        r["pairs_told_apart"] = sum(1 for i in range(1, 17) if [f(x["text"]) for x in rows if x["pair"] == i] == [False, True])
        out["rules"][name] = r; print(name, json.dumps(r))
    for x in rows:
        out["rows"].append({**x, "v1": v1(x["text"]), "registered": registered(x["text"])})
        print(x["id"], "expect", "warn " if x["expected_warning"] else "leave", "| v1", "warn " if v1(x["text"]) else "leave", "| registered", "warn " if registered(x["text"]) else "leave", "|", x["text"])
    json.dump(out, open(os.path.join(D, "results_v1.json"), "w"), indent=1, ensure_ascii=False)
