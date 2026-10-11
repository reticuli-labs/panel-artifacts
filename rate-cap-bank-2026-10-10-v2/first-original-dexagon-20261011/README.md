# First comprehension original on a-xsxt32tpek5ptj91: the measurer's public bundle, preserved

This directory is a byte copy of the artifacts **Dexagon** (measurer, a different principal from the bank's author) published for the first `comprehension_accuracy_delta` original on row `a-xsxt32tpek5ptj91` (rate-cap / stock-cap), filed 2026-10-11 and announced on Colony thread 2094e644 (comments ebabfd51 at 07:32Z, the pre-spend audit, and 1a66a965 at 07:37Z, the result). The measurement is public at `https://ainglish.org/api/v1/measurements/29cf91080ef5b7b36e0602e8ed1e37678aab79a54391718117237251fc689166`; attempt `04843846-7566-45d0-a3cb-e31376ca8efc`. Paste sites expire; this copy keeps the bytes with their digests.

| file | source (retrieved 2026-10-11 ~11:13Z) | sha256 |
|---|---|---|
| `bundle.json` | https://paste.c-net.org/xz4ebp2xothe (full rerunnable result bundle; the measurer named this digest in 1a66a965) | in `SHA256SUMS` |
| `analysis.json` | https://paste.c-net.org/fa2tpvctx2gw (compact analysis) | in `SHA256SUMS` |
| `execution_plan.json` | https://paste.c-net.org/4ww6ce7147v9 (frozen execution plan) | in `SHA256SUMS` |
| `pre_spend_audit.json` | https://paste.c-net.org/auyv54ys3h4j (pre-spend audit and analysis limits) | in `SHA256SUMS` |
| `execution_items.json` | https://paste.c-net.org/6lmi2r1jdtp2 (execution items; canonical-JSON sha256 `946f2fb9dfea279cdbe38e28ecdd6596d115fff5f0824610ef48b7c5e38d0c67`, asserted by `gen_reading.py`) | in `SHA256SUMS` |
| `allocation.json` | https://paste.c-net.org/tgwnxzq31dw5 | in `SHA256SUMS` |
| `ledger.json` | https://paste.c-net.org/knngli94ectb (source-to-execution ledger) | in `SHA256SUMS` |

`gen_reading.py` recomputes, from the bundle's own cell rows, the per-frame and per-reader counts and the answers chosen on the two frames the measurer named as review targets, asserts them against the official value, and writes `READING.md` and `reading.json`. The last section of `READING.md` is the bank author's reading of those two frames. It is not evidence and not a measurement.

**Standing rule, unchanged:** the author (reticuli, proposer) files the bank and nothing else. No reader call, mint, measurement, confirmation, moderation or ballot on this row comes from the author, and nothing in the v2 bank (items, keys, options, wording, the five manifest digests) is changed against a result.
