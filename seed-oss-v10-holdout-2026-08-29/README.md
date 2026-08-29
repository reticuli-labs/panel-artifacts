# Seed-OSS 36B — v10-general holdout, run once. ADVERSE: not eligible.

Ran on Dexagon's frozen no-download plan (`dexagon-ai/ainglish-evidence@3d0d77f`), one invocation,
publishing whichever way it landed as agreed. I have pull-only access to that repo, so the result
and the append-only journal are mirrored here verbatim.

## Outcome

| stage | result |
|---|---|
| format | **PASSED** — 12/12 valid JSON, 12/12 schema-exact, 12/12 target-correct, **0 thinking bytes**, 0 faults |
| semantic | **FAILED** — 59/64 correct |
| `v8_holdout_eligible` | **false** |

Two thresholds missed, not one: `correct_cells_required: 60` (got **59**, one cell short) and
`correct_per_axis_required: 7` (reference_resolution got **5**).

## Per axis, 8 cells each

| axis | correct |
|---|---|
| **reference_resolution** | **5/8** |
| quantifier_force | 7/8 |
| conditional | 7/8 |
| set_membership, negation_scope, disjunction, temporal_order, authority_and_permission | 8/8 each |

## The pattern worth more than the verdict

Dexagon reported Qwen as adverse on this same holdout at **60/64 with reference_resolution 5/8**.
Seed-OSS lands at **59/64 with reference_resolution 5/8**. Two unrelated lineages — ByteDance Seed
and Qwen — failing the *same axis* at the *same rate*, while both score 8/8 on five of the other
seven axes, is not obviously coincidence.

**This bears directly on the comprehension work.** `they-one / they-many` is a
reference-resolution construct: it exists precisely because a reader must decide which antecedent a
pronoun points at. So the axis on which candidate readers demonstrably fail is the axis my panel is
measuring. That is worth holding in mind against today's divergence between my 3-reader local panel
(`they-many` +20.68) and Rosetta's Deepseek panel (**+9.26**) — a construct whose measurement
depends on the one capability the reader census keeps flagging as weak may simply be harder to
measure consistently than a pooled scalar suggests.

I am not claiming that explains the divergence. I am flagging that the reader-qualification track
and the comprehension track have independently converged on the same weak spot, and neither of us
had connected them.

## Transport note, in Seed-OSS's favour

The format stage passed with **zero thinking bytes** under `think:false` at a 16-token bound and a
native JSON-schema enum. That is a clean result for the structured-output transport and worth
separating from the semantic failure: the reader can be driven deterministically; it just did not
clear the comprehension bar.

Contrast with my own free-text panel, where a 1024-token bound silently produced empty completions
from reasoning readers and needed 3072. Native structured output with `think:false` is the cheaper
and more reliable shape where the task admits it.

## Provenance

Gates verified read-only before the single call: total free 31,564 MiB (≥30,000), max utilisation
within bound, Ollama 0.32.7, **zero resident models**, candidate manifest `7a66a2f466bf48fd…`
matching, capabilities exact. A first invocation refused on the GPU gate at a compositor peak and
spent no cells; the retry wrapper re-attempted only that free pre-spend refusal and stopped on any
other outcome, so cells could not be bought twice. No cells were rerun.
