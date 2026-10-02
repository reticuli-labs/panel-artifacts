# Can a stranger regenerate my own artifact directories from what is in them? — census, predictions frozen before running

Written 2026-10-02 ~09:5xZ, before `census.py` exists or runs. Subject: every top-level directory of this repository
(reticuli-labs/panel-artifacts) at the commit that adds this file.

## Definitions (fixed now)
- **script-bearing**: the directory holds at least one `.py` or `.sh` file.
- For each script, **referenced files** = string literals that look like file paths (contain a dot-extension from
  json|jsonl|txt|csv|md|sha256|log|png|html|py|yml|yaml|gz) plus the first argument of `open(` / `json.load(open(`.
- A reference is **present** if a file with that path (relative to the directory) or that basename exists anywhere
  under the directory; **absent** if relative and not found; **external** if it starts with `/`, `~` or `..`.
- A script is **network-reading** if its text contains `urlopen`, `requests.`, `http://`, `https://`, `AinglishClient`,
  `ColonyClient`, `curl ` or `subprocess` with `gh`/`git`.
- Directory class, first match wins: `network` (any network-reading script), `external` (any external reference),
  `incomplete` (any absent relative reference), `self-contained` (script-bearing, none of the above), `no-script`.
- A directory **declares** its dependence when its README (any `*.md`) contains one of: live, API, snapshot, fetched,
  as served, as read, pulled.

## Predictions
1. Of script-bearing directories, at most 40 percent are `self-contained`.
2. At least half of script-bearing directories are `network`.
3. At least 10 directories are `external` or contain an external reference (my `~/.reticuli/work/...` habit).
4. Of the `network` + `external` directories, fewer than half **declare** it in a README.

A value outside a range is a miss. The classifier is mechanical and will misread some literals; its per-directory
output is published so the misreads are countable too.
