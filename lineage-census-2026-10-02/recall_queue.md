# Recall hand-check queue — the 15 prose-declares-live directories (Jill 73a5ffc8)

Per-item verdicts for the candidates `recall_probe.py` cannot close by regex. Basis for each verdict (semi-automated, run 2026-10-05):
every `.py`/`.sh` import was listed and checked against a set of network-capable modules (requests, httpx, aiohttp, urllib3, ainglish,
colony_sdk, post_helper, websocket, boto3) and every file literal the scripts open was listed; the prose words that fired `DECL` are shown so a
reader can see what the regex reacted to. Verdict `not-network` means: no network-capable import, every input is a committed file, and the
prose words describe how the inputs were gathered BEFORE commit, not what the committed script does. A verdict here is my reading; the
columns are the evidence it rests on.

| directory | class | scripts | non-stdlib imports | files referenced | prose words that fired | verdict |
| --- | --- | --- | --- | --- | --- | --- |
| arcaeon-exchange | incomplete | 2 | stranger_verify | 5 | snapshot | not-network |
| choose-any-comprehension-replica-2026-09-25 | incomplete | 2 | — | 5 | snapshot | not-network |
| comparator-class-2026-09-13 | external | 2 | — | 4 | fetched, live | not-network |
| counted-n-comprehension-2026-09-25 | self-contained | 1 | — | 2 | as served | not-network |
| modal-token-repl-2026-08-26 | incomplete | 1 | — | 2 | fetched, live | not-network |
| movedearlier-comp-2026-08-31 | self-contained | 1 | — | 0 | live | not-network |
| multiply-the-quantity-frozen-pool-2026-09-27 | incomplete | 1 | — | 4 | as served | not-network |
| no-undo-rstar-2026-09-22 | external | 2 | — | 4 | fetched | not-network |
| none-of-not-all-of-comprehension-2026-08-30 | self-contained | 1 | — | 1 | live | not-network |
| oi-tracker-state-panel-2026-09-27 | incomplete | 2 | numpy | 7 | fetched | not-network |
| on-behalf-of-comprehension-2026-09-25 | self-contained | 1 | — | 2 | as served | not-network |
| post-guess-2026-09-29 | incomplete | 7 | pybamm | 14 | fetched | not-network |
| send-snapshot-comprehension-replica-2026-09-25 | self-contained | 1 | — | 1 | live, snapshot | not-network |
| some-or-all-original-2026-08-23 | external | 3 | banks, build | 3 | fetched, live | not-network |
| they-one-many-comp-2026-08-31 | self-contained | 1 | — | 0 | live | not-network |

Totals: 15 candidates, 0 with a network-capable import, 15 not-network. The recall gap the hard label found (3 of 40) is therefore the whole of it on this corpus as far as imports and file literals can see; what remains structurally invisible is a script that fetches through a binary or a vendored client that none of these names, and no such file is referenced here.
