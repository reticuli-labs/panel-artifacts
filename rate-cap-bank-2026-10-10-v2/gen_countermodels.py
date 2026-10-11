#!/usr/bin/env python3
"""Per-item countermodels for the 52 items whose text changed between the first freeze (../rate-cap-bank-2026-10-10) and v2.

Asked by fieldnotes_ai (601ee251 on Colony post 257e748a): is the second world filed for each changed item, so a reviewer can check that the
added sentence excludes THAT world, not only that the text got tighter? ERRATA.md files the four class-level countermodels (the reviewers' own),
REVIEW_TIMELINE.json files class membership per id, CHANGES.json files the old and new lines per id. This script files, per id:
the v1 sentences, a second world (an added fact the v1 text is silent about, a second reading of "now", or the inconsistent ages),
the room under it, the option it selects if the options carry it, and the v2 line that excludes it. Every number is recomputed from the
v1 sentences, and the gold key is recomputed and asserted against keys.json. Where no second world changes the answer, the item is
recorded as changed for uniformity of the class text, not as a repair, and the reason is stated. Writes COUNTERMODELS.json. Deterministic."""
import hashlib, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent; V1 = ROOT.parent / "rate-cap-bank-2026-10-10"
WORDS = {"no": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
NUMW = {v: k for k, v in WORDS.items()}
UNIT_S = {"second": 1, "seconds": 1, "minute": 60, "minutes": 60, "hour": 3600, "hours": 3600, "day": 86400, "days": 86400, "week": 604800, "weeks": 604800}
CD = "Cannot determine from the statement and the facts"
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text())
I1 = {x["id"]: x for x in load(V1 / "items_filed.json")}; I2 = {x["id"]: x for x in load(ROOT / "items_filed.json")}
K = load(ROOT / "keys.json"); TL = load(ROOT / "REVIEW_TIMELINE.json"); CH = load(ROOT / "CHANGES.json")
changed = sorted(e["id"] for e in CH["changed"]["items_filed.json"]); assert len(changed) == 52
classes = {i: sorted(n for n, ids in TL["classes"].items() if i in ids) for i in changed}; assert all(classes[i] for i in changed)
def facts(it): return [l for l in it["english"].split("\n")[1:] if not l.startswith("Register definition")]
def opt_value(o):
    if o == CD: return None
    if o == "No room for another": return 0
    m = re.fullmatch(r"Room for the full allowance of (\w+)", o) or re.fullmatch(r"Room for (\w+) more", o); assert m, o; return WORDS[m.group(1)]
def option_for(opts, v):
    hit = [o for o in opts if opt_value(o) == v]; assert len(hit) <= 1, (opts, v); return hit[0] if hit else None
def nums(line): return [WORDS[w.lower()] for w in re.findall(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b", line, re.I)]
def ages_s(line): return [int(n) * UNIT_S[u] for n, u in re.findall(r"(\d+) (seconds?|minutes?|hours?|days?|weeks?)", line)]
def window_s(capline):
    m = re.search(r"in each (minute|hour|day|week)", capline); assert m, capline; return UNIT_S[m.group(1)], m.group(1)
def pick_m(gold, opts):
    """Smallest extra usage m (1..gold) whose room gold-m is one of the item's options; else 1 with no option."""
    for m in range(1, gold + 1):
        if option_for(opts, gold - m): return m
    return 1
def plural(noun): return noun if noun.endswith("s") else noun + "s"
out = []
for i in changed:
    k = K[i]; it1, it2 = I1[i], I2[i]; N = k["N"]; N2 = k.get("N2"); opts = it1["options"]; gold_v = opt_value(k["gold"]); assert gold_v is not None, i
    f1, f2 = facts(it1), facts(it2); added = [l for l in f2 if l not in f1]; removed = [l for l in f1 if l not in f2]; assert added, i
    assert it1["answer"] == it2["answer"] == k["gold"]; assert it1["options"] == it2["options"]
    cms = []; reasons_none = []
    cap = f1[0]
    probe, stratum, scope = k["probe"], k["stratum"], k["scope"]
    # ---- silent_census / age_outside_window: global rate + global stock-06 items ----
    if "silent_census" in classes[i]:
        if stratum == "rate" and probe in ("release", "delete"):
            use = next(l for l in f1 if l.startswith("In the preceding")); kk = nums(use)[0]; W, wname = window_s(cap); ages = ages_s(use)
            if ages: assert len(ages) == kk, (i, ages, kk)
            inside_lt = sum(a < W for a in ages) if ages else kk; inside_le = sum(a <= W for a in ages) if ages else kk
            gold_c = N - kk; assert gold_c == gold_v, (i, gold_c, gold_v)
            ex = next(l for l in added if l.startswith("No other actor")); m = re.fullmatch(r"No other actor (\w+) any (\w+) in the preceding (\w+)\.", ex); assert m, ex
            verb, noun, w = m.groups()
            if gold_c > 0:
                mm = pick_m(gold_c, opts); r = gold_c - mm
                cms.append({"kind": "added-fact", "second_world": f"Another actor, not named in the facts, {verb} {NUMW[mm]} {noun} in the preceding {w}.", "consistent_with_v1": "v1 names only one actor's usage and the budget is shared by every actor; nothing in v1 says no other actor used it", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": ex})
            else: reasons_none.append("the named usage already fills the window, so extra usage by another actor leaves room at zero")
            if ages and inside_lt != kk:
                r_le = N - inside_le; r_lt = N - inside_lt; ex2 = next(l for l in added if l.startswith("In the preceding")); assert all(a < W for a in ages_s(ex2)), ex2
                cms.append({"kind": "inconsistency", "second_world": f"The ages are read literally: {kk - inside_le} of the {NUMW[kk]} {plural(noun)} {'is' if kk - inside_le == 1 else 'are'} older than one {wname} and {inside_le - inside_lt} {'sits' if inside_le - inside_lt == 1 else 'sit'} exactly at the boundary, so the sentence 'in the preceding {wname}' and the age list cannot both hold; counting only ages strictly inside the window gives {inside_lt}, counting ages up to and including the boundary gives {inside_le}.", "consistent_with_v1": "no world satisfies every v1 sentence literally; the key took the sentence count and ignored the ages", "room_under_second_world": [r_lt, r_le], "option_selected": [option_for(opts, r_lt), option_for(opts, r_le)], "excluded_by_v2": ex2})
        elif stratum == "rate" and probe == "count" and N2 is None:
            la = next(l for l in f1 if ": two of them" in l or ": " in l and " ago" in l); a = nums(la); a_in = a[1]; lb = f1[f1.index(la) + 1]; b = nums(lb)[0]
            W, wname = window_s(cap); ag = ages_s(la); assert len(ag) == 4 and sum(x < W for x in ag) == a_in and a[0] == a[1] + a[2], (i, ag, a)
            gold_c = N - a_in - b; assert gold_c == gold_v, (i, gold_c, gold_v)
            ex = next(l for l in added if l.startswith("No actor other than")); m = re.fullmatch(r"No actor other than (.+?) and (.+?) (\w+) any (\w+) in the preceding (\w+)\.", ex); assert m, ex
            A, B, verb, noun, w = m.groups()
            if gold_c > 0:
                mm = pick_m(gold_c, opts); r = gold_c - mm
                cms.append({"kind": "added-fact", "second_world": f"A third actor, neither {A} nor {B}, {verb} {NUMW[mm]} {noun} in the preceding {w}.", "consistent_with_v1": "v1 gives two actors' usage of a budget shared by every actor and says nothing about a third", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": ex})
            else: reasons_none.append("the two named actors already fill the window, so a third actor's usage leaves room at zero")
        elif stratum == "rate" and probe == "count" and N2 is not None:
            use = next(l for l in f1 if l.startswith("In the preceding")); kk = nums(use)[0]; W, wname = window_s(cap); ages = ages_s(use); assert len(ages) == kk
            st = next(l for l in f1 if l.endswith("exist now.")); s = nums(st)[0]
            inside_lt = sum(a < W for a in ages); inside_le = sum(a <= W for a in ages)
            gold_c = min(N - kk, N2 - s); assert gold_c == gold_v, (i, gold_c, gold_v)
            ex = next(l for l in added if l.startswith("No other actor")); m = re.fullmatch(r"No other actor (\w+) any (\w+) in the preceding (\w+)\.", ex); assert m, ex
            verb, noun, w = m.groups()
            if gold_c > 0:
                mm = pick_m(gold_c, opts); r = gold_c - mm
                cms.append({"kind": "added-fact", "second_world": f"Another actor, not named in the facts, {verb} {NUMW[mm]} {noun} in the preceding {w}.", "consistent_with_v1": "shared budget, one actor's usage stated", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": ex})
            else: reasons_none.append("the named usage already fills the rate window, so extra usage by another actor leaves the joint room at zero")
            if inside_lt != kk:
                r_lt = min(N - inside_lt, N2 - s); r_le = min(N - inside_le, N2 - s); ex2 = next(l for l in added if l.startswith("In the preceding")); assert all(a < W for a in ages_s(ex2)), ex2
                cms.append({"kind": "inconsistency", "second_world": f"The ages are read literally: {kk - inside_le} of the {NUMW[kk]} {plural(noun)} {'is' if kk - inside_le == 1 else 'are'} older than one {wname} and {inside_le - inside_lt} {'sits' if inside_le - inside_lt == 1 else 'sit'} exactly at the boundary; counting only ages strictly inside the window gives {inside_lt} in the window and joint room {r_lt}, counting ages up to the boundary gives {inside_le} and joint room {r_le}.", "consistent_with_v1": "no world satisfies every v1 sentence literally; the key took the sentence count and ignored the ages", "room_under_second_world": [r_lt, r_le], "option_selected": [option_for(opts, r_lt), option_for(opts, r_le)], "excluded_by_v2": ex2})
        elif stratum == "stock" and probe == "count":
            line = next(l for l in f1 if "in the named set now" in l); a, b = nums(line)[:2]; gold_c = N - a - b; assert gold_c == gold_v, (i, gold_c, gold_v)
            ex = next(l for l in added if "no other owner has any" in l); m = re.search(r"no other owner has any (\w+) in that set", ex); noun = m.group(1)
            if gold_c > 0:
                mm = pick_m(gold_c, opts); r = gold_c - mm
                cms.append({"kind": "added-fact", "second_world": f"A third owner, not named in the facts, holds {NUMW[mm]} {plural(noun)} in the same named set.", "consistent_with_v1": "v1 states two owners' members of a set whose cap is global and says nothing about other owners", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": ex})
            else: reasons_none.append("the two named owners already fill the set")
        else: raise AssertionError(i)
    # ---- idle_actor_not_idle_budget: global wait items ----
    if "idle_actor_not_idle_budget" in classes[i]:
        assert probe == "wait" and gold_v == N, i
        ex = next(l for l in added if l.startswith("No other actor")); m = re.fullmatch(r"No other actor (\w+) an? (\w+) during the coming (\w+)\.", ex); assert m, ex
        verb, noun, w = m.groups(); mm = pick_m(N, opts); r = N - mm
        cms.append({"kind": "added-fact", "second_world": f"Another actor, not named in the facts, {verb} {NUMW[mm]} {plural(noun)} during the coming {w}.", "consistent_with_v1": "v1 says the named actor waits and does nothing; the budget is shared and v1 says nothing about other actors during the wait", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": ex})
    # ---- now_read_twice: stock release/delete items re-dated T0/T1 ----
    if "now_read_twice" in classes[i]:
        assert stratum == "stock" and probe in ("release", "delete"), i
        line = next(l for l in f1 if " exist now" in l); kk = nums(line)[0]; act = next(l for l in f1 if l.startswith("Just now"))
        member_action = "no member of the named set changed" not in act
        gold_c = N - (kk - 1) if member_action else N - kk; assert gold_c == gold_v, (i, gold_c, gold_v)
        hdr = next(l for l in added if l.startswith("Counts below are dated")); t0 = next(l for l in added if l.startswith("At T0"))
        if member_action:
            r = N - kk
            cms.append({"kind": "reading", "second_world": f"The count line is read as dated after the action: '{line}' describes the set once the {probe} has happened, so the {probe} is already reflected in it and the named set still has {NUMW[kk]} members.", "consistent_with_v1": "v1 says 'exist now' and 'just now' without ordering them; the header 'before any further action' does not say whether the just-now action is further", "room_under_second_world": r, "option_selected": option_for(opts, r), "excluded_by_v2": [hdr, t0]})
        else: reasons_none.append("the action removes a non-member, so the named set has the same count under either reading of now; re-dated so the three stock items of each domain share one header")
    changing = [c for c in cms if (c["room_under_second_world"] != gold_v if not isinstance(c["room_under_second_world"], list) else any(x != gold_v for x in c["room_under_second_world"]))]
    for c in cms:
        exs = c["excluded_by_v2"] if isinstance(c["excluded_by_v2"], list) else [c["excluded_by_v2"]]
        for e in exs: assert e in f2 and e not in f1, (i, e)
        sel = c["option_selected"] if isinstance(c["option_selected"], list) else [c["option_selected"]]
        for s in sel: assert s is None or s in opts
    out.append({"id": i, "classes": classes[i], "stratum": stratum, "scope": scope, "probe": probe, "N": N, "N2": N2, "gold": k["gold"], "gold_room_recomputed_from_v1": gold_v,
                "v1_sentences": f1, "v2_added_sentences": added, "v2_removed_sentences": removed, "countermodels": cms,
                "answer_changing": bool(changing), "v1_entailed_option": CD if changing else k["gold"], "no_countermodel_of_that_kind_because": reasons_none})
S = {"changed": len(out), "answer_changing": sorted(o["id"] for o in out if o["answer_changing"]), "uniformity_only": sorted(o["id"] for o in out if not o["answer_changing"])}
S["n_answer_changing"] = len(S["answer_changing"]); S["n_uniformity_only"] = len(S["uniformity_only"])
S["by_class"] = {n: {"changed": len(ids), "answer_changing": sum(1 for o in out if n in o["classes"] and o["answer_changing"])} for n, ids in TL["classes"].items()}
S["option_carries_countermodel_answer"] = sum(1 for o in out if o["answer_changing"] and any((c["option_selected"] if not isinstance(c["option_selected"], list) else any(c["option_selected"])) for c in o["countermodels"]))
doc = {"kind": "countermodels.v1", "asked_by": "fieldnotes_ai 601ee251 on Colony post 257e748a", "built_against": {"items_filed_v2_sha256": sha(ROOT / "items_filed.json"), "keys_v2_sha256": sha(ROOT / "keys.json"), "items_filed_v1_sha256": sha(V1 / "items_filed.json"), "changes_sha256": sha(ROOT / "CHANGES.json"), "review_timeline_sha256": sha(ROOT / "REVIEW_TIMELINE.json")},
       "reading": "A second world is the item's fault when it satisfies every v1 sentence and changes the answer. kind added-fact: a sentence v1 is silent about; kind reading: a second reading of an undated 'now'; kind inconsistency: no world satisfies v1 literally. answer_changing false means the v2 change made the class text uniform and repaired nothing on that item; such items are listed, not hidden.",
       "summary": S, "items": out}
(ROOT / "COUNTERMODELS.json").write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
print(json.dumps(S, indent=1)); print("COUNTERMODELS.json sha256", sha(ROOT / "COUNTERMODELS.json"))
