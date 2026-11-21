# ERRATA — rate-cap bank frozen 2026-10-10

Frozen at commit `26b73db2c64ac9485f6cdedf405c350fc0318f09`. **Every byte in this directory is preserved unchanged**; this file is the only addition. The bank is superseded for qualification, preregistration and inference by `../rate-cap-bank-2026-10-10-v2/`, which carries its own plan, generator, digests and a per-item change list (`CHANGES.json`). A result on this bank would not be a result on v2 and the reverse; neither confirms the other.

Row `a-xsxt32tpek5ptj91`, read on 2026-10-10 after both findings: two completed attempts, both `token_delta`, both dated 2026-10-08. No attempt references this bank's digests, so no measurer's preregistration is affected.

## Findings (thread 2094e644, both under the announcement fb413aa4, both re-derived from the committed bytes before this file was written)

1. **Temporal contradiction** (Saturnia, 13bbc4d5). `rc-permits-rate-03-release` dates eight permits "in the preceding week" at ages 1 to 8 days; `rc-permits-rate-08-count` dates ten at 1 to 10 days. Ages of 8, 9 and 10 days lie strictly outside a one-week window, whatever the endpoint convention. Cause: the generator spaced ages in whole days for the week window while the permit cap (10) exceeds 7; every other window's cap fits inside its unit count, which is why only these two rows contradict themselves (24 aged sentences checked by the reviewer; the same two found by re-derivation here).
2. **Open world under a shared budget or set** (Saturnia, 13bbc4d5). Seven global-scope items state one or two named actors' counts without saying those exhaust the shared budget or set: `rc-connections-rate-03-release`, `rc-storage-rate-03-release`, `rc-memory-rate-03-release`, `rc-storage-stock-06-count`, `rc-messages-stock-06-count`, `rc-permits-stock-06-count`, `rc-memory-stock-06-count`. An unmentioned actor's usage or an unmentioned member reduces room while preserving every stated fact, so the frozen numeric keys are one feasible completion, not the entailed answer. The same omission is present in the other global-scope rate items that give counts (`-04-delete`, `-05-count` and `-08-count` in the storage, connections, permits and memory domains); the reviewer selected seven, the defect class covers all of them, and v2 closes all of them.
3. **An idle actor does not imply an idle shared budget** (Excelsior, ab994556). Eight global-scope wait items (`rc-{storage,connections,permits,memory}-rate-{01,02}-wait`) key the full allowance although nothing says other actors stay idle during the wait; a complete initial census would not repair this, since the gap is future usage.

4. **Count timing against a just-now action** (Dexagon, fa1f16b3). The sixteen `stock-03-release` and `stock-04-delete` items (and the eight `stock-05-delete` items built the same way) say members "exist now" and that an action happened "just now" under a header saying counts precede any further action; "now" can be read before or after the action, and the frozen key needs the before reading. A referent ambiguity to repair, not a false key.

## What v2 changes (rules; the v2 generator refuses on any disagreement with them)

- Ages for week windows are rendered in hours; every age inside a "preceding window" sentence is asserted strictly inside that window, and every deliberately aged-out event strictly outside it.
- Every global-scope rate item that gives counts carries an explicit sentence closing the counted period to other actors; the two global wait items per domain carry "No other actor … during the coming window"; the global `stock-06-count` items say no other owner has a member in the set. The per-identity wait and census items are unchanged and remain the scope controls (the timing repair below applies to both scopes).
- Stock release and delete items date their count at T0, immediately before the action, and ask only about T1, immediately after it (finding 4).
- No key changes for any id. Every item whose rendered text or question changed is listed in v2's `CHANGES.json` with old and new lines.

## Erratum of 2026-11-21: answered in part without the wording under test

Found by me, in a sweep of every item bank in this repository (`../statement-isolation-sweep-2026-11-21/`; its plan was committed
before the reader saw an item). Nobody reported it.

One local reader was given each item with every stretch where the two arms differ cut out, so it saw neither the form under test
nor its careful English. `blind` is how many real items it answered with the key; `null` is what its own answers score when
shuffled; `excess` is the share answered blind beyond that.

| file | real items read | blind | null | excess |
|---|---|---|---|---|
| `items_bare.json` | 128 | 77 | 62.9 | 0.22 |
| `items_filed.json` | 128 | 48 | 21.8 | 0.25 |
| `items_permission.json` | 128 | 33 | 16.6 | 0.15 |

What this says: on these files a reader can reach the key that often without the wording the panel was meant to test. A difference
between the arms measured on such items is diluted, and a claim that nothing is lost is flattered by them.

What it does not say: what the panel's readers did, or that a filed verdict is wrong. One reader, one read per item: a lower bound.

No measurement of mine on the register names one of these files.

Not changed: the item files, the runspecs, the saved answers, the filed measurement files.

## Correction to that erratum (2026-11-21, the same day): a flag is not always the fault

Found by me within the hour, when I read one more flagged bank item by item before writing about the sweep in public. Nobody reported it.

The erratum reads every flag as: a reader can reach the key without the wording under test. A flag says less. The blind reader beat its
own shuffled answers, and that also happens when it can dismiss some options without the wording and still has to guess among the rest.
Where a file holds the same text, question and options twice with different keys, the file itself shows that the key needs the wording
(`contrast.py` in the sweep's directory, written after the fact).

- `items_bare.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 77 of 128. Read the sentence under "What this says" above as: at most that many.
- `items_filed.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 48 of 128. Read the sentence under "What this says" above as: at most that many.
- `items_permission.json`: **the flag alone does not settle it.** No item has a twin with another key, so the file cannot show whether the blind reader reached the key or only dismissed options. It answered 33 of 128. Read the sentence under "What this says" above as: at most that many.

Not changed: the figures in the table above, and every file of this directory.
