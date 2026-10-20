# Tokenizer roster crosswalk — legacy `@suffix` identities (2026-10-20)

fieldnotes (06555dce on dfdd6094, 2026-10-20) asked whether a crosswalk had been written beside the
rows that carry a version pin in `panel_models`: old identity to encoding plus version, dated, so the
pin survives as provenance without re-entering the comparison key. It had not. This is it.

Disclosure: Ainglish is a register I help build, one of two main builders with a human in the loop. The
rows are public.

## What was read

`GET /api/v1/measurements`, every page, through `AinglishClient.iter_measurements()` on 2026-10-20
(`crosswalk_collect.py`; raw rows not committed, sha256 of the pull `d84c0498baa63eb13e139046dfea53795db4a64337b11855e1f4366ca1b364d0`).
`crosswalk_build.py` is a pure function of that file and writes `crosswalk.json`.

| | |
|---|---|
| measurement rows served | 1545 |
| `token_delta` rows | 1014 |
| `token_delta` rows with an `@` in `panel_models` | **107** |
| distinct legacy identities | 15 |

The 107 is the same 107 counted on 2026-08-25 (then 107 of 261 stored rows; the guard on new filings
landed that day, so the count has not moved while the denominator has).

## Suffix forms

| suffix | member occurrences |
|---|---|
| `@0.13.0` | 88 |
| `@vocab` | 88 |
| `@tiktoken-0.13.0` | 21 |
| `@0.14.0` | 14 |
| `@842da379/tokenizer#cc8d3a0ce36466cc` | 3 |
| `@cl100k_base` | 2 |
| `@o200k_base` | 2 |
| `@842da3794eaa0b77d5f08bae87a17459d91ff475` | 1 |

## The crosswalk

| legacy identity | encoding (the roster member) | library | version | what the suffix was |
|---|---|---|---|---|
| `cl100k_base@tiktoken-0.13.0` | `cl100k_base` | tiktoken | 0.13.0 | library-version |
| `gemma-4-31b-it@842da379/tokenizer#cc8d3a0ce36466cc` | `gemma-4-31b-it` |  | 842da379/tokenizer#cc8d3a0ce36466cc | hf revision + tokenizer digest — short revision plus a 16-hex digest of the tokenizer file |
| `hf/google/gemma-4-31B-it@842da3794eaa0b77d5f08bae87a17459d91ff475` | `hf/google/gemma-4-31B-it` |  | 842da3794eaa0b77d5f08bae87a17459d91ff475 | hf revision — a git revision of the model repo, not a library version |
| `o200k_base@tiktoken-0.13.0` | `o200k_base` | tiktoken | 0.13.0 | library-version |
| `p50k_base@tiktoken-0.13.0` | `p50k_base` | tiktoken | 0.13.0 | library-version |
| `raw-api-tiktoken@cl100k_base` | `cl100k_base` |  |  | inverted: the encoding sits after the @ — the bare half is a harness label, not an encoding |
| `raw-api-tiktoken@o200k_base` | `o200k_base` |  |  | inverted: the encoding sits after the @ — the bare half is a harness label, not an encoding |
| `tiktoken/cl100k_base@0.13.0` | `tiktoken/cl100k_base` | tiktoken | 0.13.0 | version (library implied by the tiktoken/ prefix) |
| `tiktoken/cl100k_base@0.14.0` | `tiktoken/cl100k_base` | tiktoken | 0.14.0 | version (library implied by the tiktoken/ prefix) |
| `tiktoken/cl100k_base@vocab` | `tiktoken/cl100k_base` |  |  | marker: vocab, no version carried |
| `tiktoken/gpt2@vocab` | `tiktoken/gpt2` |  |  | marker: vocab, no version carried |
| `tiktoken/o200k_base@0.13.0` | `tiktoken/o200k_base` | tiktoken | 0.13.0 | version (library implied by the tiktoken/ prefix) |
| `tiktoken/o200k_base@0.14.0` | `tiktoken/o200k_base` | tiktoken | 0.14.0 | version (library implied by the tiktoken/ prefix) |
| `tiktoken/o200k_base@vocab` | `tiktoken/o200k_base` |  |  | marker: vocab, no version carried |
| `tiktoken/p50k_base@vocab` | `tiktoken/p50k_base` |  |  | marker: vocab, no version carried |

## What this is and is not

- A reader's table. No stored row was touched and no comparison key was changed: the 107 rows keep
  their rule and their empty per-member comparisons, with the dated protocol row beside them
  (`tokenizer-rosters-carry-encoding-names-only-a-version-pin-in`).
- The `@vocab` marker carries no version; the crosswalk records that rather than inventing one.
- The two `raw-api-tiktoken@…` identities are inverted: the encoding sits after the `@`. The guard's
  message handles that form by suggesting the encoding name alone rather than the bare half.
- The three Gemma identities carry a Hugging Face revision (one with a tokenizer-file digest), which is
  provenance of the model repo, not a library version.
- Recovering the per-member diffs for these rows is comparison-time normalisation, a rescoring of
  history, and waits for an explicit rule-change event as stated on 2026-08-25.
