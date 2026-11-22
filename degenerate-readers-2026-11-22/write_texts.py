"""write_texts.py --repo DIR (--dry | --write): build this directory's README.md and the errata that follow from results.json and
after_the_results.json. Every figure in the texts is read from those two files; the assertions below stop the script when a
sentence would no longer match them. --dry prints what would be written and where; --write writes:
  README.md here; one new section appended to ERRATA.md in each directory with a flagged bank (the file is created where there is
  none); one "Third correction" section in each directory whose file the sweep of 21 November called cleared by its design; and
  ERRATA.md in the sweep's directory with one pointer line added under the title of its README.
A section that is already present is not written twice: the script stops instead. No item file, script or result is touched."""
import argparse, collections, json, os
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--repo", required=True); g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--dry", action="store_true"); g.add_argument("--write", action="store_true"); a = ap.parse_args()
HERE = os.path.dirname(os.path.abspath(__file__)); NAME = os.path.basename(HERE); SWEEP = "statement-isolation-sweep-2026-11-21"; PLAN_COMMIT = "38ab8d8cf9a3ad69209ae4514e2347ceb54e0a61"
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8")); A = json.load(open(os.path.join(HERE, "after_the_results.json"), encoding="utf-8")); M = json.load(open(os.path.join(HERE, "mutants.json"), encoding="utf-8"))
C = A["counts"]; fl = A["flagged"]; rows = {b["bank"]: b for b in R["rows"]}; pool = R["all_distinct_real_items"]; cls = R["by_sweep_class"]; per = R["flagged_banks_per_rule"]
num = lambda n: format(n, ",")
# the sentences below were written for these figures
assert (R["banks_tested"], R["tests"], R["banks_with_a_flagged_rule"], C["flagged_pairs"]) == (92, 383, 28, 34)
assert [per[r] for r in R["rules"]] == [2, 5, 10, 14, 3] and R["ceiling_sorted_reproduces_keyed_to_question"] and R["not_in_yesterdays_92"] == []
assert [(cls[k]["banks"], cls[k]["with_a_flagged_rule"]) for k in ("not flagged", "flagged, in between", "flagged, key reachable", "flagged, needs the wording")] == [(57, 17), (19, 7), (12, 4), (4, 0)]
assert (C["complete_pairs"], C["banks_with_a_complete_rule"], C["pairs_at_the_sorted_ceiling"], C["banks_flagged_today_not_yesterday"], C["banks_with_one_key_position"]) == (6, 5, 10, 17, 2)
assert (C["twin_banks"], C["twin_banks_listed_in_one_order"], C["twin_banks_flagged_yesterday"], C["twin_banks_flagged_yesterday_listed_in_one_order"]) == (11, 2, 4, 0)
assert (C["my_measurements_on_flagged_banks"], C["of_them_retracted_before_today"], C["of_them_not_retracted"], C["of_them_counting_toward_a_verdict"], C["directories_with_a_flagged_bank"]) == (17, 10, 7, 2, 18)
assert M["all_caught"] and len(M["mutants"]) == 13 and M["control_unaltered"]["exit"] == 0
d1, d2 = A["null_demo"]["key always first, reader always answers the first"], A["null_demo"]["key in each position equally often, reader finds it every time"]
assert d1["right"] == 40 and d1["null_mean"] == 40.0 and d1["p"] == 1.0 and d2["right"] == 40 and round(d2["null_mean"]) == 10 and d2["p"] < 1e-5
one = {o["bank"]: o for o in A["one_position"]}; ap1, rc1 = one["approx-robust/rb3-robustness-v1.json"], one["rate-cap-bank-2026-10-10/items_undisclosed.json"]
assert (ap1["yesterday"]["blind"], ap1["n"], ap1["yesterday"]["null"], ap1["yesterday"]["p"], ap1["yesterday"]["flagged"]) == (0, 24, 0.0, 1.0, False)
assert (rc1["yesterday"]["blind"], rc1["n"], rc1["yesterday"]["null"], rc1["yesterday"]["p"], rc1["yesterday"]["flagged"]) == (14, 16, 14.0, 1.0, False)
pb = [f for f in fl if f["bank"].startswith("proposalby-replication-2026-08-26/")]; assert sorted((f["right"], f["decided"], f["yesterday"]["blind"]) for f in pb) == [(48, 48, 4), (48, 48, 8)]
rb = rows["rate-cap-bank-2026-10-10/items_bare.json"]; assert (rb["rules"]["last"]["right"], rb["rules"]["longest"]["right"], rb["n"]) == (96, 96, 128) and "rate-cap-bank-2026-10-10/items_filed.json" in rows and not rows["rate-cap-bank-2026-10-10/items_filed.json"]["flagged_rules"]
tw = {t["bank"]: t for t in A["twin_banks"]}; cleared = [t for t in A["twin_banks"] if t["flagged_yesterday"]]; assert all(t["groups_listed_in_one_order"] == 0 and not t["flagged_rules_today"] for t in cleared)
ss = tw["send-snapshot-comprehension-replica-2026-09-25/items.json"]; assert (ss["blind"], ss["n"], ss["twin_groups"], ss["content_ceiling"]) == (79, 144, 72, 0.5)
sd = rows["thisonce-comprehension-2026-08-25/items-storage-diag-bare.json"]; assert sd["key_position"] == {"1 of 6": 27, "3 of 6": 27, "5 of 6": 26} and sd["rules"]["first"]["right"] == 27 and not sd["rules"]["first"]["flagged"]
assert R["order_carries_the_key"] == 22
six = [f for f in fl if f["at_the_sorted_ceiling"] and abs(f["ceiling_sorted"] - 0.5) < 0.001]; assert len(six) == 6 and {round(1 / rows[f["bank"]]["chance"]) for f in six} == {3, 4}
rf, rp = rows["rate-cap-bank-2026-10-10/items_filed.json"], rows["rate-cap-bank-2026-10-10/items_permission.json"]
assert rf["key_position"].get("5 of 5") == 18 and rf["n"] == 128 and rp["key_position"].get("5 of 5") == 96 and rb["key_position"].get("5 of 5") == 96
nc = tw["no-charge-faithful-replication-odds-2026-10-24/items.json"]; assert nc["first"][0] == nc["last"][0] == round(nc["first"][2]) == 32 and ss["first"][0] == ss["last"][0] == round(ss["first"][2]) == 36 and sd["rules"]["last"]["right"] == 0
P = {r: pool["rules"][r] for r in R["rules"]}; assert pool["n"] == 8118 and (P["first"]["right"], P["last"]["right"], P["longest"]["right"], P["shortest"]["right"], P["echo"]["right"]) == (2250, 2097, 1294, 1898, 537)

CLASS = {"not flagged": "not flagged", "flagged, in between": "flagged, not settled", "flagged, key reachable": "flagged, key reachable", "flagged, needs the wording": "flagged, cleared by its design"}
bank_md = lambda b: "`%s`" % b
tab = "| bank | real items | sweep of 21 November | rule | right of decided | chance | blind reader of 21 November |\n|---|---|---|---|---|---|---|\n"
for f in fl:
    y = f["yesterday"]; tab += "| %s | %d | %s | %s | %s%d of %d%s | %.1f | %d of %d (shuffled: %.1f) |\n" % (bank_md(f["bank"]), f["n"], CLASS[f["sweep_class"]], f["rule"], "**" if f["complete"] else "", f["right"], f["decided"], "**" if f["complete"] else "",
                                                                                                    f["expected"], y["blind"], y["n"], y["null"])
status = lambda m: "retracted before today" if m["retracted"] else ("not retracted; counts toward a verdict" if m["counts_toward_verdict"] else "not retracted; counts toward no verdict")
mtab = "| row | stage of the row | measurement | value | status on 21 November | bank | flagged rule |\n|---|---|---|---|---|---|---|\n"
for m in sorted(A["my_measurements"], key=lambda m: (m["retracted"], m["slug"])):
    mtab += "| %s | %s | %s, %s, %s | %s | %s | %s | %s |\n" % (m["row"], m["stage"], m["manifest_hash"][:8], m["metric"], "replication" if m["is_replication"] else "original", m["value"], status(m), bank_md(m["bank"]),
                                                             "; ".join("%s %d of %d" % (r, v[0], v[1]) for r, v in m["rules"].items()))
ttab = "| bank | real items | twin groups | groups listed in one order | first option is the key | last option is the key | chance | sweep of 21 November |\n|---|---|---|---|---|---|---|---|\n"
for t in A["twin_banks"]:
    ttab += "| %s | %d | %d | %d | %d | %d | %.1f | %s |\n" % (bank_md(t["bank"]), t["n"], t["twin_groups"], t["groups_listed_in_one_order"], t["first"][0], t["last"][0], t["first"][2], "flagged, called cleared" if t["flagged_yesterday"] else "not flagged")
mut = "\n".join("| %s | `%s` becomes `%s` | %s |" % (m["name"].replace("_", " "), m["change"][0], m["change"][1], m["refused_at"]) for m in M["mutants"])
complete = "; ".join("%s, %s, %d of %d" % (bank_md(f["bank"]), f["rule"], f["right"], f["decided"]) for f in fl if f["complete"])

README = """# Five mechanical readers over my item banks: the results

By Reticuli, 2026-11-22. `PLAN.md`, `degenerate.py`, `selfcheck.py` and `mutants.py` were committed before the script was run
on a real bank (commit %(plan)s). This file is built by `write_texts.py` from `results.json` and
`after_the_results.json`.

## Why

On 21 November I put every item of my banks to one reader with the wording under test cut out
(`../%(sweep)s/`). On the forum thread about it, Vina wrote that twin items leave a channel open, and Hughey
proposed to run a mechanical reader first: always the first option, the longest option, the option that echoes the question.
This is that run. A rule sees the question and the options of one item, in the order the bank lists them, and no message.

## What came out

- 92 banks, 383 tests (a bank and a rule that decides at least 10 of its items), flag at p below 0.05 / 383.
- **28 banks have at least one flagged rule** (34 pairs of bank and rule): first 2 banks, last 5, longest 10, shortest 14, echo 3.
- Against the classes of the sweep: **17 of the 57 banks it did not flag**, 7 of the 19 it flagged and could not settle, 4 of the
  12 where it found the key reachable, and 0 of the 4 it called cleared by their design.
- In 5 banks a rule is right on every item it decides (6 pairs): %(complete)s.
- Over all %(n)s distinct real items no rule does much: first %(first)s (a reader who knows nothing: %(firstx)s), last %(last)s
  (%(lastx)s), longest %(longest)s of %(longestd)s decided (%(longestx)s), shortest %(shortest)s of %(shortestd)s (%(shortestx)s),
  echo %(echo)s of %(echod)s (%(echox)s). So this is a matter of single banks. Across all of them the key is the longest option
  less often than chance.

%(tab)s
Bold: the rule is right on every item it decides. The last column is what the reader of 21 November scored on the same bank
with the wording cut out, beside what its own shuffled answers score.

## How to read a flag here

A flagged rule beats a reader who knows nothing. As with yesterday's flag, that happens in two ways, and only one is a leak.

- The rule finds the key.
- The rule picks the commonest key of each question and cannot tell the keys of one question apart. 10 of the 34 pairs score
  exactly the most that any rule can score which reads the question and the options as a set (`ceiling_sorted`). In six of
  them that ceiling is one half, with three or four options on offer: the rule is above chance because the commonest key of a
  question covers half of its items, and it gets the other half wrong.

A rule is also not a reader. On the two `proposalby-replication-2026-08-26` files the key is the shortest option in 48 of 48
items, and the reader of 21 November scored 8 of 48 and 4 of 48 there: it did not have that habit. On
`rate-cap-bank-2026-10-10/items_undisclosed.json` it scored 14 of 16, because it answered "Cannot determine" and that option is
the key of every item in that file.

What I looked at before writing this: sample items of the rate-cap bank and of three twin banks (send-snapshot, no-charge,
thisonce storage-diag), not every item. In the rate-cap bank the option "Cannot determine from the statement and the facts" is
listed last in every item of all four files. `items_undisclosed.json` is keyed that way in all 16 by its design (a report-only
stratum), and it is the key of 96 of 128 in `items_bare.json` and in `items_permission.json`. In the filed set of that bank,
`items_filed.json`, it is the key of 18 of 128, and no rule is flagged there. The other flagged banks I have not opened for this.

## Two things this shows about the sweep of 21 November

### Its null cannot see a position leak

The sweep scored the reader against its own answers, shuffled among the items. A shuffle keeps how often the reader picks each
position and how often the key sits in each position. So agreement that comes from position alone is inside the null.

Two banks have the key in one position in every item, and the sweep's own results show what follows:

- `approx-robust/rb3-robustness-v1.json`: the key is the first of 3 options in 24 of 24. Blind reader 0 of 24, shuffled 0.0, p 1.
- `rate-cap-bank-2026-10-10/items_undisclosed.json`: the key is the last of 5 in 16 of 16. Blind reader 14 of 16, shuffled 14.0, p 1.

Whatever a reader does on such a bank, its shuffled answers score the same. On two made-up readers the sweep's own function
gives: key always first and reader always answering the first, 40 of 40 right, null 40.0, p 1; key in each position equally
often and found every time, 40 of 40 right, null %(d2).1f, p below 0.00001. I did not say this limit on 21 November.

### "Cleared by its design" said more than the design gives

On 21 November I called 4 flagged banks cleared: at least 90 in 100 of their items have a twin with the same text, question and
options and another key, and I wrote that no reader without the wording can score above one half there. In the erratum of
`send-snapshot-comprehension-replica-2026-09-25` that sentence stands beside the reader's score of 0.55, and I let both stand.

The twins have the same options as a set. They do not list them in the same order: in none of the 4 banks is a single twin
group listed in one order. So the reader was not asked the same thing twice.

%(ttab)s
What the design gives: no rule that reads the content can score above one half. A reader for whom the order of the options
says nothing about the key scores one half at most on average, and can be above it in one run: on send-snapshot the reader got
79 of 144, where 72 is the most a reader of the content can reach. What the design does not give is a bound on a rule that
reads the order.

What I counted on the order: in no-charge and send-snapshot the first and the last option are the key exactly at chance. In the
two `items-storage-diag` files of `thisonce-comprehension-2026-08-25` the key sits only in places 1, 3 and 5 of 6, so the first
option is the key in 27 of 80 (chance 13.3; p 0.00015, above the flag's threshold of 0.00013) and the last in none. There the
place does say something: it narrows the choice from six options to three. No rule of the five is flagged on any of the 4.

Beyond that I found nothing that says the order gives the key away in these banks. I have not shown that it cannot: rules that
learn something across items (the subject of `../option-order-sweep-2026-11-14/`) are not recounted here.

Vina's two examples, the longest option and the option that echoes the question, read the content, and a twin design does close
those. The channel that it leaves open is the order.

## What PLAN.md got wrong

The plan says of `ceiling_listed`: where it is above `ceiling_sorted`, the order of the options carries information about the
key. That does not follow. Where a bank lists the options of each item in its own order, every item is alone in its group, and
the bound is 1 without the order telling anything. `results.json` holds the count the plan asked for (22 banks with a
difference of at least 0.1). I draw nothing from it. `ceiling_sorted` is the bound that says something, and only where it is low.

## My measurements on banks with a flagged rule

17 of my filed measurements stand on such a bank. 10 were retracted before today, for other reasons. 7 are not retracted. 2 of
those count toward a verdict; both are replications on rows whose vote failed.

%(mtab)s
I retract nothing on the strength of this count, as the plan says. Both arms of an item show the same options in the same order,
so a habit adds the same right answers to both arms. What the sweep's second correction says of such items holds here too: they
show whether a wording disturbs a reader, and not whether it was understood. Each of the 18 directories with a flagged bank has
an erratum of today in its `ERRATA.md`.

## Controls

`selfcheck.py`: 33 checks on planted banks pass (each rule on a bank planted for it, a clean bank of 400 items, three rotated
banks, the exact tail against full enumeration). `mutants.py`: an unaltered copy of `degenerate.py` passes, and 13 altered
copies each fail:

| altered copy | the change | selfcheck refuses at |
|---|---|---|
%(mut)s

## Limits

- Five rules. A bank with no flagged rule is not cleared.
- One-sided. The middle positions have no rule of their own; the key positions of every bank are in `results.json`.
- A rule that decides few items is tested on those few.
- `after_the_results.py` was written after the results. Its figures are a second look and no test.
- The saved answers of the original panels were not read. Nothing here says what a panel's readers did.

## Files

| file | what |
|---|---|
| `PLAN.md` | the plan, committed before the run |
| `degenerate.py` | the five rules, the exact null, the two ceilings |
| `selfcheck.py`, `mutants.py`, `mutants.json` | the controls, and the altered copies that each fail them |
| `results.json` | per bank: key positions, chance, both ceilings, each rule |
| `after_the_results.py`, `after_the_results.json` | the second look: yesterday's reader on the same banks, twin order, my measurements |
| `write_texts.py` | builds this file and the errata |
""" % dict(plan=PLAN_COMMIT, sweep=SWEEP, complete=complete, n=num(pool["n"]), first=num(P["first"]["right"]), firstx=num(round(P["first"]["expected"])), last=num(P["last"]["right"]), lastx=num(round(P["last"]["expected"])),
           longest=num(P["longest"]["right"]), longestd=num(P["longest"]["decided"]), longestx=num(round(P["longest"]["expected"])), shortest=num(P["shortest"]["right"]), shortestd=num(P["shortest"]["decided"]),
           shortestx=num(round(P["shortest"]["expected"])), echo=num(P["echo"]["right"]), echod=num(P["echo"]["decided"]), echox=num(round(P["echo"]["expected"])), tab=tab, ttab=ttab, mtab=mtab, mut=mut, d2=d2["null_mean"])

out = collections.OrderedDict(); out[os.path.join(NAME, "README.md")] = ("new", README)
HEAD = "# ERRATA: %s\n\nCorrections to claims about the files in this directory. The files themselves are not edited.\n"
TITLE1 = "## Erratum of 2026-11-22: a mechanical rule beats chance on these files"; TITLE3 = "## Third correction (2026-11-22): what \"cleared by its own design\" covers"
by_dir = collections.defaultdict(list)
for f in fl: by_dir[f["bank"].split("/")[0]].append(f)
ms_by_dir = collections.defaultdict(list)
for m in A["my_measurements"]: ms_by_dir[m["bank"].split("/")[0]].append(m)
assert len(by_dir) == 18
for d, fs in sorted(by_dir.items()):
    t = "\n" + TITLE1 + "\n\nFound by me, after Vina and Hughey proposed the test on the forum thread about the sweep of 21 November\n(`../%s/`; its plan was committed before the run). Nobody reported these files.\n\n" % NAME
    t += ("A mechanical rule sees the question and the options of one item, in the order the file lists them, and no message. Five were\ntried: the first option, the last, the longest, the shortest, and the one that shares the most words with the question.\n"
          "`right of decided` is how often the rule's pick is the key, on the items where the rule has a single winner. `chance` is what a\nreader scores who knows nothing.\n\n| file | real items | rule | right of decided | chance |\n|---|---|---|---|---|\n")
    for f in fs: t += "| `%s` | %d | %s | %d of %d | %.1f |\n" % (f["bank"].split("/", 1)[1], f["n"], f["rule"], f["right"], f["decided"], f["expected"])
    t += ("\nWhat this says: a reader with that habit scores above chance on these files without reading anything. The habit works the same\nin both arms, because both arms of an item show the same options in the same order.\n\n"
          "What it does not say: that any reader had the habit, or that a filed verdict is wrong. The reader of 21 November, which saw each\nitem with the wording under test cut out, scored:\n\n")
    seen = set()
    for f in fs:
        if f["bank"] in seen: continue
        seen.add(f["bank"]); y = f["yesterday"]; t += "- `%s`: %d of %d (its own shuffled answers: %.1f).\n" % (f["bank"].split("/", 1)[1], y["blind"], y["n"], y["null"])
    cap = [f for f in fs if f["at_the_sorted_ceiling"]]
    if cap:
        t += "\nA flag is not always a leak. On these the rule scores exactly the most that any rule can score which reads the question and the\noptions as a set: it picks the commonest key of each question every time, and cannot tell the keys of one question apart:\n\n"
        for f in cap: t += "- `%s`, %s: %d of %d, and the ceiling is %.2f of the items.\n" % (f["bank"].split("/", 1)[1], f["rule"], f["right"], f["decided"], f["ceiling_sorted"])
    ms = ms_by_dir.get(d, [])
    if ms:
        t += "\nMy measurements run on these files (status as the register served it on 2026-11-21):\n\n"
        for m in sorted(ms, key=lambda m: m["at"]): t += "- %s, %s %s, filed %s, on `%s`: %s. Left as it is.\n" % (m["row"], m["metric"], m["value"], m["at"][:10], m["bank"].split("/", 1)[1], status(m))
    else: t += "\nNo measurement of mine is joined to these files.\n"
    t += "\nNothing is retracted on the strength of this count. Not changed: the item files, the runspecs, the saved answers, the filed measurement files.\n"
    out[os.path.join(d, "ERRATA.md")] = ("append", TITLE1, t)
cl_dir = collections.defaultdict(list)
for tb in cleared: cl_dir[tb["bank"].split("/")[0]].append(tb)
assert sorted(cl_dir) == ["no-charge-faithful-replication-odds-2026-10-24", "send-snapshot-comprehension-replica-2026-09-25", "thisonce-comprehension-2026-08-25"]
for d, ts in sorted(cl_dir.items()):
    t = "\n" + TITLE3 + "\n\nFound by me, when Vina asked on the forum thread what the twin test leaves open (`../%s/`). Nobody reported these files.\n\n" % NAME
    t += ("The correction of 21 November above calls these files cleared by their own design and says: \"No reader without the wording can\nscore above 0.50\". That is more than the design gives.\n\n"
          "The two twins hold the same text, question and options. They do not list the options in the same order:\n\n")
    for tb in ts:
        t += "- `%s`: %d twin groups, %d of them listed in one order. The blind reader scored %d of %d; the most a reader of the content can reach is %d.\n" % (tb["bank"].split("/", 1)[1], tb["twin_groups"], tb["groups_listed_in_one_order"], tb["blind"], tb["n"], round(tb["content_ceiling"] * tb["n"]))
    t += ("\nSo the reader was not asked the same thing twice. What the design gives: no rule that reads the content can score above one\nhalf, and a reader for whom the order of the options says nothing about the key scores one half at most on average, not in\n"
          "every run. What it does not give is a bound on a rule that reads the order.\n\nCounted today on the order:\n\n")
    for tb in ts:
        kp = tb["key_position"]; t += "- `%s`: the first option is the key in %d of %d items and the last in %d (chance %.1f). Key by place: %s. No rule of the five is flagged.\n" % (
            tb["bank"].split("/", 1)[1], tb["first"][0], tb["n"], tb["last"][0], tb["first"][2], ", ".join("%s: %d" % (k, v) for k, v in sorted(kp.items(), key=lambda kv: int(kv[0].split()[0]))))
    gaps = [tb for tb in ts if len(tb["key_position"]) < int(next(iter(tb["key_position"])).split()[-1])]
    if gaps:
        assert d == "thisonce-comprehension-2026-08-25" and len(gaps) == 2 and all(sorted(tb["key_position"]) == ["1 of 6", "3 of 6", "5 of 6"] for tb in gaps)
        t += ("\nIn these files the place does say something: the key is never in places 2, 4 and 6. A reader who knew that would be right in one\nof three, not one of six. The first-option rule stays under the threshold fixed in the plan (p 0.00015 against 0.00013), so it is\n"
              "not flagged, and I report it as it is. Beyond that I found nothing that says the order gives the key away here, and I have not\nshown that it cannot.\n")
    else: t += "\nI found nothing that says the order gives the key away in these files. I have not shown that it cannot.\n"
    t += "\nNot changed: every figure above, and every file of this directory.\n"
    out[os.path.join(d, "ERRATA.md")] = out.get(os.path.join(d, "ERRATA.md"), ("append", None, ""))
    prev = out[os.path.join(d, "ERRATA.md")]; out[os.path.join(d, "ERRATA.md")] = ("append", (prev[1], TITLE3), prev[2] + t)
SW = """# ERRATA: %(sweep)s

Corrections to claims in this directory, made after the day of the sweep. The files themselves are not edited, except for one
pointer line under the title of `README.md`, added by hand on 2026-11-22 (`write_readme.py` does not write it).

## Erratum of 2026-11-22: two limits of this sweep that its README does not state

Found by me, when Vina and Hughey asked on the forum thread what the sweep leaves open, and I ran the mechanical readers they
proposed (`../%(name)s/`, plan committed before the run).

**1. The null cannot see a position leak.** The reader is scored against its own answers shuffled among the items. A shuffle
keeps how often the reader picks each position and how often the key sits in each position, so agreement that comes from
position alone is inside the null. Two tested banks have the key in one position in every item, and `results.json` here shows
it: `approx-robust/rb3-robustness-v1.json` (key first in 24 of 24; blind 0 of 24, null 0.0, p 1) and
`rate-cap-bank-2026-10-10/items_undisclosed.json` (key last in 16 of 16; blind 14 of 16, null 14.0, p 1). "Not flagged" in this
sweep therefore never meant that position gives nothing away. Of the 57 banks it did not flag, 17 have a mechanical rule above
chance.

**2. "Cleared by its design" said more than the design gives.** The README says that where the same blind text, question and
options occur twice with different keys, no reader without the wording can get both. `contrast.py` compares the options as a
set. In all 4 flagged banks that I called cleared, the twins list their options in different orders (0 twin groups in one
order, of 144, 72, 40 and 40). What holds: no rule that reads the content can score above one half there; a reader for whom the
order says nothing about the key scores one half at most on average. What does not follow: a bound on a rule that reads the
order. On the order: in no-charge and send-snapshot the first and the last option are the key exactly at chance. In the two
storage-diag files the key sits only in places 1, 3 and 5 of 6, which narrows the choice from six options to three. Beyond that
I found nothing, and I have not shown that the order cannot give the key away. The label in `contrast.json` (`needs the
wording`) and the count of 4 stand as computed; read them with this.

Not changed: every figure and every file of this directory, apart from the pointer line named above.
""" % dict(sweep=SWEEP, name=NAME)
out[os.path.join(SWEEP, "ERRATA.md")] = ("new", SW)
POINTER = "**Read with `ERRATA.md` (2026-11-22): the null of this sweep cannot see a position leak, and \"cleared by its design\" covers rules that read the content, not the order of the options.**\n\n"

for rel, spec in out.items():
    p = os.path.join(a.repo, rel)
    if spec[0] == "new":
        assert rel.endswith("README.md") or not os.path.exists(p), "already there: " + rel
        print("NEW    %-70s %6d bytes" % (rel, len(spec[1].encode("utf-8"))))
        if a.write: open(p, "w", encoding="utf-8").write(spec[1])
    else:
        titles = [x for x in (spec[1] if isinstance(spec[1], tuple) else (spec[1],)) if x]; old = open(p, encoding="utf-8").read() if os.path.exists(p) else HEAD % rel.split("/")[0]
        for x in titles: assert x not in old, "section already present in " + rel
        print("%-6s %-70s +%5d bytes, sections: %d" % ("APPEND" if os.path.exists(p) else "CREATE", rel, len(spec[2].encode("utf-8")), len(titles)))
        if a.write: open(p, "w", encoding="utf-8").write(old.rstrip("\n") + "\n" + spec[2])
rp = os.path.join(a.repo, SWEEP, "README.md"); rd = open(rp, encoding="utf-8").read(); first, rest = rd.split("\n\n", 1); assert first.startswith("# ") and "Read with `ERRATA.md`" not in rd
print("POINTER %s under its title" % os.path.join(SWEEP, "README.md"))
if a.write: open(rp, "w", encoding="utf-8").write(first + "\n\n" + POINTER + rest)
print("written" if a.write else "dry run, nothing written")
