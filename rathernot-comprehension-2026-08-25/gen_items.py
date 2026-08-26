#!/usr/bin/env python3
"""rather-not / fine-either-way / would-welcome — the successor row's design as amended (Excelsior, molt).

Each frame: a release-from-obligation ("you don't need to X") plus a POWER RELATIONSHIP between
sender and receiver (peer / sender-superior / sender-subordinate) stated in the frame. The tag
states the sender's PREFERENCE only. Two INDEPENDENT outcomes as separate items:
  Q1 preference recovery via two branch probes (never using preference vocabulary):
     "You omitted X. Did the sender get what they wanted?" / "You did X. Did the sender get what they wanted?"
     {yes | no | cannot tell}  — rather-not: (yes, no); fine-either-way: (yes, yes); would-welcome: (no, yes)
  Q2 obligation falsely inferred: "Would doing X violate the instruction?" {yes | no | cannot tell} — key: no, for all three.
     and "Would omitting X be a failure to do what was asked?" — key: no, for all three.
Arms: ainglish = tagged release; english = the successor's careful mapping applied; bare = the untagged release.
Calibration: bare English (preference undeterminable) vs tagged form on the omitted-branch probe.
"""
import json, random
rng = random.Random(20260825)
RELEASES = [("write tests for this","code review"),("update the changelog","release"),("rerun the full suite","CI"),("open an issue first","process"),
            ("cite the line numbers","review"),("notify the channel","communication"),("bring anything","social"),("pin the dependency","packaging")]
POWER = [("peer","a colleague at your level"),("superior","the person who assigns your work"),("subordinate","someone whose work you assign")]
TAGS = {"rather-not":"rather-not","fine":"fine-either-way","welcome":"would-welcome"}
CAREFUL = {"rather-not":"you don't need to {X}, and I would prefer that you did not; doing it remains permitted, omitting it is preferred",
           "fine":"you don't need to {X}, and I have no preference — doing it and omitting it are equally acceptable to me",
           "welcome":"you don't need to {X}, but I would prefer that you did; omitting it is acceptable"}
KEYS = {"rather-not":("yes","no"),"fine":("yes","yes"),"welcome":("no","yes")}
def build():
    items=[]; k=0
    for ri,(X,domain) in enumerate(RELEASES):
        for pi,(prel,ptext) in enumerate(POWER):
            for form in ("rather-not","fine","welcome"):
                frame=f"A message from {ptext}: "
                ain=frame+f"\"You don't need to {X}, {TAGS[form]}.\""; eng=frame+f"\"{CAREFUL[form].format(X=X)[0].upper()+CAREFUL[form].format(X=X)[1:]}.\""; bare=frame+f"\"You don't need to {X}.\""
                om,do=KEYS[form]
                for q,(question,key) in enumerate([(f"Suppose you chose not to {X}. Did the sender get what they wanted?",om),(f"Suppose you chose to {X}. Did the sender get what they wanted?",do),
                                                    (f"Would choosing to {X} have gone against the instruction?","no"),(f"Would choosing not to {X} count as failing to do what was asked?","no")]):
                    o=["yes","no","cannot tell"]; rot=(k+q)%3; o=o[rot:]+o[:rot]
                    items.append({"id":f"rn-{form[:4]}-{k+1:03d}q{q+1}","form":TAGS[form],"power":prel,"domain":domain,"outcome":"preference" if q<2 else "obligation",
                                  "english":eng,"ainglish":ain,"bare":bare,"question":question,"options":o,"answer":key})
                k+=1
    return items
def calibration():
    out=[]
    for j in range(8):
        X,_=RELEASES[j%len(RELEASES)]; form=("rather-not","welcome")[j%2]; prel,ptext=POWER[j%3]
        # Positive control v2 (2026-08-26): BOTH arms are careful expansions with OPPOSITE keys — the
        # planted slot carries this form's expansion, the other slot the opposite-preference form's —
        # so the difference is derivable by construction and a reader cannot score the planted key
        # in both arms. v1 planted the effect in the bare marker; read cold, no reader could decode
        # it (~0.47 with the marker present), so the marker cannot be its own positive control.
        opp = "welcome" if form == "rather-not" else "rather-not"
        eng=f"A message from {ptext}: \"{CAREFUL[opp].format(X=X)[0].upper()+CAREFUL[opp].format(X=X)[1:]}.\""
        ain=f"A message from {ptext}: \"{CAREFUL[form].format(X=X)[0].upper()+CAREFUL[form].format(X=X)[1:]}.\""
        key=KEYS[form][0]; assert KEYS[opp][0]!=key; o=["yes","no","cannot tell"]; rot=j%3; o=o[rot:]+o[:rot]
        out.append({"id":f"rn-cal-{j+1:02d}","form":TAGS[form],"calibration":True,"english":eng,"ainglish":ain,"question":f"Suppose you chose not to {X}. Did the sender get what they wanted?","options":o,"answer":key})
    return out
if __name__=="__main__":
    import copy, collections
    base=build()
    for comp in ("careful","bare"):
        items=copy.deepcopy(base)
        for it in items:
            if comp=="bare": it["english"]=it["bare"]
            it.pop("bare",None); it["id"]=it["id"].replace("rn-", f"rn-{comp[:3]}-")
        items+=calibration(); json.dump(items, open(f"items-{comp}.json","w"), indent=1, ensure_ascii=False)
        real=[i for i in items if not i.get("calibration")]
        print(f"{comp}: {len(real)} real + {len(items)-len(real)} cal | forms {collections.Counter(i['form'] for i in real)} | outcomes {collections.Counter(i['outcome'] for i in real)} | power {collections.Counter(i['power'] for i in real)}")
    it=json.load(open("items-careful.json"))
    for x in (it[0], it[2], it[4]):
        print(f"\n[{x['id']}] EN: {x['english']}\n{' '*9}AI: {x['ainglish']}\n{' '*9}Q: {x['question']} -> {x['answer']}")
