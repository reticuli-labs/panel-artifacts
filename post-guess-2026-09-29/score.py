"""Scoring of the post against predictions.md (frozen at ed30c5bf). Labels are my judgment after reading."""
import json, hashlib, collections
meta = json.load(open("sealed_meta.json")); sealed = json.load(open("sealed.json"))
assert hashlib.sha256(sealed["post"]["body"].encode()).hexdigest() == meta["body_sha256"]
assert hashlib.sha256(open("predictions.md", "rb").read()).hexdigest() == open("predictions.sha256").read().split()[0]
P = [
 ("links the result to earlier results by number (R05, R08)", "G", "guess 12"),
 ("the question it answers came from specie", "F", None),
 ("PyBaMM 26.8, DFN model", "G", "guess 2"),
 ("O'Kane 2022 parameters with SEI, partially reversible plating, particle mechanics, SEI on cracks", "F", None),
 ("thickness stated: k = 2, cathode 151 µm (I guessed the graphite side would be named)", "G", "guess 5"),
 ("C/2 CC-CV", "G", "guess 5"),
 ("300 cycles", "G", "guess 6"),
 ("two tortuosity levels at three conductivity levels", "G", "guess 3"),
 ("the tortuosity values are 1.2 and 1.8", "F", None),
 ("transference number 0.26", "F", None),
 ("conductivity scaled by 0.5 and by 2, the whole function multiplied (what the post states; see the probe for what ran)", "G", "guess 3"),
 ("the baseline rows are borrowed from R08", "F", None),
 ("wrapper script and results file named", "G", "guess 11"),
 ("a table of the three levels with plating and retention for both electrodes", "G", "guess 9"),
 ("the twelve cell values in the table", "F", None),
 ("plating penalties 80.3, 25.2 and 14.9 mAh; retention penalties 7.26 and 0.85 pt", "T", None),
 ("retention penalty at double conductivity is 0.60 pt", "F", None),
 ("penalty means the difference between the two electrodes", "G", "guess 4"),
 ("the retention penalty is multiplied by eight", "T", None),
 ("at the low level and tortuosity 1.8 the cell keeps 87 percent", "F", None),
 ("doubling cuts the plating penalty by 41 percent, with diminishing returns", "T", None),
 ("comparable to raising the transference number to 0.40, which gave 63 percent in R08", "F", None),
 ("SEI loss stays flat near 0.04 Ah", "F", None),
 ("so the whole effect is plating", "L", None),
 ("low tortuosity is insurance: nearly worthless with good transport, decisive with poor", "T", None),
 ("real causes named: cold, depletion with age, viscous or concentrated electrolyte", "G", "guess 8"),
 ("the trade-off curve needs conductivity as an axis", "L", None),
 ("the recommendation flips with the electrolyte", "L", None),
 ("electrolyte optimisation substitutes for structure only on the good-transport side", "L", None),
 ("limits: two points and a baseline, one rate, one transference number", "L", None),
 ("the cliff lies between the low level and the baseline and is unmapped", "L", None),
 ("the command line that produced it", "G", "guess 11"),
 ("environment: python 3.13.4, darwin arm64", "F", None),
 ("their own grading: verdict PARTIAL, evidence E2, first run", "F", None),
 ("needed 5-cycle chunks to stay under 6 GB", "F", None),
 ("lineage: 103c, R08, R10, R05", "F", None),
]
G = {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: False, 8: True, 9: True, 10: False, 11: True, 12: True, 13: True, 14: True, 15: False, 16: False}
WHY = {7: "the post gives no mechanism for the asymmetry at all", 10: "the limits are about the coverage of the sweep; nothing on chemistry, model or plating parameters",
       13: "held, and checked in the code: only the conductivity function is touched, diffusivity is not, and the post does not name it as a limit",
       14: "held: no interval or spread is given", 15: "one paragraph ending in a question, but it accepts the result; it is not sceptical",
       16: "it asks about a floor or a ceiling; it does not doubt the model. It brings no number, as guessed",
       1: "held through the PyBaMM point"}
c = collections.Counter(l for _, l, _ in P)
out = {"kind": "reticuli.post-guess.scoring.v1", "post": meta["post_id"], "predictions_sha256": open("predictions.sha256").read().split()[0],
       "points": [{"n": i + 1, "point": p, "label": l, **({"via": v} if v else {})} for i, (p, l, v) in enumerate(P)],
       "guesses": [{"n": n, "held": h, **({"note": WHY[n]} if n in WHY else {})} for n, h in sorted(G.items())],
       "totals": {"points": len(P), "T": c["T"], "G": c["G"], "F": c["F"], "L": c["L"], "O": c["O"], "guesses": len(G), "guesses_held": sum(G.values()), "guesses_missed": len(G) - sum(G.values())},
       "note": "No point of the post is labelled O. The three findings in findings.json are not points of the post: they came from running code, which no guess covered."}
assert sum(c.values()) == len(P) and set(c) <= set("TGFLO")
json.dump(out, open("scoring.json", "w"), indent=1, ensure_ascii=False); print(json.dumps(out["totals"]))
