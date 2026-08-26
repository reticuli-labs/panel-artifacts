# Per-reader qualification on the approx(N) development set — 2026-08-26

Each candidate reader ran ALONE (1-reader panel, `panel_neff: 1`) on the approx(N) cold-read development
set (8 real + 4 planted-effect calibration items, seed 7, never filed), so the harness's planted-effect
gate (min gap 0.5) is applied PER READER rather than at panel level. Harness: panel worktree at
ai-nglish/ainglish#89 head `9f94d30` (stamps as the installed 0.2.35). Credentials unset; nothing filed.

| reader | planted arm | other arm | gap | verdict |
|---|---|---|---|---|
| qwen35-27b-q4 (qwen3.8:27b, reasoning off) | 1.00 | 0.00 | 1.00 | QUALIFIED |
| gemma4-31b-q4 | 1.00 | 0.00 | 1.00 | QUALIFIED |
| ornith-35b-q4 | 1.00 | 0.00 | 1.00 | QUALIFIED |
| qwen25-7b-q4 | 1.00 | 0.00 | 1.00 | QUALIFIED |
| llama31-8b-q4 | 1.00 | 1.00 | 0.00 | REFUSED |
| llama31-8b-fp16 | 1.00 | 1.00 | 0.00 | REFUSED |

Why the Llamas fail: the English calibration arm says "exactly N" and the later finding is off by a
tenth, so its correct answer is "Yes — the sentence claimed the precise figure"; the gate scores the
PLANTED key ("No — the sentence allowed for that") in both arms. Llama chooses the planted key in the
English arm too — it does not read "exactly" as strict — so it cannot serve as a reader for this
construct at either precision. Earlier panel-level passes (3-reader other=0.333, 5-reader other=0.2)
were exactly one reader at 1.0 carried by the rest. Consequence: `llama31-8b-q4` is removed from every
staged roster; three-reader rosters take `ornith-35b-q4` in its place; five-reader rosters drop to four
with `panel_neff` 3 (the two Qwens share a lineage).

`out-<reader>.json` are the harness's own outputs (refusal receipts or dry measurements); `dev-<reader>.json`
are the exact single-reader manifests.
