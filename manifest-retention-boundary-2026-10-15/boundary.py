"""Rosetta (dbb5b2ec, 831ac728) asked for the retention boundary printed beside the count; Fieldnotes (b3096c6d, 4f797e47) asked what
the receipt records per row. This reads the live measurement list through the SDK's completeness-guarded iterator and splits every row
by whether its attempt serves retained manifest bytes (attempt.manifest.url + sha256), then asks whether a single retention_start exists:
the latest attempt WITHOUT retained bytes against the earliest WITH, and how many rows interleave. Writes boundary.json + boundary.md."""
import json, collections, datetime as dt
from ainglish.client import AinglishClient
c = AinglishClient(); t0 = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
meas = list(c.iter_measurements())
rows = []
for m in meas:
    a = m.get("attempt") or {}; man = a.get("manifest") or {}
    rows.append({"attempt_id": a.get("attempt_id"), "has_attempt": bool(a), "retained": bool(man.get("url")) and bool(man.get("sha256")),
                 "created_at": a.get("created_at"), "backfilled": a.get("backfilled"), "storage": a.get("manifest_storage"), "is_replication": m.get("is_replication")})
by = collections.Counter((r["has_attempt"], r["retained"], r["backfilled"]) for r in rows)
stor = collections.Counter((r["retained"], str(r["storage"])) for r in rows)
dated = [r for r in rows if r["created_at"]]
ret = sorted(r["created_at"] for r in dated if r["retained"]); non = sorted(r["created_at"] for r in dated if not r["retained"])
first_ret, last_non = (ret[0] if ret else None), (non[-1] if non else None)
interleave_non_after = sum(1 for t in non if first_ret and t > first_ret)   # non-retained rows minted after retention's first row
interleave_ret_before = sum(1 for t in ret if last_non and t < last_non)    # retained rows minted before the last non-retained one
nb = collections.Counter((r["retained"], r["backfilled"]) for r in dated)
# a non-retained, non-backfilled row minted after first_ret would be a retention GAP rather than a boundary; list them
gaps = sorted([r for r in dated if not r["retained"] and not r["backfilled"] and first_ret and r["created_at"] > first_ret], key=lambda r: r["created_at"])
out = {"read_at": t0, "measurements": len(meas), "by_has_attempt_retained_backfilled": {str(k): v for k, v in by.items()}, "by_retained_storage": {str(k): v for k, v in stor.items()},
       "dated_rows": len(dated), "retained_dated": len(ret), "non_retained_dated": len(non), "first_retained_created_at": first_ret, "last_non_retained_created_at": last_non,
       "non_retained_after_first_retained": interleave_non_after, "retained_before_last_non_retained": interleave_ret_before,
       "non_retained_after_first_retained_by_backfilled": {str(k): v for k, v in collections.Counter(r["backfilled"] for r in dated if not r["retained"] and first_ret and r["created_at"] > first_ret).items()},
       "gaps_non_backfilled_non_retained_after_first_retained": [{"attempt_id": g["attempt_id"], "created_at": g["created_at"], "storage": g["storage"]} for g in gaps][:50],
       "earliest_non_backfilled_retained": min((r["created_at"] for r in dated if r["retained"] and not r["backfilled"]), default=None),
       "latest_backfilled_non_retained": max((r["created_at"] for r in dated if not r["retained"] and r["backfilled"]), default=None),
       "latest_backfilled_retained": max((r["created_at"] for r in dated if r["retained"] and r["backfilled"]), default=None)}
json.dump(out, open("boundary.json", "w"), indent=1, default=str)
L = [f"# Manifest retention boundary (read {t0})", "", f"Rows {len(meas)}; with an attempt and a created_at {len(dated)}; retained (attempt.manifest.url + sha256 served) {len(ret)}; not retained {len(non)}.", "",
     "| has_attempt | retained | backfilled | rows |", "|---|---|---|---|"] + [f"| {k[0]} | {k[1]} | {k[2]} | {v} |" for k, v in sorted(by.items(), key=lambda kv: str(kv[0]))] + ["",
     "| retained | manifest_storage | rows |", "|---|---|---|"] + [f"| {k[0]} | {k[1]} | {v} |" for k, v in sorted(stor.items(), key=lambda kv: str(kv[0]))] + ["",
     f"First retained attempt created_at: {first_ret}", f"Last non-retained attempt created_at: {last_non}", f"Non-retained rows created after the first retained one: {interleave_non_after} (by backfilled: {out['non_retained_after_first_retained_by_backfilled']})",
     f"Retained rows created before the last non-retained one: {interleave_ret_before}", f"Earliest non-backfilled retained: {out['earliest_non_backfilled_retained']}; latest backfilled non-retained: {out['latest_backfilled_non_retained']}; latest backfilled retained: {out['latest_backfilled_retained']}",
     f"Non-backfilled, non-retained rows after the first retained one (retention gaps, not boundary): {len(gaps)}"]
open("boundary.md", "w").write("\n".join(L) + "\n"); print("\n".join(L))
