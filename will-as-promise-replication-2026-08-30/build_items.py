#!/usr/bin/env python3
"""Build a will-as-promise / will-as-plan / will-as-forecast pair set.

Independent of Dexagon's original ("In cycle N, <Name> promises the reader to ...") and of
Excelsior's ("I promise to send the signed release to Mara by 17:00 ..."). What is DELIBERATELY
matched is the estimand, not the wording: the english side is a complete careful-English gloss
that states the same three things the marker states -- for a promise, that the utterance itself
creates the commitment and that failing it without release wrongs the addressee; for a plan, that
it is the current intention, that it may change, and that notice is owed if it does; for a
forecast, that it predicts the world, claims no control, and creates no obligation.

That matching is the point. A replication that shortens the gloss measures its own prose.
"""
import json

CONTENT = [
    ("Priya", "the migration runbook", "the release manager", "before the freeze"),
    ("Tomas", "the vendor questionnaire", "the security lead", "this sprint"),
    ("Ines", "the retention audit", "the data steward", "by the review board"),
    ("Kwame", "the rollback switch", "the on-call engineer", "during the window"),
    ("Sora", "the pricing appendix", "the contracts desk", "ahead of signature"),
    ("Rafi", "the incident timeline", "the postmortem group", "before Friday"),
    ("Noor", "the access revocation", "the joiner-mover-leaver queue", "this cycle"),
    ("Elias", "the schema backfill", "the platform team", "in the next window"),
    ("Mira", "the disclosure notice", "the regulator liaison", "within the period"),
    ("Diego", "the capacity forecast", "the finance partner", "for the quarter"),
    ("Ayla", "the consent copy", "the privacy reviewer", "before launch"),
    ("Hugo", "the failover drill", "the reliability guild", "next month"),
    ("Lena", "the licence inventory", "the procurement analyst", "this period"),
    ("Bram", "the redaction pass", "the disclosure officer", "before release"),
    ("Yuki", "the dependency bump", "the maintainer", "in this batch"),
    ("Otto", "the archive export", "the records custodian", "by the deadline"),
]

def promise(a, obj, party, when):
    return (
        f"{a} undertakes to {party} to complete {obj} {when}; saying so is itself what binds "
        f"{a}, and if it is not done and {party} has not released {a} from it, {a} has wronged "
        f"{party}.",
        f"{a} will-as-promise complete {obj} {when} to {party}.",
    )

def plan(a, obj, party, when):
    return (
        f"{a} currently intends to complete {obj} {when}, and tells {party} so; the intention may "
        f"still change, and if it does {a} owes {party} notice of the change, but the saying of it "
        f"binds {a} to nothing.",
        f"{a} will-as-plan complete {obj} {when}, told to {party}.",
    )

def forecast(a, obj, party, when):
    return (
        f"{a} predicts to {party} that {obj} will be complete {when}; the prediction is about how "
        f"things will turn out, {a} claims no control over whether it happens, and {a} takes on no "
        f"obligation by saying it.",
        f"{a} will-as-forecast {obj} complete {when}, told to {party}.",
    )

FORMS = [("will-as-promise", promise), ("will-as-plan", plan), ("will-as-forecast", forecast)]

items = []
n = 0
for actor, obj, party, when in CONTENT:
    for form, fn in FORMS:
        n += 1
        english, ainglish = fn(actor, obj, party, when)
        items.append({"id": f"ret-will-{n:03d}", "form": form,
                      "english": english, "ainglish": ainglish})

if __name__ == "__main__":
    json.dump({"items": items}, open("items.json", "w"), indent=1, ensure_ascii=False)
    print(f"{len(items)} pairs written")
