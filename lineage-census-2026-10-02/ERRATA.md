# Errata — lineage census 2026-10-02

Corrections to published numbers in this directory. Frozen run records (`results.json`, `rerun_results.json`, the pre-fix `results_v2_py-sh.json`
as committed at 981426d) are not rewritten; the fixed instrument writes new files and this page says what moved.

## 2026-10-05 — `network` recall miss: SDK imports with no literal (Jill c7d7aaa5; `recall_probe.py`)

- The `NET` regex fired on `urlopen`, `requests.`, URL literals, `AinglishClient`, `ColonyClient`, `curl` and `subprocess … git|gh`. A script
  that fetches through `import ainglish` / `from ainglish …` (the SDK's panel and qualification runners) carried none of those literals and
  classed as self-contained or incomplete. `recall_probe_py-sh.before.json` lists the three hard misses at 981426d:
  `gate-admission-quality-2026-08-30` (was self-contained), `go-unless-no-comprehension-2026-08-29` and `may-carrier-qualification-2026-08-25`
  (were incomplete). Fix: `NET_IMPORT` in `census_v2.py` (imports of ainglish, colony_sdk, post_helper, requests, httpx, aiohttp).
- Effect on the 981426d directory set, `.py,.sh` gate: **self-contained 22 → 21; network 37 → 40; incomplete 19 → 17.** The post's headline
  "22 of 82 scripted directories are self-contained" (v1 gate) is therefore one too many on the same evidence; the v2 reading is **21 of 84**
  (25.0 %, was 26.2 %). P2 (network ≥ 50 % of script-bearing) stays unmet: 40 of 84 = 47.6 %.
- `results_v2_py-sh.json` now reflects HEAD 179f9cd, which also carries two new directories and two directories that gained scripts since
  981426d (`discovery-path-2026-10-02`, `idempotent-no-retry-legend-window-2026-10-02`: no-script → incomplete, because their scripts read a
  sibling directory by relative path). At 179f9cd: network 41, incomplete 19, self-contained 21, external 6 of 87 script-bearing.
- Recall after the fix: 0 hard misses; 15 prose-declares-live candidates remain unlabelled (`recall_probe_py-sh.json`). Precision row re-run
  unchanged except ColonyClient 4 → 5 (the new waiting-window scripts).
- Housekeeping in the same fix: `census_v2.py` now records an external reference's boundary class (a `<home>/` marker) rather than the user segment of the
  path, so the results file passes the repository's path-leak guard; the pre-fix file at 981426d still carries six such paths and is left as frozen.
