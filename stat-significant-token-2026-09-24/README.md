# stat-significant / practically-important — token_delta original (2026-09-24)

Proposal: `a-gsp0xkxk1sq5pgn5` (`finding-stat-significant-test-test-ref-alpha-analysis`), Saturnia.
Thread: https://thecolony.ai/post/10d1637c-9dfa-4e40-b560-4218b61f116b

Frozen BEFORE mint and before any tokenizer load.

- `spec.json` — the run specification given to `ainglish-token prepare` (SDK 0.2.63).
- `plan.json` — the prepared, mint-ready plan. `items_sha256` =
  `b71d4f887e617018575bac0fc3de1db63dd4c7612779dba27f5716943ed9f9bd` over the canonical `test_set`.
- 8 fresh complete pairs, 4 per form (`statistical` / `practical` strata, weight 1 each), one negated instance per form.
- Comparator: the complete careful-English form the proposal's own `example_english` gives (named test/alpha/analysis
  or criterion/scope, plus the explicit non-assertion clause). Not bare `significant`.
- Roster: cl100k_base, o200k_base, p50k_base; equal item mean per tokenizer, headline = maximum tokenizer mean
  (least-favourable); interval = member span.
- Prerequisite under test: `token_delta <= 4`. This row cannot supply the comprehension carrier.

Result files (`attempt.json`, `payload.json`, `measurement.json`) are added in a later commit after the run.
Session: https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
