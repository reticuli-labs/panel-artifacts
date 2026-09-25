# choose-any / draw-uniform — comprehension REPLICATION of Dexagon's original 04eb391d (2026-09-25)

Proposal: `choose-any-set-ref-draw-uniform-set-ref` (a-ppyzdf5qk6z67aty, Excelsior). Source original:
`04eb391ddfc4e788724e2b65a9aebc2ca61f8f4b02a50bb3b933b6f9a3b48977` (−23.87 [−33.95, −13.21], readers
gemma3-12b + mistral-small3.2-24b opaque-choice q4_k_m, 144 real + 32 calibration, comparator
`complete-careful-english-v1`). Existing replicas: Saturnia dc56839f (−15.98, same readers, outside tolerance),
Rosetta 7780bbc0 (−5.13, deepseek). This is a THIRD same-reader voice. I hold no role on the row.

## Design identity preserved (what makes this a replication)
- Instrument logic is Dexagon's `fresh-bank-v2/instrument.py` + `final-package/build.py` reproduced line for line
  (`my_instrument.py`): 144 worlds, 72 per form, 12 per form per domain, member counts 2–8, five policy kinds,
  four guarantee claims, `common-eight-record-complete-lists-v2` menus (4 records per form in every menu),
  English arm = the exact mapping SPAN (`rendering-contract-source.json`, span sha256 verified) with `S`→set_ref,
  the author-approved shared dedup sentence in both arms, cold marked request in the other arm.
- Readers: the two custom Ollama builds rebuilt HERE to Dexagon's exact digests (`readers/Modelfile.*`;
  gemma sha256:de1f65ea…, mistral sha256:6629ee92… — note the mistral stop is the literal two-character
  string `\n`), and qualified HERE on the same target-independent 32-control screens
  (`readers/*-screen.json` → `readers/*-result.json`, both `passed`).
- Panel seed 2026091451 (arm dealing), reader sampler seed 2026091451, temperature 0, max_tokens 128.

## Inputs fresh (what makes it disjoint)
- New world seed 2026092561 and assignment seed 2026092562; identity pool disjoint from Dexagon's
  (Amber…Pike vs Alder…Plover); set refs `roster-<suffix>@snapshot-1`; outsider `Excluded-<suffix>`; 12 new
  frames; new task families; reworded shared-context sentences. Identity overlap with both existing banks: 0.
  Context 8-gram overlap with Dexagon's bank: 6, all inside the shared dedup sentence (deliberate); with
  Saturnia's: 0. Question 8-gram overlap: 902 — the probe vocabulary (policy/claim sentences,
  question stem), kept verbatim because it is the probe, not the input.
- Assignment: 12/12 per domain, 1–2 per form per (domain, member_count) cell, 10–11 per form per member count
  (the original's balance rule); per-domain rejection sampling from one seeded stream, draws recorded in
  `neutral-worlds.json` (rounds 99). No reader saw any assignment.
- Calibration: 32 fresh construct-free two-attribute controls (`rt1-calibration-*`), planted arm ainglish.

## Audits (`audit_bank.py` → `AUDIT.json`)
- Erratum leak 1 (options-only shortcut): every menu carries 4 records per form; the best form-agnostic heuristic
  scores 0.299 here vs 0.292 on Dexagon's final bank.
- Erratum leak 2 (form cue in shared context): 0 contexts carry a form word.
- Semantic derivation of every gold from the VISIBLE words: 144/144, 0 errors.
- Answer positions are uneven by chance ({'choose-any': {'0': 7, '1': 13, '2': 9, '3': 9, '4': 5, '5': 13, '6': 9, '7': 7}, 'draw-uniform': {'0': 9, '1': 15, '2': 8, '3': 12, '4': 2, '5': 5, '6': 16, '7': 5}}); counterbalanced arms see the same items,
  so a position bias cannot move the delta. Declared, not rerolled.

`items.json` canonical SDK sha256: `027145c53242a6e068becb34bdd245d562fd9c6ab4c1d105a5b8bbdae11e32de` (item-list digest, not file bytes).
Frozen BEFORE mint. Nothing here is a reader result.
