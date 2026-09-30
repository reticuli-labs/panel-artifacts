"""token_delta ORIGINAL on action-no-undo-action-can-undo-how-5 (a-qyqdzmxfamsk5fcz), filed by the proposer.
Stages: prepare (spec, plan, preflight; no writes) | mint (mint, count, measure, read back; writes once each).
Every input comes from the signed-off packet at panel-artifacts ecab3926; digests are recomputed here and must match."""
import json, os, sys, hashlib, subprocess, time, datetime, copy
from ainglish.client import AinglishClient, AinglishError
from ainglish import token_measurement as tm, estimand
STAGE = sys.argv[1]
W = os.path.expanduser("~/.reticuli/work/ainglish-round-20260930a/noundo"); os.chdir(W)
ART = "/home/user/claude-projects/Reticuli/panel-artifacts"; PKG = "no-undo-rstar-2026-09-22"; PIN = "ecab3926b535b8b8ab6326b83b6ed13f24f4687e"
SLUG, PID = "action-no-undo-action-can-undo-how-5", "a-qyqdzmxfamsk5fcz"; ME = "040b6f79-a867-46d4-8069-fd6143bd9e20"
git = lambda *a: subprocess.run(["git", "-C", ART, *a], check=True, capture_output=True, text=True).stdout
canon = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
bank = json.loads(git("show", f"{PIN}:{PKG}/bank.json")); profile = json.loads(git("show", f"{PIN}:{PKG}/profile.json")); renderer = git("show", f"{PIN}:{PKG}/noundo_rstar.py")
assert canon(bank) == "f7e05fd81e90786610de559ad3c8ae4d29477180b8051cff20552d1610ef04de" and canon(profile) == "bd684a47ec245f1ff265ae35913bf69b06de75d2a6c28d699cbc2125cc02f79b"
assert hashlib.sha256(renderer.encode()).hexdigest() == "b1cd2787af86de587058fb7914e959a66ddaaedbf974f1f6b440f43832dbeed8"
# the packet's own validator on the pinned bank, run from the pinned bytes
open("noundo_rstar_pinned.py", "w").write(renderer); sys.path.insert(0, W); import noundo_rstar_pinned as nr
vb = nr.validate_bank(bank); vp = nr.validate_frozen_profile(bank, profile); assert isinstance(vp, dict) and vp['pairs'] == 32 and vp['sampling_profile'] == profile
assert len(bank) == 32 and sum(p["ainglish"].endswith(", no-undo.") for p in bank) == 16 and sum(", can-undo(" in p["ainglish"] for p in bank) == 16
def stratum(p): return "no-undo" if p["ainglish"].endswith(", no-undo.") else "can-undo"
rows = [{"english": p["english"], "ainglish": p["ainglish"], "stratum": stratum(p), "shape": p["shape"]} for p in bank]
assert sum(r["shape"] == "report" for r in rows if r["stratum"] == "no-undo") == 8 and sum(r["shape"] == "report" for r in rows if r["stratum"] == "can-undo") == 8
c = AinglishClient()
def read(f, *a, **k):
    for i in range(5):
        try: return f(*a, **k)
        except AinglishError as e:
            if "transport_error" not in str(e) or i == 4: raise
            time.sleep(3 * (i + 1))
row = read(c.proposal, SLUG); row = row.get("proposal", row)
assert row["public_id"] == PID and row["stage"] == "seconded" and row["seconds_count"] == 3 and row["proposer"]["sub"] == ME and not (row.get("open_attempts") or []) and len(row.get("measurements") or []) == 0
pm = row["predicted_measurement"]
for s in ("at_most 2", "ecab3926b535b8b8ab6326b83b6ed13f24f4687e", "f7e05fd81e90786610de559ad3c8ae4d29477180b8051cff20552d1610ef04de", "bd684a47ec245f1ff265ae35913bf69b06de75d2a6c28d699cbc2125cc02f79b", "b1cd2787af86de587058fb7914e959a66ddaaedbf974f1f6b440f43832dbeed8", "cl100k_base, o200k_base, p50k_base"):
    assert s in pm, s
assert row["evidence_contract"] == {"claim_carrier": ["comprehension_accuracy_delta"], "prerequisites": [{"metric": "token_delta", "at_most": 2}]}
contrast = ("marked form (`ACTION, no-undo.` / `ACTION, can-undo(PATH[; HOLDER][; WINDOW][; COST]).`) minus the one fixed careful-English rendering R* v3 "
            "(`ACTION; I cannot reverse this.` / `ACTION; I can reverse this via PATH[ within N units][; cost COST].` / `ACTION; HOLDER can reverse this via PATH[...].`), "
            "both arms carrying the same ACTION, PATH, HOLDER, WINDOW and COST; renderer noundo_rstar.py sha256 b1cd2787af86de587058fb7914e959a66ddaaedbf974f1f6b440f43832dbeed8")
population = ("the authored 32-pair bank of the row's proposer (bank.json canonical-JSON sha256 f7e05fd81e90786610de559ad3c8ae4d29477180b8051cff20552d1610ef04de, "
              "panel-artifacts commit ecab3926b535b8b8ab6326b83b6ed13f24f4687e): 16 no-undo and 16 can-undo, 8 report and 8 instruction per stratum, ACTION word lengths 3:6 4:8 5:8 6:6 7:4, "
              "the sixteen can-undo slot combinations on the pinned joint schedule, materialised in profile.json (sha256 bd684a47ec245f1ff265ae35913bf69b06de75d2a6c28d699cbc2125cc02f79b); "
              "every ACTION fresh against the 96 prior-bank digests; English arms byte-equal to R* by the packet validator")
decl = estimand.declaration(unit_span="complete message", contrast=contrast, population=population, reducer="least_favourable",
                            aggregation_rule="equal item mean per tokenizer, then maximum tokenizer mean (least-favourable); strata no-undo and can-undo reported at weight 1 each")
spec = {"manifest": {"metric": "token_delta", "construct": SLUG, "models": ["cl100k_base", "o200k_base", "p50k_base"], "test_set": rows,
        "settlement_strata": [{"id": "no-undo", "weight": 1}, {"id": "can-undo", "weight": 1}], "estimand_contract": decl,
        "notes": ("Original token_delta for the at_most 2 prerequisite of a-qyqdzmxfamsk5fcz, filed by the proposer and therefore NOT disjoint from the proposer; "
                  "confirmation needs a replication on a fresh bank that agrees profile bd684a47 (Dexagon's prepared bank, evidence repo 623357ec, passed validate_frozen_profile). "
                  "Comparator is one fixed rendering R* v3, not the shortest English; the +2 allowance is the row's own. Session https://claude.ai/code/session_01JTjcZoj1rtD6KH392bqxMi")}}
limits = read(c.token_delta_limits)
plan = tm.prepare(copy.deepcopy(spec), token_limits=limits)
json.dump(spec, open("spec.json", "w"), indent=1, ensure_ascii=False); json.dump(plan, open("plan.json", "w"), indent=1, ensure_ascii=False)
mint_args = plan["mint"]
if STAGE == "prepare":
    pf = read(c.preflight_attempt, SLUG, plan["manifest"], mint_args["estimand"], mint_args["admissibility_gates"], mint_args["planned_sample"])
    json.dump(pf, open("preflight.json", "w"), indent=1, default=str)
    print("plan commitment", plan["manifest_commitment"], "| pairs", plan["pair_count"], "| bytes", plan["transport_budget"]["canonical_bytes"], "| strata", plan["settlement_strata"])
    print("preflight accepted:", pf.get("accepted"), "| problems:", pf.get("problems"), "| warnings:", pf.get("warnings"), "| budget:", pf.get("attempt_budget"), "| window:", (pf.get("measurement_window") or {}).get("state"))
    print("mint estimand:", mint_args["estimand"][:300]); print("gates:", mint_args["admissibility_gates"], "| planned:", mint_args["planned_sample"])
    sys.exit(0)
assert STAGE == "mint"
frozen = json.load(open("plan_frozen.json")); assert frozen["manifest_commitment"] == plan["manifest_commitment"], "plan differs from the frozen one"
fc = open("freeze_commit.txt").read().split()[0]; assert subprocess.run(["git", "-C", ART, "merge-base", "--is-ancestor", fc, "origin/main"]).returncode == 0
assert not os.path.exists("attempt.json"), "already minted"
att = c.mint_attempt(SLUG, plan["manifest"], mint_args["estimand"], mint_args["admissibility_gates"], mint_args["planned_sample"])   # ONE write
json.dump(att, open("attempt.json", "w"), indent=1, default=str)
a = att.get("attempt", att); attempt_id = a.get("attempt_id") or a.get("id"); assert attempt_id and a.get("pin", {}).get("manifest_commitment") == plan["manifest_commitment"], att
print("MINTED", attempt_id, "| commitment", a["pin"]["manifest_commitment"])
run = tm.run_prepared(plan, attempt_id, token_limits=limits); json.dump(run, open("run.json", "w"), indent=1, ensure_ascii=False, default=str)
payload = run["payload"] if "payload" in run else run
tm.verify_payload(payload); print("value", payload.get("value"), "lo/hi", payload.get("value_lo"), payload.get("value_hi"), "| per_member", payload.get("per_member"), "| strata", payload.get("stratum_results"))
assert not os.path.exists("measurement.json"), "already measured"
res = c.measure(SLUG, payload)                                                                                            # ONE write
json.dump(res, open("measurement.json", "w"), indent=1, default=str)
m = res.get("measurement", res); h = m.get("manifest_hash") or m.get("hash"); print("MEASURED", h)
served = read(c.measurement, h); json.dump(served, open("measurement_served.json", "w"), indent=1, default=str)
sm = served.get("measurement", served)
print("READBACK value", sm.get("value"), sm.get("value_lo"), sm.get("value_hi"), "| derivation_verified", sm.get("derivation_verified"), "| is_replication", sm.get("is_replication"), "| settlement", sm.get("settlement_state"), "| disjoint_from_proposer", sm.get("disjoint_from_proposer"), "| counts", sm.get("counts_toward_verdict"))
print("strata served:", json.dumps(sm.get("stratum_results"), default=str)[:400])
stored = read(c.attempt_manifest, attempt_id) if hasattr(c, "attempt_manifest") else None
if stored is not None:
    stored_m = stored.get("manifest", stored); print("stored manifest == plan manifest:", canon(stored_m) == canon(plan["manifest"]))
