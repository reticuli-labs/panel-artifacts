# The frozen item file and the as-run manifest are not the same bytes

Found while preparing the filing, and worth stating plainly because it is a defect in my own
process rather than a curiosity.

`gun_panel_items.json` (committed at the freeze, `3c3da66`) hashes to `a8106ea5…`.
`items-as-run.json` — the item array actually carried by the manifest the panel executed, extracted
verbatim from the result receipt — hashes to `85ed9cd2…`.

## What differs

Exactly two fields, on all 54 items:

| field | frozen | as-run |
|---|---|---|
| `form` | populated (e.g. `'calibration'`) | absent |
| `behaviour` | populated (e.g. `'silent'`) | absent |

These are the **design stratification labels** — the 12/12/12/12 form × behaviour grid the item set
was authored against.

## What does NOT differ

Every answer-bearing field, on every item: `english`, `ainglish`, `question`, `options`, `answer`
are byte-identical across all 54. Checked explicitly, not assumed — the comparison is in the
session log and reports `NONE`.

So the experiment that ran is the experiment that was frozen. `comprehension_accuracy_delta` is
computed from the arms and the answer key; it does not read `form` or `behaviour`, and this panel
declares no `settlement_stratum`. The measurement is unaffected.

## Why it happened, and the actual lesson

The authoring script emitted the design labels into the frozen artifact but the manifest assembled
for the run never carried them. My runner asserted `sha256(manifest['items'])` against a constant
I had taken **from that same manifest** — a self-consistent check that pinned the manifest to
itself and could never have caught this. The freeze exists to bind the run to the *published*
bytes, and my assertion did not do that.

The fix for next time is one line in the wrong place: the runner should verify against the
**committed artifact's** digest, ideally via `panel.fetch_items(url, pinned_sha256)`, which
verifies twice — the artifact's own embedded digest and the caller's pin — rather than against a
constant copied out of the object under test.

Because the receipt pins `items_sha256 = 85ed9cd2…`, the filing references `items-as-run.json`,
which is what a replicator must fetch to reproduce this run. The frozen file is retained unchanged
alongside it; nothing is rewritten to make the mismatch disappear.
