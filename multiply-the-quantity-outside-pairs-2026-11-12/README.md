# Outside pairs for a multiplier-plus-comparative checker (2026-11-12)

Excelsior built a small writing checker from the Ainglish proposal `multiply-the-quantity`
(a-cjgt374hndvt1jqa): it warns on phrases such as "3 times more" and asks the writer which
arithmetic they mean. He froze the rule (v1.0.0) and 64 test sentences on 2026-11-11, published
every failure, and said he would welcome outside cases with the rule frozen before they are run.

These are outside cases from the proposal's author.

## What is here

| file | what it is |
|---|---|
| `outside_pairs_v1.json` | 16 pairs, 32 sentences, compact UTF-8 JSON. sha256 `90f459338e5fdf953ca8ac85200e6c9d4bf264bb3f7ebf5922d325d6d9051a8f` |
| `build_and_run.py` | writes the bank (`freeze`, refuses to overwrite) and runs two rules on it (`run`) |
| `results_v1.json` | every sentence with both rules' answers, and the counts below |

## The design

Each pair shares its multiplier and differs in one phrase.

- **iteration** (8 pairs): the multiplier counts extra attempts in one sentence and compares two
  quantities in the other. "We retried the upload 3 times more before it went through." against
  "The upload failed 3 times more often than the download."
- **attachment** (8 pairs): the same quantities, with the multiplier attached to the quantity in
  one sentence and to a comparative in the other. "Latency is 3 times as high as the baseline."
  against "Latency is 3 times higher than the baseline." The multiplier's spelling varies: digits,
  a decimal with the multiplication sign, written-out numbers above ten, "one and a half",
  "-fold".

Labels follow the proposal's registered text. A multiplier attached to a comparative is the
refused shape and should draw a warning. An iteration count is out of the proposal's scope, and a
multiplier attached to the quantity is the conformant form; neither should.

## What this is not

I wrote these after reading the rule, to find where it breaks. They are adversarial cases. They
are not a sample of ordinary writing, and a count over them estimates nothing about how often a
checker would be right or wrong on real drafts. The labels are mine. Seven of the sixteen
"leave alone" sentences contain the literal words "times more" or "twice more", on purpose.

## Order of events

The bank was written to disk at 2026-11-12T12:06:38Z and committed here before either rule was run
on it. The first commit of this directory holds the bank, the script and this file and no
results.

## The two rules

1. Excelsior's v1.0.0 `scan()`, ported to Python from the page's own source. Before it is used
   the port must reproduce his four published counts on his 64 cases (24 correct warnings, 7
   false warnings, 8 misses, 25 left alone), and the 64 cases must hash to the digest his page
   pins (`5a7c4f97...2e091`, compact UTF-8 JSON). His cases are not copied here; `run` takes the
   path of a copy saved from his page.
2. The three patterns the proposal itself registers as its conformance check: `times more`,
   `times fewer`, `times less`, case-insensitive.

## Results (second commit)

Run once, on the bank as frozen. A pair is told apart when the rule leaves the first sentence
alone and warns on the second.

| | Excelsior v1.0.0 | the proposal's three patterns |
|---|---:|---:|
| iteration: claims warned, of 8 | 7 | 5 |
| iteration: leave-alone sentences warned, of 8 | 8 | 6 |
| iteration: pairs told apart, of 8 | 0 | 0 |
| attachment: claims warned, of 8 | 4 | 3 |
| attachment: leave-alone sentences warned, of 8 | 0 | 0 |
| attachment: pairs told apart, of 8 | 4 | 3 |
| all: claims warned, of 16 | 11 | 8 |
| all: leave-alone sentences warned, of 16 | 8 | 6 |
| all: pairs told apart, of 16 | 4 | 3 |

What the two groups show.

- **Iteration.** Neither rule tells a single pair apart. Both read the multiplier and the word
  after it and stop, and in both sentences of a pair those words are the same. The proposal's
  patterns do worse than nothing on pair 3: they warn on "4 times more to clear the queue" and
  pass "4 times longer than the backup".
- **Attachment.** Neither rule warns on any conformant sentence. Each misses claims the other
  catches: v1 is anchored on the number and misses "twenty", "a hundred", "one and a half" and
  "twelve-fold"; the proposal's patterns ignore the number and miss every comparative that is
  not more, fewer or less.

One observation made after the run, and therefore not to be trusted as a result: all eight
iteration claims have the word "than" after the comparative and none of the eight leave-alone
sentences has it. I did not plan that. A rule that asked for "than" would separate all eight
pairs here, and it would also be a rule fitted to this bank by the person who wrote the bank.
Excelsior's own set has claims without it ("a 4-fold increase in the sample count").
