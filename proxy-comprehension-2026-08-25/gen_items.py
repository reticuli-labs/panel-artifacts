#!/usr/bin/env python3
"""proxy(<M>) comprehension items — Rosetta's pre-registered design, operationalised for a two-arm
harness with held-out probes.

Every scenario: a claim X whose only directly-verified evidence is a measured quantity M that is a
proxy for X (the design's population). Two probes per scenario, as separate items (the some-or-all
precedent), with option vocabulary sharing no stem with 'proxy'/'verify'/'infer' in either arm:
  Q1  "What did the writer directly check?"            {M only | X only | both | cannot tell}  key: M only
  Q2  "If X later turns out false, what was wrong?"    {reading of M | step from M to X | nothing: X was checked directly | cannot tell}  key: step
Arms for the CARRIER run: ainglish = `X proxy(<M>)`; english = the complete careful-English disclosure.
The generator also emits the two diagnostic comparators the design names: bare "X, and I measured M"
and the source-tagged `X obs(M)` (distinctiveness), as separate english arms for separate runs.
Calibration (planted): english arm says X was checked directly; ainglish arm marks proxy(M).
"""
import json, random, hashlib
rng = random.Random(20260825)
# (X claim, M measured, domain) — M correlates with X but is not X
SCEN = [
 ("9 people read the message", "page-fetches", "9 of 9 fetches"), ("the service is healthy", "ping-latency", "ping under 5 ms"),
 ("the migration succeeded", "exit-code", "exit code 0"), ("users understood the notice", "click-through", "click-through of 62 percent"),
 ("the backup is restorable", "file-count", "all 4,120 files present"), ("the model improved", "loss-curve", "training loss down 12 percent"),
 ("the vote was representative", "turnout", "turnout of 71 percent"), ("the patch fixed the bug", "test-pass", "the regression test passing"),
 ("the reviewer read the diff", "time-open", "the tab open for 40 minutes"), ("the cache is warm", "hit-rate", "a 94 percent hit rate"),
 ("the agent is idle", "cpu-load", "CPU load under 2 percent"), ("the document is accurate", "spell-check", "zero spelling errors"),
 ("the deploy reached every region", "dns-propagation", "DNS answers from all 6 resolvers"), ("the audience was engaged", "dwell-time", "median dwell of 3 minutes"),
 ("the key was rotated", "timestamp-change", "a new mtime on the key file"), ("the queue is drained", "queue-length", "queue length 0 at 09:00"),
 ("the translation is faithful", "back-translation", "back-translation matching 88 percent"), ("the anchor is confirmed", "calendar-ack", "acknowledgements from 4 calendars"),
 ("the contributor accepted the terms", "checkbox", "the checkbox ticked"), ("the sensor is calibrated", "self-test", "the self-test passing"),
 ("the room is empty", "motion-sensor", "no motion for 10 minutes"), ("the dataset is deduplicated", "hash-uniqueness", "all row hashes unique"),
 ("the customer is satisfied", "nps-score", "an NPS of 9"), ("the link is secure", "padlock-icon", "the padlock icon showing"),
 ("the disk is healthy", "smart-status", "SMART status OK"), ("the meeting happened", "calendar-entry", "the calendar entry marked done"),
 ("the code is tested", "coverage", "coverage of 91 percent"), ("the alert was seen", "notification-delivered", "the notification marked delivered"),
 ("the argument is sound", "citation-count", "14 citations"), ("the API is compatible", "schema-diff", "an empty schema diff"),
]
OPT1 = {"m": "the measurement ({M_label}) only", "x": "the claim itself ({X_label}) only", "both": "both the measurement and the claim", "ct": "cannot tell"}
OPT2 = {"m": "the {M_label} reading itself", "step": "the step from {M_label} to the claim", "none": "nothing — the claim was checked directly", "ct": "cannot tell"}
def arms(X, Mtag, Mtext):
    Ml = Mtag.replace("-", " ")
    return {
      # The register form: claim X, then the marker naming the measured quantity; the reading follows.
      "ainglish": f"{X[0].upper()+X[1:]} proxy(<{Mtag}>); {Mtext}.",
      # The proposal's own mapping, applied verbatim (v2: the English arm is the declared mapping, not a competitor I wrote).
      "careful":  (f"{X[0].upper()+X[1:]}; the evidence I directly verified is {Ml} ({Mtext}); {Ml} is a proxy for "
                   f"whether {X}, not the same thing; the inference from {Ml} to whether {X} is the load-bearing step and it is unverified."),
      "bare":     f"{X[0].upper()+X[1:]}, and I measured {Mtext}.",
      "obs":      f"{X[0].upper()+X[1:]} obs({Mtag}); {Mtext}.",
    }
def build(comparator):
    items=[]; order=list(range(len(SCEN))); rng.shuffle(order)
    for k,idx in enumerate(order):
        X, Mtag, Mtext = SCEN[idx]; a = arms(X, Mtag, Mtext)
        Ml = Mtag.replace("-", " "); Xl = f"that {X}"
        for q, (question, opts, key) in enumerate([
            ("What did the writer directly check?", [OPT1["m"], OPT1["x"], OPT1["both"], OPT1["ct"]], OPT1["m"]),
            (f"Suppose it later turns out that it is NOT the case that {X}. Going only by the sentence, what was wrong?", [OPT2["m"], OPT2["step"], OPT2["none"], OPT2["ct"]], OPT2["step"]),
        ]):
            opts=[o.format(M_label=Ml, X_label=Xl) for o in opts]; key=key.format(M_label=Ml, X_label=Xl)
            rot=(k+q)%4; opts=opts[rot:]+opts[:rot]
            items.append({"id": f"pr-{comparator[:3]}-{k+1:02d}q{q+1}", "scenario": idx, "probe": q+1,
                          "english": a[comparator], "ainglish": a["ainglish"], "question": question, "options": opts, "answer": key})
    return items
def calibration(comparator):
    out=[]
    for j in range(8):
        X, Mtag, Mtext = SCEN[(j*7)%len(SCEN)]; Ml=Mtag.replace("-"," "); Xl=f"that {X}"
        eng = f"{X[0].upper()+X[1:]}; I checked that directly."
        ain = f"{X[0].upper()+X[1:]} proxy(<{Mtag}>): {Mtext}."
        opts=[OPT1["m"], OPT1["x"], OPT1["both"], OPT1["ct"]]; opts=[o.format(M_label=Ml, X_label=Xl) for o in opts]
        rot=j%4; opts=opts[rot:]+opts[:rot]
        out.append({"id": f"pr-{comparator[:3]}-cal-{j+1:02d}", "calibration": True, "english": eng, "ainglish": ain,
                    "question": "What did the writer directly check?", "options": opts, "answer": OPT1["m"].format(M_label=Ml, X_label=Xl)})
    return out
if __name__ == "__main__":
    for comp in ("careful", "bare", "obs"):
        items = build(comp) + calibration(comp)
        json.dump(items, open(f"items-{comp}.json","w"), indent=1, ensure_ascii=False)
        real=[i for i in items if not i.get("calibration")]
        print(f"{comp}: {len(real)} real (30 scenarios x 2 probes) + {len(items)-len(real)} cal")
    it=json.load(open("items-careful.json"))
    for i in (0,1,60):
        x=it[i]; print(f"\n[{x['id']}] EN: {x['english']}\n{' '*9}AI: {x['ainglish']}\n{' '*9}Q:  {x['question']}\n{' '*9}-> {x['answer']}   options={x['options']}")
