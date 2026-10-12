"""Writes README.md from the frozen previews and the served rows; every number is read from the files beside it."""
import json, hashlib
from pathlib import Path
H = Path(__file__).resolve().parent
def L(n): return json.loads((H / n).read_text())
pe, pc, ch, res, before, after = L("preview_english_mapping.json"), L("preview_corruption_cells_only.json"), L("changes_submitted.json"), L("result_successor.json"), L("row_before.json"), L("row_after.json")
pb, pa = before.get("proposal", before), after.get("proposal", after)
assert pe["dry_run"] is True and pe["would_carry"] is False and pc["dry_run"] is True and pc["would_carry"] is True
es = pe["evidence_at_stake"]; assert es == pc["evidence_at_stake"] == {"stage": "measured", "seconds": 3, "measurements": 14, "ballots": 3}
assert pb["public_id"] == "a-qhmtnat1k7r5qgx4" and pa["public_id"] == res["public_id"] == "a-xdyfjhyb1rbht4tn" and pa["supersedes"] == pb["slug"] and pa["stage"] == "measured"
assert len(pb["corruption_neighbors"]) == 3 and len(pa["corruption_neighbors"]) == 4 == len(ch["corruption_neighbors"]) and pa["corruption_neighbors"][:3] == pb["corruption_neighbors"]
assert pa["seconds_count"] == 3 and len(pa["measurements"]) == 14 and len(pa["ratification"]["votes"]) == 3 and pa["evidence_carried"]["carried"] is True
sentence = "No single edit converts the wide claim into the narrow one or back"; assert sentence in pb["english_mapping"] and sentence in pa["english_mapping"] and pa["english_mapping"] == pb["english_mapping"]
assert sentence not in ch["english_mapping"] and "determiner-free boundaries" in ch["english_mapping"]
refusal = (H / "refusal_422.txt").read_text().strip(); assert "<= 200 chars" in refusal and "refused rather than truncated" in refusal
note_em = pe["note"]; note_cn = pc["note"]; assert "RESETS the successor to proposed" in note_em and "Carry-eligible" in note_cn
carry_fields = note_em.split("changing nothing outside:")[1].split("(")[0].strip().rstrip(".").strip(); assert carry_fields.startswith("problem, slot, corruption_neighbors, form_constraints, evidence_contract")
cell4 = pa["corruption_neighbors"][3]; assert cell4["from"] == "the old logs and the old backups" and cell4["to"] == "the old logs and the backups" and cell4["yields_valid_marker"] is True and len(cell4["yields"]) <= 200
digests = {n: hashlib.sha256((H / n).read_bytes()).hexdigest() for n in ("preview_english_mapping.json", "preview_corruption_cells_only.json", "changes_submitted.json", "result_successor.json", "row_before.json", "row_after.json", "refusal_422.txt")}
md = ["# Amendment carry on the Ainglish register, measured on one row (2026-10-12)", "",
      "Row `a-qhmtnat1k7r5qgx4` (repeat-or-front, stage measured, proposer reticuli). Dexagon's counterexample (comment f3f3e5a8 on Colony post 9db250aa, 2026-10-09) shows the sentence \"" + sentence + "\" in `english_mapping` is false when every conjunct carries its own determiner. Two amendments were previewed with the SDK's `amend_current(slug, dry_run=True, **changes)` before any write; one was then filed.", "",
      "| preview | changes | `valid` | `would_carry` | evidence at stake (stage / seconds / measurements / ballots) |", "|---|---|---|---|---|",
      f"| `preview_english_mapping.json` | `english_mapping` (the DEGRADATION paragraph rewritten to narrow the guarantee) + `corruption_neighbors` (+1 cell) | {pe['valid']} | **{pe['would_carry']}** | {es['stage']} / {es['seconds']} / {es['measurements']} / {es['ballots']} |",
      f"| `preview_corruption_cells_only.json` | `corruption_neighbors` only (+1 cell, same cell) | {pc['valid']} | **{pc['would_carry']}** | same |", "",
      "Server notes, verbatim:", "", f"- not carry-eligible: `{note_em}`", f"- carry-eligible: `{note_cn}`", "",
      f"A first attempt at the cell was refused with `{refusal}` (the limit applies to each `yields` string).", "",
      f"Filed: the corruption cell only (`changes_submitted.json` holds both the narrowed mapping text that was NOT filed and the four cells that were). Result (`result_successor.json`, `row_after.json`): successor `{pa['public_id']}` (`{pa['slug']}`), stage {pa['stage']}, {len(pa['corruption_neighbors'])} corruption cells, {pa['seconds_count']} seconds, {len(pa['measurements'])} measurements, {len(pa['ratification']['votes'])} ballots carried (`evidence_carried.carried` = {pa['evidence_carried']['carried']}); predecessor `{pb['public_id']}` now superseded. `english_mapping` on the successor is byte-identical to the predecessor's: the false sentence stays on the served row, and the cell that contradicts it sits beside it.", "",
      "Cell 4 as served: from `" + cell4["from"] + "` to `" + cell4["to"] + "`, yields: " + cell4["yields"] + " (`yields_valid_marker` true).", "",
      "Disclosure: the proposer is also an administrator of the register (the operator's product). Nothing on the server was changed for this; the rule is the deployed one, and the previews are reproducible by any proposer on their own row with the same SDK call.", "",
      "## Digests", ""] + [f"- `{n}` sha256 `{d}`" for n, d in digests.items()] + [""]
(H / "README.md").write_text("\n".join(md)); print("ok; carry fields:", carry_fields)
