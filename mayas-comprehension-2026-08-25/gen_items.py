#!/usr/bin/env python3
"""may-as-permission / may-as-possibility — Saturnia's pre-registered design, operationalised.

Each frame: a subject, a predicate, and a WORLD stating (a) the governing authority record
(permits / denies) and (b) the live-outcome state (feasible / blocked). The target sentence uses
ONE marked form in the ainglish arm and its shortest adequate careful control in the english arm
('is permitted to' / 'might'). The two load-bearing cross-cells are included: permitted-but-
impossible (grant + hard technical block) and forbidden-but-possible (denial + working credentials).
Consequence probes, no definition vocabulary: (1) a later disjoint fact arrives — which record
could REFUTE the sentence? (authority record / outcome model / neither / cannot tell); (2) which
response does the sentence LICENSE? (inspect-or-change the authority record / revise-or-mitigate
the outcome model / neither / cannot tell). Balanced over force, cross-cell, subject type, voice,
severity. Bare-'may' descriptive arm emitted as a separate comparator set. Negated may excluded.
Both marked forms in ONE set (strata = form), reported separately by the analyst; calibration:
English bare 'may' (force undeterminable) vs the marked form.
"""
import json, random, hashlib
rng = random.Random(20260825)
SUBJ = [("the export worker","inanimate"),("the on-call engineer","animate"),("the backup job","inanimate"),("the auditor","animate"),
        ("the deploy bot","inanimate"),("the contractor","animate"),("the ingest pipeline","inanimate"),("the reviewer","animate")]
PRED = [("transmit customer data","high"),("restart the primary","high"),("read the staging logs","low"),("post to the status page","low"),("rotate the signing key","high")]
CELLS = {"permission": [("permitted","feasible"),("permitted","blocked")],      # permitted-but-impossible: a forecast reading would be false
         "possibility": [("permitted","feasible"),("denied","feasible")]}      # forbidden-but-possible: an authorisation reading would be false
CTRL = {"permission":"is permitted to", "possibility":"might"}
def world(auth, live, subj, pred):
    a = f"The access policy on file {'grants' if auth=='permitted' else 'denies'} {subj} the action '{pred}'."
    l = (f"Working credentials and a reachable endpoint mean the action can currently go through." if live=="feasible"
         else "A hard technical block (revoked credentials, no route) means the action cannot currently go through.")
    return a + " " + l
def build():
    items=[]; k=0
    for fi,(subj,stype) in enumerate(SUBJ):
        for pi,(pred,sev) in enumerate(PRED):
            for form in ("permission","possibility"):
                cell = CELLS[form][(fi+pi)%2]; auth, live = cell
                w = world(auth, live, subj, pred)
                ain = f"{w} {subj[0].upper()+subj[1:]} may-as-{form} {pred}."
                eng = f"{w} {subj[0].upper()+subj[1:]} {CTRL[form]} {pred}."
                bare = f"{w} {subj[0].upper()+subj[1:]} may {pred}."
                # probe 1: which record could refute the sentence
                key1 = "the authority record" if form=="permission" else "the live-outcome model"
                o1 = ["the authority record","the live-outcome model","neither","cannot tell"]; r=k%4; o1=o1[r:]+o1[:r]
                items.append({"id":f"ma-{form[:4]}-{k+1:03d}q1","form":form,"cell":f"{auth}-{live}","subject_type":stype,"severity":sev,"probe":1,
                              "english":eng,"ainglish":ain,"bare":bare,
                              "question":"A later fact arrives that contradicts the sentence. Which record would that fact have to be about?","options":o1,"answer":key1})
                # probe 2: which response is licensed
                key2 = "inspect or change the authority record" if form=="permission" else "revise or mitigate the live-outcome model"
                o2 = ["inspect or change the authority record","revise or mitigate the live-outcome model","neither","cannot tell"]; r=(k+1)%4; o2=o2[r:]+o2[:r]
                items.append({"id":f"ma-{form[:4]}-{k+1:03d}q2","form":form,"cell":f"{auth}-{live}","subject_type":stype,"severity":sev,"probe":2,
                              "english":eng,"ainglish":ain,"bare":bare,
                              "question":"If the sentence turns out to be wrong, what is the reader licensed to do about it?","options":o2,"answer":key2})
                k+=1
    return items
def calibration():
    out=[]
    for j in range(8):
        subj,_=SUBJ[j%len(SUBJ)]; pred,_=PRED[(j*3)%len(PRED)]; form=("permission","possibility")[j%2]; auth,live=CELLS[form][(j//2)%2]
        w=world(auth,live,subj,pred)
        # Control v2 (2026-08-26): both arms are CAREFUL expansions with OPPOSITE forces, so the two
        # keys differ and neither arm can be answered from the shared world context alone. v1 used a
        # bare 'may' arm; the world sentences state both the grant and the live capability, so a
        # reasoning reader answered the record question from context in BOTH arms (0.75/0.75) and a
        # weak reader in neither (0.13/0.13) — nothing was planted.
        opp = "possibility" if form == "permission" else "permission"
        CTRL = {"permission": "is permitted to", "possibility": "might"}
        eng=f"{w} {subj[0].upper()+subj[1:]} {CTRL[opp]} {pred}."
        ain=f"{w} {subj[0].upper()+subj[1:]} {CTRL[form]} {pred}."
        key="the authority record" if form=="permission" else "the live-outcome model"
        o=["the authority record","the live-outcome model","neither","cannot tell"]; r=j%4; o=o[r:]+o[:r]
        out.append({"id":f"ma-cal-{j+1:02d}","form":form,"calibration":True,"english":eng,"ainglish":ain,
                    "question":"A later fact arrives that contradicts the sentence. Which record would that fact have to be about?","options":o,"answer":key})
    return out
if __name__=="__main__":
    import copy, collections
    base=build()
    for comp in ("careful","bare"):
        items=copy.deepcopy(base)
        for it in items:
            if comp=="bare": it["english"]=it["bare"]
            it.pop("bare",None); it["id"]=it["id"].replace("ma-", f"ma-{comp[:3]}-")
        items+=calibration()
        json.dump(items, open(f"items-{comp}.json","w"), indent=1, ensure_ascii=False)
        real=[i for i in items if not i.get("calibration")]
        c=collections.Counter((i["form"],i["cell"]) for i in real)
        print(f"{comp}: {len(real)} real + {len(items)-len(real)} cal | per form: {collections.Counter(i['form'] for i in real)} | cells: {dict(c)}")
    it=json.load(open("items-careful.json"))
    for x in (it[0], it[3]):
        print(f"\n[{x['id']}] EN: {x['english']}\n{' '*9}AI: {x['ainglish']}\n{' '*9}Q: {x['question']} -> {x['answer']}")
