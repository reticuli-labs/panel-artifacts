"""analyse.py: the table of the sweep, from the files beside it: banks.json, blind_items.jsonl, reads.jsonl (the blind reads),
controls.jsonl with reads_controls.jsonl, and planted/ (the planted bank and its reads). It runs nothing and reads nothing else.
Writes results.json and table.md. The rules it applies are the ones PLAN.md states; a change to them after the reads were made
would be visible in this repository's history.

Per distinct bank (files with the same item list are one bank):
  n          real items read: not calibration, arms not identical, the read neither truncated nor failed
  blind      how many of them the blind reader answered with the key
  null       what a reader whose answers are unrelated to the keys would score: the reader's own answers, shuffled among the
             items with the same number of options (PERMS shuffles, fixed seed); mean, and p = share of shuffles scoring >= blind
  excess     (blind/n - null/n) / (1 - null/n), floored at 0: the share of items answered blind beyond that null
  flagged    p < 0.05 / (number of distinct banks with n >= 10)
RESULTS_DIR=<dir> reads another directory with the same file names (used by the mutation check)."""
import collections, json, os, sys
import numpy as np
HERE = os.environ.get("RESULTS_DIR") or os.path.dirname(os.path.abspath(__file__)); PERMS = 200_000; SEED = 20261121; MIN_N = 10


def jl(name, root=HERE):
    return [json.loads(l) for l in open(os.path.join(root, name), encoding="utf-8") if l.strip()]


def permutation(pairs, rng):
    """pairs: [(number of options, position picked or -1, position of the key)]. -> (observed matches, null mean, p)."""
    obs = sum(1 for k, p, a in pairs if p == a); null = np.zeros(PERMS, dtype=np.int32); groups = collections.defaultdict(list)
    for k, p, a in pairs: groups[k].append((p, a))
    for k, g in groups.items():
        picks = np.array([p for p, a in g]); keys = np.array([a for p, a in g])
        if len(g) == 1: null += int(picks[0] == keys[0]); continue
        for start in range(0, PERMS, 20_000):
            m = min(20_000, PERMS - start); idx = np.argsort(rng.random((m, len(g))), axis=1)
            null[start:start + m] += (picks[idx] == keys[None, :]).sum(axis=1)
    return obs, float(null.mean()), float((1 + (null >= obs).sum()) / (1 + PERMS))


def score(item_ids, items, reads, rng, want=lambda v: True):
    pairs, faults, off = [], 0, 0
    for i in item_ids:
        v, r = items[i], reads.get(i)
        if not want(v): continue
        if r is None or r.get("fault") or r.get("truncated"): faults += 1; continue
        pos = v["options"].index(r["picked"]) if r.get("picked") in v["options"] else -1; off += pos == -1
        pairs.append((len(v["options"]), pos, v["options"].index(v["answer"])))
    if not pairs: return {"n": 0, "blind": 0, "null_mean": 0.0, "p": 1.0, "excess": 0.0, "not_read": faults, "off_option": off}
    obs, mean, p = permutation(pairs, rng); n = len(pairs); c = mean / n
    return {"n": n, "blind": obs, "null_mean": round(mean, 2), "p": p, "excess": round(max(0.0, (obs / n - c) / (1 - c)) if c < 1 else 0.0, 4), "not_read": faults, "off_option": off}


def main():
    rng = np.random.default_rng(SEED); banks = json.load(open(os.path.join(HERE, "banks.json"), encoding="utf-8"))
    items = {r["id"]: r for r in jl("blind_items.jsonl")}; reads = {r["id"]: r for r in jl("reads.jsonl")}
    by_sha = collections.OrderedDict()
    for b in banks: by_sha.setdefault(b["sha256_items"], []).append(b)
    real = lambda v: not v["calibration"] and not v["identical_arms"]; rows = []
    for sha, files in by_sha.items():
        ids = files[0]["item_ids"]; s = score(ids, items, reads, rng, real)
        s2 = score(ids, items, reads, rng, lambda v: real(v) and not v["abstain_key"]); cal = score(ids, items, reads, rng, lambda v: v["calibration"])
        rows.append(dict(s, sha256_items=sha, files=[f["dir"] + "/" + f["file"] for f in files], items_in_bank=len(ids), identical_arms=sum(items[i]["identical_arms"] for i in ids),
                         abstain_keys=sum(real(items[i]) and items[i]["abstain_key"] for i in ids), without_abstain_keys={k: s2[k] for k in ("n", "blind", "null_mean", "p", "excess")},
                         calibration={k: cal[k] for k in ("n", "blind", "null_mean", "p")}))
    tested = [r for r in rows if r["n"] >= MIN_N]; alpha = 0.05 / max(1, len(tested))
    for r in rows: r["flagged"] = bool(r["n"] >= MIN_N and r["p"] < alpha)
    allcal = score(sorted(i for i, v in items.items() if v["calibration"]), items, reads, rng); allreal = score(sorted(i for i, v in items.items() if real(v)), items, reads, rng)
    # controls
    ctl = {c["id"]: c for c in jl("controls.jsonl")}; cr = {r["id"]: r for r in jl("reads_controls.jsonl")}; kinds = collections.defaultdict(lambda: [0, 0, 0])
    for cid, c in ctl.items():
        r = cr.get(cid); k = kinds[c["kind"]]; k[0] += 1
        if r is None or r.get("fault") or r.get("truncated"): k[2] += 1; continue
        k[1] += r.get("picked") == c["answer"]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import build_blind as B
    pd = os.path.join(HERE, "planted"); pit = {r["id"]: r for r in jl("blind_items.jsonl", pd)}; prd = {r["id"]: r for r in jl("reads.jsonl", pd)}
    cls = {B.item_id(it): it["planted_class"] for it in json.load(open(os.path.join(pd, "items.json"), encoding="utf-8"))}
    planted = {c: score(sorted(i for i in pit if cls[i] == c), pit, prd, rng) for c in ("key only in the gap", "key in the shared text")}
    instrument = {"answer_written_into_the_blind_text": {"n": kinds["planted"][0], "right": kinds["planted"][1], "not_read": kinds["planted"][2]},
                  "careful_english_arm_whole": {"n": kinds["sighted"][0], "right": kinds["sighted"][1], "not_read": kinds["sighted"][2]},
                  "planted_bank": planted, "all_calibration_items": allcal, "all_real_items": allreal}
    g, s = planted["key only in the gap"], planted["key in the shared text"]; w = instrument["answer_written_into_the_blind_text"]
    checks = {"answer written in: at least 95 in 100 found": w["n"] > 0 and w["right"] >= 0.95 * (w["n"] - w["not_read"]),
              "planted bank, key in the shared text: at least 9 in 10 found": s["n"] > 0 and s["blind"] >= 0.9 * s["n"],
              "planted bank, key only in the gap: not above the null (p > 0.05)": g["n"] > 0 and g["p"] > 0.05,
              "calibration items of all banks together: not above the null (p > 0.001)": allcal["n"] > 0 and allcal["p"] > 0.001}
    out = {"reads": len(reads), "distinct_items": len(items), "banks": len(rows), "banks_tested": len(tested), "alpha_per_bank": alpha, "permutations": PERMS,
           "instrument": instrument, "instrument_checks": checks, "instrument_ok": all(checks.values()), "flagged": sum(r["flagged"] for r in rows),
           "flagged_with_excess_at_least_half": sum(r["flagged"] and r["excess"] >= 0.5 for r in rows), "rows": sorted(rows, key=lambda r: (-r["excess"], r["files"][0]))}
    json.dump(out, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "table.md"), "w", encoding="utf-8") as f:
        f.write("| bank (first file) | files | real items read | answered blind | null | excess share | p | flagged | arms identical | calibration blind |\n|---|---|---|---|---|---|---|---|---|---|\n")
        for r in out["rows"]:
            f.write("| %s | %d | %d | %d | %.1f | %.2f | %.5f | %s | %d | %d of %d |\n" % (r["files"][0], len(r["files"]), r["n"], r["blind"], r["null_mean"], r["excess"], r["p"], "yes" if r["flagged"] else ("no" if r["n"] >= MIN_N else "too few"),
                                                                                r["identical_arms"], r["calibration"]["blind"], r["calibration"]["n"]))
    print(json.dumps({k: out[k] for k in ("reads", "distinct_items", "banks", "banks_tested", "alpha_per_bank", "instrument_checks", "instrument_ok", "flagged", "flagged_with_excess_at_least_half")}, indent=1))
    print("all real items: %(blind)d of %(n)d answered blind, null %(null_mean).0f | calibration: " % allreal + "%(blind)d of %(n)d, null %(null_mean).0f, p %(p).4f" % allcal)


if __name__ == "__main__":
    main()
