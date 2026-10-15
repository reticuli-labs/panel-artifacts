# Mirror: PR #683 review thread and the shared message-blind-floor parity fixture (2026-10-15)

Preservation and checkability only. The register repository (ai-nglish/ainglish-symfony) is private, so its pull-request links return 404 to anyone else; this directory carries the text that a public post cites. Nothing here is assessed, altered or endorsed by the mirror beyond the byte checks listed.

## Files

- `REVIEWS-683.md` — verbatim bodies of dexagon-ai's three reviews on PR #683 (2026-10-13 and two on 2026-10-15) and reticuli-labs's two fix comments (2026-10-15), copied from the GitHub API response. Authorship is as labelled.
- `message-blind-floor-parity-v1.json` — the cross-language fixture, byte-identical in both repositories: register `tests/Fixtures/message-blind-floor-parity-v1.json` at PR #683 head `97a42f1029fca9ccd3d05a024b3d6b98dd7747ff` and SDK `tests/fixtures/message-blind-floor-parity-v1.json` at ai-nglish/ainglish#223 head `0484f9569d303466c9f53edff12158972d4a28f5` (public: https://github.com/ai-nglish/ainglish/pull/223). sha256 `bdbb099b224b7283e1addf84d5f24a26f8495e7bc956d4257d6e201bddddf3d1`, 8936 bytes, 6 cases: integer-keys-reordered-options, no-break-space-key, python-whitespace-set, casefold-not-lowercase, calibration-excluded-integer-and-text-mix, calibration-string-zero-is-truthy. Its header pins the SDK commit and the sha256 of `panel.py` whose `message_blind_floor` produced every expected block.

- `diff_check.php` and `differential.json` — a differential run on 2026-10-15 of the four primitive pairs the thread turned on, PHP 8.2.33 in the register's container against Python 3.12.3 on the same box: `empty()` against `bool()` over one JSON value of every type and shape (the only disagreement is the string `"0"`), `trim` against `str.strip` on NUL, form feed, no-break space and file separator, `MB_CASE_FOLD` and `mb_strtolower` against `casefold` and `lower` on sharp s, and `number_format(17/32, 4)` against `f"{17/32:.4f}"`. The Python half is inlined in `differential.json` (`strip`, `casefold`, `round` keys); the PHP half is the `php` key, which is the script's output verbatim.

## Checks run before committing

The two fixture copies were fetched independently (the register copy from the local checkout of 97a42f1, the SDK copy as base64 from the GitHub contents API at the #223 head) and compared byte for byte before writing; the sha256 above is of those bytes. The review bodies were copied from one `gh pr view --json reviews,comments` response and not edited.
