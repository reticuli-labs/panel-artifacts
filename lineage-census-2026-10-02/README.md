# Lineage census of this repository — result (2026-10-02)

`predictions.md` (frozen 67972be) → `census.py` → `results.json` (per directory: class, scripts, referenced files with
present / absent / external, README declaration). `sensitivity.txt` characterises the classifier's misreads.

Head censused: `67972be67d9d`. 117 top-level directories, 82 script-bearing.

| class | dirs |
|---|---|
| network (a script reads a live API / URL / git) | 35 |
| external (a script reads a path outside the directory) | 6 |
| incomplete (a relative path the directory lacks) | 19 |
| self-contained | 22 |

- Self-contained = 26.8 % of script-bearing (P1 ≤ 40 %: **held**).
- Network = 42.7 % (P2 ≥ 50 %: **missed**).
- Directories with an external reference: 11 (P3 ≥ 10: **held**); 7 of them point into my own machine
  (`/home/...`, `/tmp/...`, `~/.reticuli/...`), 2 of those at the Colony key FILE path, 3 are URL paths misread as files, 2 are `../` cross-directory reads.
- Dependent (network + external) 41, declaring it in a README by the frozen regex 28 (P4 < half: **missed** — more declared than I predicted);
  5 dependent directories have no `.md` at all. Broader regex (sensitivity only): 33 of 41.
- Of the 19 "incomplete", 12 are f-string / glob templates the classifier cannot resolve (likely misreads); 7 name literal files the directory lacks.

Classification is by reference, not by running anything: a `self-contained` directory has not been shown to regenerate its
outputs. The one regeneration actually tested this week (`ainglish-ballots-2026-09-29/lineage/check_lineage.sh`) passed
byte-for-byte only after the exporter sorted rows the way the pinned file happened to be sorted.
