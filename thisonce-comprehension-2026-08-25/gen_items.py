#!/usr/bin/env python3
"""this-once / from-now-on — the pre-registered design as amended in review (Excelsior, 2026-08-25).

Each frame: a directive given during a task, then a LATER piece of work at one of four attachment
distances — same artifact / same session, different artifact / different session, same user /
different user. Two hidden-intent worlds share a byte-identical bare directive (one intends
one-off, one standing), so no default reading earns credit in both. Arms: ainglish = the tagged
directive (`, this-once` / `, from-now-on`); english = the careful control (`, just this once` /
`, from now on`); the bare arm is emitted as a separate comparator set.

Probe 1 (the operational one): the six-way STORAGE TARGET — where should the receiver keep this
instruction? {task-local state | artifact record | session state | project memory | global
preference | nowhere}. The flagship binary ("survives this task or not") is derived from it;
attachment stays visible. Probe 2: does the directive govern the later work? {yes | no | cannot
tell}. Retry cells: the later work is a RETRY of the same task (this-once must survive).
Calibration: bare English (persistence undeterminable) vs the tagged form.
"""
import json, random
rng = random.Random(20260825)
DIRECTIVES = [("use British spelling","document"),("run the linter before you commit","branch"),("keep changelog entries in past tense","release"),
              ("cite the line number with every claim","review"),("quote prices in euros","invoice"),("prefer composition over inheritance here","module"),
              ("ask before touching production","task"),("summarise findings before the detail","report"),("use tabs rather than spaces","file"),("address me by my first name","thread")]
LATER = [("retry",      "You are retrying the same task after a first attempt failed.",                      "task-local state"),
         ("artifact",   "You are now editing a second, unrelated {unit} for the same person in the same session.", None),
         ("session",    "A new session starts the next day; the same person asks for a comparable {unit}.",       None),
         ("user",       "A different person, in a different project, asks for a comparable {unit}.",              None)]
# Discordant strata (Saturnia's review, 2026-08-26): applicability is scored SEPARATELY from whether a
# save is licensed. Each stratum adds a policy clause to the frame and keeps the applicability key of
# the directive's scope: a standing directive stays binding where retention policy forbids saving it;
# a one-off directive stays one-off where every instruction must be logged; and a standing directive
# is PROJECT-scoped, so the same person in a different project is outside it.
STRATA = [("storage-forbidden", "Your retention policy forbids saving anything this person says beyond the current session.",
           ("session", "A new session starts the next day; the same person asks for a comparable {unit}.")),
          ("audit-required",    "Every instruction you receive must be written to the audit log.",
           ("artifact", "You are now editing a second, unrelated {unit} for the same person in the same session.")),
          ("project-scope",     "",
           ("project", "The same person, in a different project, asks for a comparable {unit}."))]
TARGET = ["task-local state","artifact record","session state","project memory","global preference","nowhere"]
def key_target(form, later):
    # Where to KEEP the instruction is decided at receipt and is a property of the directive, not
    # of whatever work comes later: this-once lives in task-local state (so a retry of the same
    # task still honours it, and nothing after it does); from-now-on lives in PROJECT memory —
    # durable for this person's comparable work, and deliberately not the global preference store,
    # which is the cross-person overreach the construct exists to prevent.
    return "task-local state" if form == "once" else "project memory"
def key_governs(form, later):
    if form=="once": return "yes" if later=="retry" else "no"
    return "no" if later in ("user", "project") else "yes"   # from-now-on is project-scoped, not global
CTRL={"once":", just this once.","standing":", from now on."}; TAG={"once":", this-once.","standing":", from-now-on."}
def build():
    items=[]; k=0
    for di,(dtext,unit) in enumerate(DIRECTIVES):
        for li,(later,ltext,_) in enumerate(LATER):
            for form in ("once","standing"):
                frame=f"Earlier, while you were working on a {unit}, the person you work for said: \"{dtext[0].upper()+dtext[1:]}"
                ain=frame+TAG[form]+"\" "+ltext.format(unit=unit); eng=frame+CTRL[form]+"\" "+ltext.format(unit=unit); bare=frame+".\" "+ltext.format(unit=unit)
                t=key_target(form,later); rot=k%6; o1=TARGET[rot:]+TARGET[:rot]
                items.append({"id":f"to-{form[:4]}-{k+1:03d}q1","form":form,"later":later,"probe":1,"english":eng,"ainglish":ain,"bare":bare,
                              "question":"Where should you keep that instruction so it applies exactly as far as it was meant to?","options":o1,"answer":t})
                g=key_governs(form,later); o2=["yes","no","cannot tell"]; rot=k%3; o2=o2[rot:]+o2[:rot]
                items.append({"id":f"to-{form[:4]}-{k+1:03d}q2","form":form,"later":later,"probe":2,"english":eng,"ainglish":ain,"bare":bare,
                              "question":"Does that instruction apply to the work you are doing now?","options":o2,"answer":g})
                k+=1
    # strata: applicability only, one item per (directive, stratum, form); OWN counter so the core
    # items keep exactly their v1 ids and option rotations (byte-identical to the 2026-08-25 freeze)
    ks=0
    for di,(dtext,unit) in enumerate(DIRECTIVES):
        for si,(sname,clause,(later,ltext)) in enumerate(STRATA):
            for form in ("once","standing"):
                pre=(clause+" ") if clause else ""
                frame=f"{pre}Earlier, while you were working on a {unit}, the person you work for said: \"{dtext[0].upper()+dtext[1:]}"
                ain=frame+TAG[form]+"\" "+ltext.format(unit=unit); eng=frame+CTRL[form]+"\" "+ltext.format(unit=unit); bare=frame+".\" "+ltext.format(unit=unit)
                g=key_governs(form,later); o2=["yes","no","cannot tell"]; rot=ks%3; o2=o2[rot:]+o2[:rot]
                items.append({"id":f"to-{form[:4]}-s{ks+1:03d}","form":form,"later":later,"stratum":sname,"probe":2,"english":eng,"ainglish":ain,"bare":bare,
                              "question":"Does that instruction apply to the work you are doing now?","options":o2,"answer":g})
                ks+=1
    return items
def calibration():
    out=[]
    for j in range(8):
        dtext,unit=DIRECTIVES[j%len(DIRECTIVES)]; form=("once","standing")[j%2]; later,ltext,_=LATER[1+(j%2)]   # artifact/session: the two forms key differently there (retry and user/project key alike)
        frame=f"Earlier, while you were working on a {unit}, the person you work for said: \"{dtext[0].upper()+dtext[1:]}"
        # Control v2 (2026-08-26): both arms careful, OPPOSITE forms, so the keys differ and a reader
        # cannot score the planted key in both arms (v1's bare English arm was "undeterminable" only
        # on paper — the same leak that failed moved-earlier's control).
        opp="standing" if form=="once" else "once"
        eng=frame+CTRL[opp]+"\" "+ltext.format(unit=unit); ain=frame+CTRL[form]+"\" "+ltext.format(unit=unit)
        g=key_governs(form,later); assert key_governs(opp,later)!=g, (form,later); o=["yes","no","cannot tell"]; rot=j%3; o=o[rot:]+o[:rot]
        out.append({"id":f"to-cal-{j+1:02d}","form":form,"calibration":True,"english":eng,"ainglish":ain,"question":"Does that instruction apply to the work you are doing now?","options":o,"answer":g})
    return out
if __name__=="__main__":
    import copy, collections
    base=build()
    for comp in ("careful","bare"):
        items=copy.deepcopy(base)
        for it in items:
            if comp=="bare": it["english"]=it["bare"]
            it.pop("bare",None); it["id"]=it["id"].replace("to-", f"to-{comp[:3]}-")
        storage=[i for i in items if i["probe"]==1]; items=[i for i in items if i["probe"]==2]
        json.dump(storage, open(f"items-storage-diag-{comp}.json","w"), indent=1, ensure_ascii=False)   # diagnostic, never the claim
        items+=calibration(); json.dump(items, open(f"items-{comp}.json","w"), indent=1, ensure_ascii=False)
        real=[i for i in items if not i.get("calibration")]
        print(f"{comp}: {len(real)} real (applicability only) + {len(items)-len(real)} cal | forms {collections.Counter(i['form'] for i in real)} | later {collections.Counter(i['later'] for i in real)} | strata {collections.Counter(i.get('stratum','core') for i in real)} | storage-diag {len(storage)}")
    it=json.load(open("items-careful.json"))
    for x in (it[0], it[1], it[6]):
        print(f"\n[{x['id']}] EN: {x['english']}\n{' '*9}AI: {x['ainglish']}\n{' '*9}Q: {x['question']} -> {x['answer']}")
