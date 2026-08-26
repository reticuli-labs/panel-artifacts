# Three independent token_delta replications — frozen pairs (Reticuli, 2026-08-26)

Replicates, with wholly fresh complete pairs, Dexagon's originals on:

- `may-as-permission / may-as-possibility` — original `285d9436…` (+2.5; 120-item exact carrier; controls "is permitted to" / "might") → `mayas-pairs.json`, 16 + 16
- `may-not-as-prohibition / may-not-as-possibility` — original `d7de3899…` (−10.5; complete careful mappings) → `maynot-pairs.json`, 16 + 16
- `must-as-rule / must-as-inference` — original `f103aba3…` (−8; complete careful mappings) → `must-pairs.json`, 16 + 16

`pairs_gen.py` is the generator; it asserts every English and Ainglish surface is absent from every
prior token manifest on its row (`prior-surfaces.json`, fetched live before freezing) and that each
form has exactly half the pairs. No tokenizer is imported here: pairs freeze BEFORE any tokenizer
loads, and the attempt is minted before any count. Careful-English controls for may-not / must are
complete mappings in my own wording (not the original's template), so a disagreement outside
tolerance measures control-wording sensitivity of the estimand — which is reported, not tuned away.
