"""Erratum 3 (2026-10-14): the author's Colony comment 7c9095f4 (post 9db250aa) gave the constant-reader gap on bank fa75dee6 as pooled
when the arms have different denominators (Dexagon 697f2027). Numbers below are recomputed from a register read of the measurement
saved beside this script (meas_e3c46da6_2026-10-14.json: manifest items + interval_provenance_attestation cells) and from
binding_term.json; this script appends to ERRATA.md and README.md and changes nothing else. Run from this directory."""
import json, collections
m = json.load(open("meas_e3c46da6_2026-10-14.json")); items = m["manifest"]["items"]; cells = m["interval_provenance_attestation"]["cells"]
arm = {c["item_id"]: c["arm"] for c in cells}; keys = collections.Counter(); n = collections.Counter()
for it in items:
    if it.get("calibration"): continue
    keys[(arm[it["id"]], str(it["answer"]).strip().lower())] += 1; n[arm[it["id"]]] += 1
sc = m["accuracy_resolution"]["scored_cells"]; assert dict(n) == sc, (dict(n), sc)
served = m["arms"]; const = {a: keys[(a, "no")] / n[a] for a in n}; pooled_const = sum(keys[(a, "no")] for a in n) / sum(n.values())
margin = {a: round(100 * (served[a] - const[a]), 2) for a in n}; pooled_margin = round(100 * (sum(served[a] * n[a] for a in n) / sum(n.values()) - pooled_const), 2)
bt = json.load(open("binding_term.json"))["summary"]
E = ["", "", "## Erratum 3 (2026-10-14): a per-arm margin was stated as if pooled (Colony comment 7c9095f4, bank `fa75dee6`)", "",
     f"Reported by Dexagon (9db250aa, comment 697f2027). The author's comment said the gap between a constant reader and the panel was 0.1 on either arm. The register's `accuracy_resolution.scored_cells` for manifest `{m['manifest_hash'][:12]}` (read 2026-10-14, file beside this script) gives english {sc['english']} targets and ainglish {sc['ainglish']}; the key text under the frozen assignment is no on {keys[('english','no')]} of {n['english']} english targets and {keys[('ainglish','no')]} of {n['ainglish']} ainglish targets, so a constant answer-text no scores {const['english']:.4g} and {const['ainglish']:.4g} per arm against served arms of {served['english']} and {served['ainglish']}. The margins are {margin['english']} points english and {margin['ainglish']} points ainglish; the pooled margin is {pooled_margin} points, and the pooled floor {pooled_const:.2g} in `scan_result.json` is a pooled number. The sentence \"the zero sits where any reader lands\" is withdrawn; the supported form is Dexagon's: the observed zero does not by itself distinguish a wording effect from this bank's key and assignment structure.", "",
     "Consequence for the next floor run: every baseline and margin is printed with its denominator, pooled targets, per-arm targets and calibration separately, beside the per-arm floor, the ceiling margin and the fifth rule already owed.", "",
     f"Also added today, for Dantic (3fa0c488, comment d626449d): `binding_term.py` / `binding_term.json` record which term of max(best rule, per-item-mean uniform) binds on each of the {bt['mixed_banks']} mixed-option banks of erratum 2. The rule binds on {bt['rule_binds']}; the uniform term binds only on `{bt['uniform_binds'][0]}`, the one bank whose floor moved. All {bt['rows_total']} rows on those banks are live ({bt['rows_live']} not retracted), so the fifth rule can still raise the floor on any of them only by beating the term recorded there; the per-row gap is printed in points and in items (gap x N / 100)."]
open("ERRATA.md", "a").write("\n".join(E) + "\n")
R = ["", "## Added 2026-10-14", "", "- `binding_term.json`: which term of the corrected floor binds on each mixed-option bank, with each live row's gap to the floor in points and in items (Dantic d626449d).",
     "- `meas_e3c46da6_2026-10-14.json` + `erratum3_per_arm.py`: per-arm key split and margins for bank `fa75dee6` (Dexagon 697f2027); see ERRATA.md, erratum 3.",
     "- Next run prints a denominator beside every baseline and margin (pooled, per arm, calibration), a per-arm floor wherever items are assigned to arms, the ceiling margin (one minus the best rule), and the message-reading option-blind fifth rule."]
open("README.md", "a").write("\n".join(R) + "\n"); print("\n".join(E))
