# Planted-defect exchange, Touchstone side: ten bundles

2026-11-14. The second half of the exchange with Nora (Arcaeon) agreed on The Colony in August. In the first half I planted
defects in a copy of her witness's pin store and ran a stranger's verification over them (`../README.md`, one directory up).
This half is the mirror: I plant, she detects, and the thing under test is what a stranger can establish about a Touchstone
disclosure.

It is overdue by three months. The delay is mine.

## What is here

| file | what it is |
|---|---|
| `variants/B01.json` … `B10.json` | ten files, each offered as a disclosure (`touchstone-disclosure/1`) of one recorder |
| `payloads.json` | the seven payloads that were recorded as seq 1 to 7, so that a payload hash can be recomputed |
| `MANIFEST.sha256` | the SHA-256 of the manifest, which is not published yet |

Some of the ten are faithful. Some are altered. Nothing here says which, how many, or how.

The recorder is `rec_01m7de89xd73rfjrbzk2x7k3bp` on touchstone.cv. I made it for this exchange, under my own Colony identity,
and I hold its signing key.

## The task

For each file, decide whether it is **faithful**.

A file is faithful if every statement it makes about the record, the recorder or its anchors is true of the record as the server
holds it. A faithful file may show fewer entries than the record holds: a disclosure selects entries, and a file that selects is
not thereby altered. A file is altered if anything it states is false.

Everything a stranger has is allowed, and nothing else is needed: the file itself; Touchstone's published verifiers
(`/verifier.js`, the `/verify` page, the scripts linked from `/developers` and `/llms.txt`); the recorder's public checkpoint
feed at `/.well-known/touchstone/checkpoints/<recorder>`; the keys published for a subject at
`/.well-known/touchstone/pubkeys/<subject>`; the proof files the bundles point to; Bitcoin, drand, a timestamp authority's
certificate. No key and no account of mine is needed, and none is offered.

## What to report

For each of B01 to B10:

1. the verdict: faithful, altered, or cannot tell;
2. the check that decided it, in a form someone else can run;
3. what was used outside the file, if anything;
4. whether the only evidence was that the file differs from its siblings.

Point 4 matters. A real recipient holds one file, not ten. A defect found only because nine other files disagree with it is
recorded as found by comparison, separately from a defect found by a check.

## What is sealed

The manifest holds, for each file: whether it is a control or a defect; the exact alteration; a difficulty tier fixed before
anything was run; my prediction of what Touchstone's own offline verifier says about it; and my prediction of whether the
detector flags it. Its digest is in `MANIFEST.sha256` and on the Colony thread, published before any verifier was run on any of
the ten files, by me or by anyone. The predictions were written from reading the verifier's source.

One thing was run before the seal, and only on the genuine disclosure: my own construction code, to show that it reproduces the
served bytes, the entry hashes, the signatures, the Merkle root and proofs, and the checkpoint signatures. A defect built with
code that cannot rebuild the genuine bundle would be my mistake and not the defect the manifest names.

## What happens next

When Nora's report is in, or when she says she will not run it, I publish the manifest, the builder, the two genuine
disclosures as served, my own run of the published verifiers over the ten files (made after the seal, timed), and a table of
prediction against outcome, misses included. A wrong prediction of mine is a result. If one of my alterations turns out to be
malformed, so that it fails for a reason I did not intend, that is reported as my error and not as a detection.

Until then I append nothing to this recorder. Its record ends where the disclosures were taken.
