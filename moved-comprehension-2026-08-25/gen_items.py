#!/usr/bin/env python3
"""moved-earlier / moved-later comprehension items — the row's pre-registered design.

Two hidden-intent worlds per frame sharing an IDENTICAL bare comparator ("moved forward two days",
rotating "pushed back", "moved up", "brought forward"); one intends earlier, one later. The frame
states the current schedule anchor (a weekday) and the shift size; context never leaks the key.
Probe 1: name the weekday of the new occurrence (anchor day in the frame; candidates other days +
cannot tell). Probe 2: "a job that fires at the old time — does it now fire too late, too early, or
as scheduled?" — option vocabulary absent from both arms. Domains crossed; forms reported separately
(this generator emits one set per form; strata never pooled). Calibration: English bare comparator
(direction undeterminable) vs Ainglish marked form (direction derivable) — planted effect.
"""
import json, random, hashlib
rng = random.Random(20260825)
DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
DOMAINS = [("the standup","meeting"),("the maintenance window","ops"),("the nightly build","cron"),("the ballot close","governance"),
           ("the settlement close","governance"),("the design review","meeting"),("the delivery slot","logistics"),("the backup job","cron"),
           ("the deadline for comments","deadline"),("the vendor call","meeting")]
BARE = ["moved forward {n} day{s}", "pushed back {n} day{s}", "moved up {n} day{s}", "brought forward {n} day{s}"]
def careful(form, n):
    d = f"{n} day{'s' if n>1 else ''}"
    return (f"is rescheduled to a time {d} earlier than its current schedule" if form=="earlier" else f"is rescheduled to a time {d} later than its current schedule")
def build(form):
    items=[]; k=0
    for dom_i,(ev,domain) in enumerate(DOMAINS):
        for rep in range(5):                       # 10 domains x 5 = 50 frames per form -> 100 items (2 probes)
            n = rng.choice([1,2,3])
            anchor = rng.randrange(n, 7) if form == "earlier" else rng.randrange(0, 7 - n)
            bare = BARE[(dom_i+rep)%len(BARE)].format(n=n, s="s" if n>1 else "")
            newday = DAYS[(anchor - n) % 7] if form=="earlier" else DAYS[(anchor + n) % 7]
            frame = f"{ev[0].upper()+ev[1:]} is currently on {DAYS[anchor]}. "
            ain = frame + f"{ev[0].upper()+ev[1:]} is moved-{form} by {n} day{'s' if n>1 else ''}."
            eng = frame + f"{ev[0].upper()+ev[1:]} {careful(form, n)}."
            bare_arm = frame + f"{ev[0].upper()+ev[1:]} is {bare}."
            # probe 1: weekday of the new occurrence
            wrong = [DAYS[(anchor + n) % 7] if form=="earlier" else DAYS[(anchor - n) % 7], DAYS[anchor]]
            opts1 = [newday, wrong[0], wrong[1], "cannot tell"]; rot=k%4; opts1=opts1[rot:]+opts1[:rot]
            items.append({"id": f"me-{form[:3]}-{k+1:03d}q1", "form": form, "domain": domain, "probe": 1, "anchor": DAYS[anchor], "shift": n,
                          "english": eng, "ainglish": ain, "bare": bare_arm,
                          "question": f"On what day does {ev} now occur?", "options": opts1, "answer": newday})
            # probe 2: the job that fires at the old time
            key2 = "too late" if form=="earlier" else "too early"
            opts2 = ["too late", "too early", "as scheduled", "cannot tell"]; rot=(k+1)%4; opts2=opts2[rot:]+opts2[:rot]
            items.append({"id": f"me-{form[:3]}-{k+1:03d}q2", "form": form, "domain": domain, "probe": 2, "anchor": DAYS[anchor], "shift": n,
                          "english": eng, "ainglish": ain, "bare": bare_arm,
                          "question": f"A job is set to fire at the time {ev} used to be. Does it now fire too late, too early, or as scheduled?", "options": opts2, "answer": key2})
            k+=1
    return items
def calibration(form):
    out=[]
    for j in range(8):
        ev,_=DOMAINS[j%len(DOMAINS)]; n=1+(j%3); anchor=(3+j)%4+3 if form=="earlier" else (j%4)
        newday = DAYS[(anchor - n) % 7] if form=="earlier" else DAYS[(anchor + n) % 7]
        frame=f"{ev[0].upper()+ev[1:]} is currently on {DAYS[anchor]}. "
        # Positive control (v2): the English arm is a CAREFUL phrase whose correct answer is a DIFFERENT
        # day (the opposite direction), so a reader cannot score the planted key in both arms. v1 used
        # the bare phrases here on the assumption they were undeterminable; readers resolved "moved
        # forward"/"pushed back" three-to-one toward EARLIER, and the earlier-form control leaked (0.75).
        opposite = "later" if form == "earlier" else "earlier"
        eng = frame + f"{ev[0].upper()+ev[1:]} is moved to {n} day{'s' if n>1 else ''} {opposite}."      # careful, resolvable to the OTHER day
        ain = frame + f"{ev[0].upper()+ev[1:]} is moved-{form} by {n} day{'s' if n>1 else ''}."               # marked: derivable to newday
        other = DAYS[(anchor + n) % 7] if form=="earlier" else DAYS[(anchor - n) % 7]
        opts=[newday, other, DAYS[anchor], "cannot tell"]; rot=j%4; opts=opts[rot:]+opts[:rot]
        out.append({"id": f"me-{form[:3]}-cal-{j+1:02d}", "form": form, "calibration": True, "english": eng, "ainglish": ain,
                    "question": f"On what day does {ev} now occur?", "options": opts, "answer": newday})
    return out
if __name__=="__main__":
    import copy
    for form in ("earlier","later"):
        base=build(form)
        for comp in ("careful","bare"):
            items=copy.deepcopy(base)
            for it in items:
                if comp=="bare": it["english"]=it["bare"]
                it.pop("bare", None); it["id"]=it["id"].replace(f"me-{form[:3]}-", f"me-{form[:3]}-{comp[:3]}-")
            items += calibration(form)
            json.dump(items, open(f"items-{form}-{comp}.json","w"), indent=1, ensure_ascii=False)
        items=json.load(open(f"items-{form}-careful.json"))
        real=[i for i in items if not i.get("calibration")]
        pos={}
        for i in real: p=i["options"].index(i["answer"]); pos[p]=pos.get(p,0)+1
        print(f"{form}: {len(real)} real + {len(items)-len(real)} cal; key positions {dict(sorted(pos.items()))}; domains {len(set(i['domain'] for i in real))}")
    it=json.load(open("items-earlier-careful.json"))
    for x in (it[0], it[1], [i for i in it if i.get('calibration')][0]):
        print(f"\n[{x['id']}] EN: {x['english']}\n{' '*11}AI: {x['ainglish']}\n{' '*11}BARE: {x.get('bare','-')}\n{' '*11}Q: {x['question']} -> {x['answer']}  {x['options']}")
