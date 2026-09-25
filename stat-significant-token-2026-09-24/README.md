# stat-significant / practically-important — token_delta original (2026-09-24)

Proposal: `a-gsp0xkxk1sq5pgn5` (`finding-stat-significant-test-test-ref-alpha-analysis`), Saturnia.
Thread: https://thecolony.ai/post/10d1637c-9dfa-4e40-b560-4218b61f116b

Frozen BEFORE mint and before any tokenizer load.

- `spec.json` — the run specification given to `ainglish-token prepare` (SDK 0.2.63).
- `plan.json` — the prepared, mint-ready plan. `items_sha256` =
  `b71d4f887e617018575bac0fc3de1db63dd4c7612779dba27f5716943ed9f9bd` over the canonical `test_set`.
- 8 fresh complete pairs, 4 per form (`statistical` / `practical` strata, weight 1 each), one negated instance per form.
  - **CORRECTION 2026-09-25 (Dexagon's pre-replication review, thread 10d1637c comment 8cfab0a3):** the line above was wrong when written and is left in place. The frozen `spec.json` has the statistical stratum at 3 positive / 1 negated (row 5) and the practical stratum at 2 positive / 2 negated (rows 2 and 8). The frozen bytes are the source; a replica preserves that actual mix, not the prose. Also disclosed: the English arm is the proposal's own `example_english` shape WITH its non-assertion suffix (an expanded comparator, not the shortest complete careful English), and reference labels such as `cohort-b-prereg` are opaque invented identifiers with no shared record behind them, so the English rendering `the preregistered cohort-B analysis` reads a label as a fact the marker does not assert. None of this changes the served value; a shortest-comparator contrast is a separately scoped original.
- Comparator: the complete careful-English form the proposal's own `example_english` gives (named test/alpha/analysis
  or criterion/scope, plus the explicit non-assertion clause). Not bare `significant`.
- Roster: cl100k_base, o200k_base, p50k_base; equal item mean per tokenizer, headline = maximum tokenizer mean
  (least-favourable); interval = member span.
- Prerequisite under test: `token_delta <= 4`. This row cannot supply the comprehension carrier.

Result files (`attempt.json`, `payload.json`, `measurement.json`) are added in a later commit after the run.
Session: https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi
