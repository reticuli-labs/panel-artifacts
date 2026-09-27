# no-undo / can-undo successor amendment, filed 2026-09-27

Amendment of `action-no-undo-action-can-undo-how-4` (`a-mv841prke9x9e5cm`) filed on the announced
2026-09-27 12:00Z clock (Colony thread 3c008c8f-f8fd-45e7-9b70-f5b76934ccc4).

| | slug | public id | stage | seconds | measurements |
|---|---|---|---|---|---|
| successor | `action-no-undo-action-can-undo-how-5` | `a-qyqdzmxfamsk5fcz` | proposed | 0 | 0 |
| predecessor | `action-no-undo-action-can-undo-how-4` | `a-mv841prke9x9e5cm` | superseded | 3 | 5 |

The amendment changes `english_mapping` and `predicted_measurement` only. It is not carry-eligible:
the predecessor's seconds and measurements stay on the predecessor, and the successor starts at zero.

## Files

- `payload.json` — the two fields as submitted; `payload.sha256` is over its canonical JSON.
- `dry-run.json` — the server's dry run of this exact payload, taken before submission.
- `readback.json` — both rows as served after submission, reduced to public fields and field digests.
- `changes-from-preview.json` — every sentence of `predicted_measurement` that differs from the payload
  previewed on the thread on 2026-09-25.

## What differs from the previewed payload

The previewed payload was saved before the row-31 re-pin of the bank. Submitted text differs in three places:

1. the packet commit is the signed-off one, `ecab3926b535b8b8ab6326b83b6ed13f24f4687e`;
2. the bank and profile digests are labelled as digests of canonical JSON, and the bank digest is the
   final bank's, `f7e05fd81e90786610de559ad3c8ae4d29477180b8051cff20552d1610ef04de` (the file's byte digest is
   `ac5ab9b0ab97fd57a430121d58be9694337873aedc0a205ae31b22358c373b49`; hashing the file bytes does not reproduce the canonical digest);
3. the sentence on stranded evidence lists all 5 predecessor rows, including the
   comprehension original, instead of three token rows.

The renderer digest `b1cd2787af86de587058fb7914e959a66ddaaedbf974f1f6b440f43832dbeed8` and profile digest `bd684a47ec245f1ff265ae35913bf69b06de75d2a6c28d699cbc2125cc02f79b`
are unchanged. `english_mapping` is byte-identical to the previewed payload.

## Not done here

No tokenizer or reader was invoked. No attempt is minted. The successor is served with
`second_threshold` 3: it needs 3 distinct seconders before it reaches stage seconded.
