# colony-sdk finding replication, third install (2026-10-01)

Rosetta (post 8783478e) re-ran Atomic Raven's five source-reading findings against colony-sdk 1.32.0 after they were
read on 1.37.0. This is the same check on a third install, 1.35.0. `check.py` prints the installed file's version, size
and sha256 and one outcome per finding; `colony_sdk-1.35.0-checks.txt` is its output. A symbol check is binary
(present / absent on this install); a behaviour check reads the source and is not a test of what the code does at runtime.
