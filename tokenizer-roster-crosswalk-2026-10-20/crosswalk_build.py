"""Build the roster crosswalk from the served rows pulled by crosswalk_collect.py: every token_delta row whose panel_models carries an '@' suffix, old identity -> encoding + library + version. Pure function of dl_meas/rows.json; writes crosswalk.json."""
import json, re, collections
rows = json.load(open("dl_meas/rows.json"))
td = [r for r in rows if r.get("metric") == "token_delta"]
pinned = [r for r in td if any("@" in str(m) for m in (r.get("panel_models") or []))]
forms = collections.Counter(); members = collections.Counter(); per_row = []
def parse(m):
    bare, _, suf = m.partition("@")
    lib = ver = None; kind = "other"; enc = bare; note = None
    if re.fullmatch(r"\d+\.\d+(?:\.\d+)?", suf): lib, ver, kind = "tiktoken", suf, "version (library implied by the tiktoken/ prefix)"
    mm = re.fullmatch(r"([A-Za-z_]+)-(\d+\.\d+(?:\.\d+)?)", suf)
    if mm: lib, ver, kind = mm.group(1), mm.group(2), "library-version"
    if suf == "vocab": kind = "marker: vocab, no version carried"
    if bare == "raw-api-tiktoken": enc, kind, note = suf, "inverted: the encoding sits after the @", "the bare half is a harness label, not an encoding"
    if re.fullmatch(r"[0-9a-f]{40}", suf): kind, ver, note = "hf revision", suf, "a git revision of the model repo, not a library version"
    if re.fullmatch(r"[0-9a-f]{8}/tokenizer#[0-9a-f]{16}", suf): kind, ver, note = "hf revision + tokenizer digest", suf, "short revision plus a 16-hex digest of the tokenizer file"
    return {"old_identity": m, "encoding": enc, "library": lib, "version": ver, "suffix": suf, "suffix_kind": kind, "note": note}
for r in pinned:
    ms = [parse(m) for m in r["panel_models"] if "@" in str(m)]
    for p in ms: forms["@" + p["suffix"]] += 1; members[p["old_identity"]] += 1
    env = (r.get("manifest") or {}).get("environment") if isinstance(r.get("manifest"), dict) else None
    per_row.append({"attempt_id": r.get("attempt_id"), "manifest_hash": r.get("manifest_hash"), "at": r.get("at"), "is_replication": r.get("is_replication"), "proposal": r.get("proposal") if isinstance(r.get("proposal"), str) else (r.get("proposal") or {}).get("slug") if isinstance(r.get("proposal"), dict) else None, "submitter": r.get("submitter") or r.get("submitted_by") or r.get("measurer"), "pinned_members": ms})
out = {"built": "2026-10-20", "source": "GET /api/v1/measurements via AinglishClient.iter_measurements (public), pulled 2026-10-20", "rows_total": len(rows), "token_delta_rows": len(td), "token_delta_rows_with_suffix": len(pinned), "suffix_forms": dict(forms), "distinct_old_identities": len(members), "identity_crosswalk": {m: parse(m) for m in sorted(members)}, "rows": per_row, "rule": "the roster member is the encoding name; the part after '@' is provenance (library and version) or a marker, and lives in manifest.environment on filings since 2026-08-25; this table maps each legacy identity to that split without touching any stored row or any comparison key"}
json.dump(out, open("crosswalk.json", "w"), indent=1)
print("rows", len(rows), "token_delta", len(td), "with suffix", len(pinned), "distinct identities", len(members))
print("forms", forms.most_common())
for m, p in out["identity_crosswalk"].items(): print(f"  {m:45s} -> enc={p['encoding']:12s} lib={p['library']} ver={p['version']} kind={p['suffix_kind']}")
print("row keys sample:", [k for k in rows[0].keys() if k in ("submitter","submitted_by","measurer","proposal","proposal_slug","slug")])
