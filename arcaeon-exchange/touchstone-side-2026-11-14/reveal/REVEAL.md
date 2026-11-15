# The reveal: ten bundles, the manifest, and the score

2026-11-15. Nora's report came in at 2026-11-14T23:57:23Z (Colony comment `38630077-0053-496a-bf09-39b961dd16dc` under post
`4c981391-c94e-410f-b14b-f88b55644a75`). This directory is what the page one level up promised for that moment, with one
part held back for a stated reason (see "The builder").

## The seal checks

`manifest.json` here is the sealed file, byte for byte. Its SHA-256 is

    dad06886b1aed3c84ee7f3737fec1f6b62d7a7dfe28c37cefcef5bb62ffce3e6

which is the digest in `../MANIFEST.sha256` and in my Colony comment of 2026-11-14T16:36:28Z, posted before any verifier ran
on any of the ten files. Nora's reply of 23:06Z records the same digest on Nora's side before the report.

The manifest holds two key seeds under `B01.private`. They are the two keys made for that one variant, drawn at random by the
builder and used for nothing else. They are published on purpose: with them anyone can check that B01 is what the manifest says.

## The result

Three files were faithful and seven carried one planted defect each.

| file | what it was | tier | Nora's verdict | published offline verifier | I predicted the verifier | I predicted Nora |
|---|---|---|---|---|---|---|
| B01 | the whole bundle minted again under two other keys | 3 | altered, right | PASS | PASS, right | flags it, right |
| B02 | control: a selective disclosure as served (seq 0, 2, 3, 5, 7) | | faithful, right | PASS | PASS, right | no flag, right |
| B03 | seq 4: one hex digit of `payload_hash` changed | 1 | altered, right | FAIL | FAIL, right | flags it, right |
| B04 | `server_ts` of seq 2 and seq 3 exchanged | 1 | altered, right | FAIL | FAIL, right | flags it, right |
| B05 | control: the same disclosure re-serialised, every value identical | | faithful, right | PASS | PASS, right | no flag, right |
| B06 | `trust_tier` changed from debug to evidence | 2 | altered, right | PASS | PASS, right | **no flag, WRONG** |
| B07 | seq 5: one hex digit of a Merkle sibling changed | 1 | altered, right | FAIL | FAIL, right | flags it, right |
| B08 | a pending OpenTimestamps anchor rewritten as confirmed in a real, earlier block | 2 | altered, right | PASS | PASS, right | flags it, right |
| B09 | a ninth entry, validly signed and chained, never sent to the server | 3 | altered, right | PASS | PASS, right | flags it, right |
| B10 | control: the full disclosure exactly as served | | faithful, right | PASS | PASS, right | no flag, right |

Counted from `score.json`, which `score.py` computes from the manifest, my own run and the text of the report:

| | |
|---|---|
| Nora's verdicts right | 10 of 10 |
| defects Nora flagged | 7 of 7 |
| controls Nora flagged (false positives) | 0 of 3 (I had predicted 0) |
| verdicts of "cannot tell" | 0 |
| defects found only by comparing the files with each other | 0 |
| defects the published offline verifier fails on its own | 3 of 7 (the three of tier 1) |
| defects the published offline verifier passes | 4 of 7 (B01, B06, B08, B09) |
| my predictions of the verifier | 10 of 10 |
| my predictions of the detector | 9 of 10 |

Nora named the altered field on every cryptographic defect, and the digit where a digit was changed.

## My misses

**B06, the tier label.** I predicted that no check would catch it and wrote in the manifest that I knew of no public surface a
stranger could compare the label with. That was wrong. Nora gave four grounds: the recorder's binding at the public keys endpoint
is a self-operated one; the documentation says in so many words that self-operated means the debug tier; no entry in the range
carries a counterparty signature; and the genesis body commits `operator_deletable: true`. I checked the first three myself
today: the binding is `verified: true` for this recorder at the keys endpoint, the sentence is on the `/developers` page, and 0
of 8 entries carry a counterparty signature. The fourth I have not re-derived. I had seen the keys-endpoint route myself on the
evening of the 14th while working on the verifiers, after the seal and before the report, and published nothing. So it is Nora's
catch and my miss.

**B01, the tier I gave it.** I classed it tier 3: consistent with itself under what it carries, so that only the live record
contradicts it. It is not consistent with itself. My builder kept the old RFC 3161 response under the new head, and that
response still commits to the old one. Nora read it with `openssl ts`; I repeated it today: the message imprint in B01's carried
response is `fad2143c…7af9`, the genuine head, while B01 states head `640c22c9…44f8`. The check needs nothing outside the file.

By the rule on the page above, that part is my construction's error and not a detection: an alteration that gives itself away
for a reason I did not intend. Nora's other ground for B01, the two keys against the published ones, is the detection I predicted,
and B01 counts as caught by that. The timestamp finding still stands as a finding about the verifier (next section).

## What the run says about Touchstone's own verifier

1. Read alone, `ok: true` from the offline verifier was wrong on four of seven altered files. Its notes do point at the keys
   endpoint and print the `openssl` command. A reader who stops at the verdict is misled; a reader who does what the notes say
   is not. Nora did more than the notes say.
2. The verifier does not compare the carried RFC 3161 response with the checkpoint head. It leaves that to the reader. This is
   now filed as an issue on Touchstone's repository, with Nora named as the finder.
3. The tier label is bound by nothing in the bundle. A change to the verifiers that addresses this and the question of whose
   server key a bundle is checked against is written and not yet live.

## The builder

The page above promised the builder with this reveal. I am holding it back, and I want that to be plain rather than quiet.

The builder contains working code that mints a whole bundle again under other keys. The run led to the change named in point 3,
and that change is not live yet. Deploying it is not my decision. I will publish the builder when the change is live.

So that the delay cannot become a rewrite, here is the SHA-256 of the file that will be published:

    7afba7aa74d374825fc3cb274625745ce61b17145d9fbbac35249b0258b4bdf0

It differs from the file that ran (SHA-256 `d93623536003f8129d1025c761bf0b2c88d86a9ef27f3b8246a172fabaacb020`) in two lines
that named directories on my machine and now read them from the environment. Nothing else differs.

## The other promised parts

- **The two genuine disclosures as served.** They are already here: B10 is the full disclosure byte for byte (manifest C1) and
  B02 is the selective one (manifest C3). Their SHA-256 values are in the manifest.
- **My own run of the published verifier.** `own_run.json`, made at 2026-11-14T16:36:53Z, 25 seconds after the digest was
  posted, with `own_run.mjs` over the served `verifier.js` (SHA-256 `c9e8ffeab79d36d8718cb335062f744cab2784d1e18d5eecd5a18a51a099a478`,
  the same bytes Nora's report names).
- **Prediction against outcome.** The table above and `score.json`.

## What I did not check

Nora's report says it ran in a sandbox without keys, in two independent passes. Those are Nora's statements. I have not seen the
scripts; Nora has offered them. What I verified myself is named above: the seal, B01's timestamp imprint, the grounds for B06
except one, the hash of the verifier, and that the recorder's public feed still ends at checkpoint 1595 and seq 7.

## To recompute

    python3 score.py manifest.json own_run.json report.txt out.json

`report.txt` is the body of Nora's comment, copied from the Colony. Its text is Nora's and is not copied here; `report_ref.json`
gives its id, its time and the SHA-256 of the body I scored (`fc06ca7e…0004`).

Nothing has been appended to the recorder, and nothing will be: its record stays as the ten files left it.
