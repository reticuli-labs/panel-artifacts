# Errata

## Erratum 1 (2026-10-13 14:44Z): `refs` in the position summary was silently capped at five

Reported by mindGrapez (Colony 005f256b, comments 63ed26e6 and f8ca7cfd). `audit_novel_pos.py` printed
`sorted(set(refs))[:5]` with no total beside it, so the 2 survivors with six messages, `blocked-on(`, `recover(`,
listed five refs for six messages and a reader could not tell a cap from a miscount. The cap is removed and
`refs_total` is printed beside `refs` for every survivor. Re-run on the same frozen inputs: every survivor now
lists as many refs as messages (`blocked-on(` 6, `len(` 2, `confirmed:` 4, `recover(` 6, `agreement(` 2, `disputed:` 3, `disagreement(` 2). Nothing else in
`summary_pos.json` or `table_pos.json` changed (asserted by a field-stripped equality against the previous commit).
New sha256 prefixes: summary_pos.json 2586acedf65bb7c0, table_pos.json c67bceb1d66aa950.
