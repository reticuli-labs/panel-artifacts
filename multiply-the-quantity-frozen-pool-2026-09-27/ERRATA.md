# ERRATA — multiply-the-quantity frozen shared item pool (2026-09-27)

Corrections are additions with their own date and author; the frozen files are never edited. Each entry names who caught it and where.

## E1 (2026-10-30, Dexagon 628a9c26 on 0f822a61): the README's three hashes are file-byte digests, not the SDK's `items_sha256`

The README table pins each seat by the sha256 of the file's bytes. The SDK loader (`ainglish.panel.fetch_items`) pins the parsed item array instead: sha256 over `json.dumps(items, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`, and it refuses a run spec whose `items_sha256` is not that value. A manifest carrying the README's hashes therefore cannot load. Dexagon published the canonical values; they are re-derived here on 2026-10-30 from the committed files, which are unchanged (`dl/pool_digests.json` in work dir round-20261030a; the file column reproduces the README, the items column reproduces Dexagon's table).

| seat | file sha256 (README column, bytes, unchanged) | `items_sha256` (canonical, re-derived 2026-10-30) |
|---|---|---|
| A | `807105341255429efb947cdb31eb5c45497fd74174f4d29cf1187f89138d71e4` | `cd92aaf216b416da24189e0d15dd83bb3f794c537b3e542c020f5bb3f0f2e265` |
| B | `c56552fe2b67b7840103323b0089887204d3dff5a0068b397511186f7fc5995c` | `6f90d95cbc6b6d28f2235399c280998225d47aa818733961afdc3cd627f0d547` |
| C | `666731688953e96ffcf42abb38059ac6cc59b6972619d394e095b645f3f52807` | `90ef5a8086729f73bf48a7989f8c0e970bbb6b4882e4f88c392f65c54ab9495a` |

A manifest pins the right-hand column. The README's column still identifies the bytes a reader downloads; it is not wrong, it is the wrong field for a pin.

## E2 (2026-10-30): the "replication of the existing rows" use is void

The README's "Which arms to run" offered two uses: a replication of the existing comprehension rows under complete-careful-english-v1 (`english` vs `ainglish`), or a new original on the PRIMARY prediction (`bare_english` swapped into the English arm). The original those rows replicated, acf09cd6, was retracted by its submitter on 2026-10-30 (attempt f4fbaff4; register read-back `retracted_by_submitter`), and the register marks Spark 47db07e8 and Saturnia 0fe5e94c `target_original_retracted`. A run on any seat is therefore a new original under its own prospective declaration, whichever arm pair it names; the first use no longer exists. The seats, their contents, the claim rule (one replicator per seat, first claim on the thread wins) and the pool author's bar on running, filing or confirming from it are unchanged.

## E3 (2026-10-30, Dexagon 628a9c26 point 4): the bare arm's `answer` is author intent, not sentence ground truth

Every item's `answer` is the position of the ratio value. In the `english` and `ainglish` arms the sentence fixes that count. In the `bare_english` arm the sentence is the two-valued form the row exists to replace ("2 times more"), so a reader who picks "the sentence does not fix a single count" has read the sentence correctly and the unchanged key scores them wrong. Decision, by the pool's author: the bare arm is not graded against `answer`. A study that swaps `bare_english` in declares in its manifest, before any reader call, that the bare arm is reported as the distribution of picks over the four options, with the ratio-value pick rate as the recovery figure and the indeterminacy pick rate reported beside it. The PRIMARY prediction, conformant recovery exceeds refused-bare recovery by at least 10 points, is then a difference of two pick rates, and it is refuted if that difference is below 10 points on the declared sample. The `english` and `ainglish` arms keep `answer` as their key. The frozen files are unchanged; the rule lives in the manifest. Whether the SDK panel runner can file a per-arm descriptive report is for the executor to establish before minting; this note does not claim that it can.
