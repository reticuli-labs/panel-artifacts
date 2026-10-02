#!/usr/bin/env bash
# Regenerate facts.json and rows_compact.json from the raw public-API pull and compare them byte-for-byte with the
# pinned files one directory up. Exit 0 = both identical. Needs only python3 and gzip.
set -u
HERE="$(cd "$(dirname "$0")" && pwd)"; PIN="$(dirname "$HERE")"; T="$(mktemp -d)"
gunzip -c "$HERE/ballots_all.json.gz" > "$T/ballots_all.json" || exit 2
cp "$PIN/facts.py" "$HERE/compact.py" "$T/" && cd "$T" && python3 facts.py > /dev/null && python3 compact.py > /dev/null || exit 3
RAW_SHA="$(sha256sum ballots_all.json | cut -d' ' -f1)"
F_OK=0; C_OK=0
[ "$(sha256sum facts.json | cut -d' ' -f1)" = "$(sha256sum "$PIN/facts.json" | cut -d' ' -f1)" ] && F_OK=1
[ "$(sha256sum rows_compact.regen.json | cut -d' ' -f1)" = "$(sha256sum "$PIN/rows_compact.json" | cut -d' ' -f1)" ] && C_OK=1
echo "raw ballots_all.json sha256 $RAW_SHA"; echo "facts.json identical: $F_OK"; echo "rows_compact.json identical: $C_OK"
rm -rf "$T"; [ "$F_OK" = 1 ] && [ "$C_OK" = 1 ]
