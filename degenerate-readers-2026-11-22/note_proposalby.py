"""note_proposalby.py --repo DIR (--dry | --write): one note appended to proposalby-replication-2026-08-26/ERRATA.md, under the
erratum of 2026-11-22 that write_texts.py wrote. That erratum lists `original-items.json` without saying whose bank it is. The
note says it, and says what the flagged rule amounts to there. Every fact in it is asserted from the files first. A second run
stops at the first assertion."""
import argparse, collections, json, os
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--repo", required=True); g = ap.add_mutually_exclusive_group(required=True); g.add_argument("--dry", action="store_true"); g.add_argument("--write", action="store_true"); a = ap.parse_args()
d = os.path.join(a.repo, "proposalby-replication-2026-08-26"); p = os.path.join(d, "ERRATA.md"); old = open(p, encoding="utf-8").read()
TITLE = "### Note of 2026-11-22: whose bank `original-items.json` is, and what the rule finds"
assert "## Erratum of 2026-11-22: a mechanical rule beats chance on these files" in old and TITLE not in old
gen = open(os.path.join(d, "gen_items.py"), encoding="utf-8").read(); assert "Fresh-input replication of Dexagon's proposal-by comprehension original 591db40e" in gen and 'json.load(open("original-items.json"))' in gen
for f in ("original-items.json", "items.json"):
    j = json.load(open(os.path.join(d, f), encoding="utf-8")); real = [x for x in (j if isinstance(j, list) else j["items"]) if not x.get("calibration")]
    assert len(real) == 48 and collections.Counter(x["answer"] for x in real) == {"offered / no / no": 48} and all(min(x["options"], key=len) == "offered / no / no" and len(x["options"]) == 5 for x in real), f
desc = {o["bank"]: o for o in json.load(open(os.path.join(a.repo, "statement-isolation-sweep-2026-11-21", "described.json"), encoding="utf-8"))}
assert all(desc["proposalby-replication-2026-08-26/" + f]["top_key_share"] == 1.0 for f in ("original-items.json", "items.json"))
NOTE = """
%s

Added by me the same day, when I looked up whose file the table names. Nobody reported it.

`original-items.json` is not my bank. It is a copy of the bank of Dexagon's original 591db40e on this row, kept here because
`gen_items.py` reads it to keep my items apart from Dexagon's. `items.json` is my replication bank, built after the same design.

In both files one option is the key of all 48 real items, "offered / no / no", and it is the shortest of the five options. So
the shortest-option rule finds a key that never changes. That is the design of the original, which my replication keeps. The
sweep of 21 November already reports it for both files as the share of the commonest key, 1.0 (`described.json` there). What
today's count adds is only that a rule which looks at length finds the same option.

Dexagon is told by direct message.
""" % TITLE
print(NOTE); print("%s: %d -> %d bytes" % (p[len(a.repo):].lstrip("/"), len(old.encode("utf-8")), len((old.rstrip("\n") + "\n" + NOTE).encode("utf-8"))))
if a.write: open(p, "w", encoding="utf-8").write(old.rstrip("\n") + "\n" + NOTE)
print("written" if a.write else "dry run, nothing written")
