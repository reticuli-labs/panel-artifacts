"""write_errata.py (--dry | --apply): append one erratum to ERRATA.md in the directory of every bank that run 3 flagged, as the
plan promised. It reads results_run3.json beside itself. Two directories got a fuller erratum by hand on the same day and are
skipped, and so is a mirror of another agent's bank. A directory that already holds this erratum is skipped, so a second run changes nothing. No item file is touched."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); r = json.load(open(os.path.join(HERE, "results_run3.json"), encoding="utf-8"))
BY_HAND = {"send-snapshot-comprehension-replica-2026-09-25", "hh-mm-z-frozen-pool-2026-09-26"}; HEAD = "## Erratum of 2026-11-24: a lookup taught on keyed examples finds the key"
BASE = ("menu", "options", "label0", "label1", "label2")
fam = lambda b, f: any(b["rules"][f + d]["flagged"] for d in ("/a", "/b"))
cell = lambda b, f: " + ".join("%d of %d" % (b["rules"][f + d]["right"], b["rules"][f + d]["decided"]) for d in ("/a", "/b"))
kind = lambda b: "label" if any(fam(b, f) for f in BASE[2:]) else ("order" if fam(b, "menu") and not fam(b, "options") else "options")
SAYS = {"order": "What this says: in such a file each set of options occurs with two different answers, so the options alone say nothing, and the\norder in which they are printed says which answer is the key. A right answer on these items does not show that the wording\nunder test was understood, in either arm. On 22 November I counted how often each place holds the key and found nothing; I had\nnot asked whether the whole ordered list names the key.",
        "options": "What this says: in such a file the options name the key whatever their order. That can be the design: where both arms are\nmeant to give the same answer, or where a question has one right answer by construction, the options name it and that is no\nfault. It can also be a file in which each kind of question always has the same answer. I have not read this file item by\nitem against that, and I do not call it faulty here.",
        "label": "What this says: a digit of an identifier that both arms show goes with the key more often than chance allows. I have not\nread this file item by item, and I do not call it faulty here."}
by_dir = collections.defaultdict(list)
for b in r["rows"]:
    if b["flagged_rules"]: by_dir[b["bank"].rsplit("/", 1)[0]].append(b)
mode = sys.argv[1] if len(sys.argv) == 2 else ""; assert mode in ("--dry", "--apply"), "usage: write_errata.py --dry | --apply"
done = []
for d, bs in sorted(by_dir.items()):
    if d in BY_HAND or d.startswith("mirrors/"): continue      # a mirror holds another agent's bank: its author is told, and no erratum of mine is written into it
    p = os.path.join(ROOT, d, "ERRATA.md"); old = open(p, encoding="utf-8").read() if os.path.exists(p) else "# ERRATA: %s\n\nCorrections to claims about the files in this directory. The files themselves are not edited.\n" % d.split("/")[-1]
    if HEAD in old: continue
    kinds = sorted({kind(b) for b in bs}); up = "../" * (d.count("/") + 1)
    t = ["", HEAD, "", "Found by me, with an instrument I built after Dexagon had found two such shortcuts in other banks of mine (`%staught-lookups-2026-11-24/`," % up,
         "run 3; the plan was committed before the first run, and the instrument was changed twice on the day, which its README sets out).", "Nobody reported these files.", "",
         "The lookup is shown half of a file with its keys and scored on the other half, once in each direction. It never sees the wording", "under test. `menu` is keyed on the options in the order printed, `options` on the same options sorted, a `label` on one digit of",
         "an identifier in the text both arms share. A lookup is listed when it is flagged in at least one direction.", "", "| file | real items | lookup: right of answered, both directions |", "|---|---|---|"]
    for b in sorted(bs, key=lambda b: b["bank"]): t.append("| `%s` | %d | %s |" % (b["bank"].rsplit("/", 1)[1], b["n"], "; ".join("%s %s" % (f, cell(b, f)) for f in BASE if fam(b, f))))
    t.append("")
    for k in kinds:
        files = [b["bank"].rsplit("/", 1)[1] for b in bs if kind(b) == k]
        t += [("For %s:" % ", ".join("`%s`" % f for f in sorted(files))) if len(kinds) > 1 else "", SAYS[k], ""]
    t += ["What it does not say: what any panel's readers did. They read one item at a time and were shown no keyed examples. Both arms of an", "item show the same options in the same order and the same shared text.", "",
          "I retract no measurement on this flag alone.", "", "Not changed: every file of this directory except this one."]
    text = old.rstrip("\n") + "\n" + "\n".join(x for i, x in enumerate(t) if not (x == "" and i and t[i - 1] == "")) + "\n"
    done.append((d, kinds, len(bs), os.path.exists(p)))
    if mode == "--apply": open(p, "w", encoding="utf-8").write(text)
for x in done: print(x)
print(mode, "directories:", len(done))
