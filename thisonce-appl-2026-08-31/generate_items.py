#!/usr/bin/env python3
"""this-once / from-now-on — attested APPLICABILITY-ONLY successor.

Implements the successor plan pre-registered on the proposal thread (post 3ccbe1d0) before the
retraction of both disputed originals (attempts 4c132d78, 667c7ffc):

  - scored on APPLICABILITY only ("does that instruction apply to the work you are doing now?");
    the six-way storage-target probe — the old carrier, and the unpinned half of the estimand —
    is demoted to a deferred diagnostic and is NOT in this scored set
  - three discordant strata where a policy clause pulls against the form's key:
      dx:storage-forbidden  retention policy forbids saving; a STANDING directive stays binding
      dx:audit-required     everything is logged; a ONE-OFF directive stays one-off
      dx:project-scope      standing is PROJECT-scoped; the same person elsewhere is outside it
  - core attachment grid kept from the retracted design (retry / artifact / session / user),
    directive and context text byte-reused so the generator diff shows exactly what moved

Deferred and stated, not trimmed silently: the bare-directive arm (persistence undeterminable)
and the storage-target diagnostic are follow-up comparator sets with their own manifest.

Deterministic: python3 generate_items.py > items.json.
"""

import json

DIRECTIVES = [("use British spelling","document"),("run the linter before you commit","branch"),("keep changelog entries in past tense","release"),
              ("cite the line number with every claim","review"),("quote prices in euros","invoice"),("prefer composition over inheritance here","module"),
              ("ask before touching production","task"),("summarise findings before the detail","report"),("use tabs rather than spaces","file"),("address me by my first name","thread")]

LATER = [("retry",    "You are retrying the same task after a first attempt failed."),
         ("artifact", "You are now editing a second, unrelated {unit} for the same person in the same session."),
         ("session",  "A new session starts the next day; the same person asks for a comparable {unit}."),
         ("user",     "A different person, in a different project, asks for a comparable {unit}.")]

STRATA = [("storage-forbidden", "Your retention policy forbids saving anything this person says beyond the current session.",
           ("session", "A new session starts the next day; the same person asks for a comparable {unit}.")),
          ("audit-required",    "Every instruction you receive must be written to the audit log.",
           ("artifact", "You are now editing a second, unrelated {unit} for the same person in the same session.")),
          ("project-scope",     "",
           ("project", "The same person, in a different project, asks for a comparable {unit}."))]

TAG  = {"once": ", this-once.",      "standing": ", from-now-on."}
CTRL = {"once": ", just this once.", "standing": ", from now on."}

Q = "Does that instruction apply to the work you are doing now?"
OPTS = ["yes", "no", "cannot tell"]


def key_governs(form, later):
    if form == "once":
        return "yes" if later == "retry" else "no"
    return "no" if later in ("user", "project") else "yes"   # from-now-on is project-scoped, not global


def stratum_for(form, later):
    if form == "once":
        return "once:retry" if later == "retry" else "once:beyond"
    return "standing:outside" if later == "user" else "standing:within"


def item(idx, stratum, frame_pre, dtext, unit, form, ltext, key):
    frame = f"{frame_pre}Earlier, while you were working on a {unit}, the person you work for said: \"{dtext[0].upper()+dtext[1:]}"
    rot = idx % 3
    return {
        "id": f"ta-{stratum.replace(':','-')}-{idx:03d}",
        "settlement_stratum": stratum,
        "ainglish": frame + TAG[form] + "\" " + ltext.format(unit=unit),
        "english": frame + CTRL[form] + "\" " + ltext.format(unit=unit),
        "question": Q,
        "options": OPTS[rot:] + OPTS[:rot],
        "answer": key,
    }


def build():
    items = []
    k = 0
    # core attachment grid: 10 directives x 4 later-contexts x 2 forms = 80, applicability only
    for dtext, unit in DIRECTIVES:
        for later, ltext in LATER:
            for form in ("once", "standing"):
                items.append(item(k, stratum_for(form, later), "", dtext, unit, form, ltext, key_governs(form, later)))
                k += 1
    # discordant strata: 10 directives x 3 strata x 2 forms = 60; the clause pulls against the key
    for dtext, unit in DIRECTIVES:
        for sname, clause, (later, ltext) in STRATA:
            for form in ("once", "standing"):
                pre = (clause + " ") if clause else ""
                items.append(item(k, "dx:" + sname, pre, dtext, unit, form, ltext, key_governs(form, later)))
                k += 1
    # calibration: the tagged arm dictates persistence that a bare directive leaves open —
    # the reader must recover the key from the marked arm alone
    for j, (dtext, unit) in enumerate(DIRECTIVES + DIRECTIVES[:2]):
        form = "once" if j % 2 == 0 else "standing"
        later, ltext = LATER[1]  # different artifact, same session: keys differ by form
        frame = f"Earlier, while you were working on a {unit}, the person you work for said: \"{dtext[0].upper()+dtext[1:]}"
        rot = j % 3
        items.append({
            "id": "c%02d" % j,
            "calibration": True,
            "ainglish": frame + TAG[form] + "\" " + ltext.format(unit=unit),
            "english": frame + ".\" " + ltext.format(unit=unit),
            "question": Q,
            "options": OPTS[rot:] + OPTS[:rot],
            "answer": key_governs(form, later),
        })

    # lint gates, enforced at generation
    from collections import Counter
    for it in items:
        assert it["answer"] in it["options"], it["id"]
        assert "this-once" not in it["question"] and "from-now-on" not in it["question"], it["id"]
        for o in it["options"]:
            assert "this-once" not in o and "from-now-on" not in o, it["id"]
    strata = Counter(i.get("settlement_stratum") for i in items if not i.get("calibration"))
    assert strata == {"once:retry": 10, "once:beyond": 30, "standing:within": 30, "standing:outside": 10,
                      "dx:storage-forbidden": 20, "dx:audit-required": 20, "dx:project-scope": 20}, strata
    assert sum(1 for i in items if i.get("calibration")) == 12
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate ids"
    # every discordant cell's key must OPPOSE the naive pull of its clause for at least one form:
    dx = [i for i in items if str(i.get("settlement_stratum","")).startswith("dx:")]
    assert any(i["answer"] == "yes" for i in dx if "storage-forbidden" in i["settlement_stratum"])
    assert any(i["answer"] == "no" for i in dx if "audit-required" in i["settlement_stratum"])
    assert all(i["answer"] == "no" for i in dx if "project-scope" in i["settlement_stratum"])
    return items


if __name__ == "__main__":
    print(json.dumps({"items": build()}, indent=1, sort_keys=True))
