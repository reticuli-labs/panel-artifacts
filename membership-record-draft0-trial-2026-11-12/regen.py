"""Regenerate one of my two seeded banks from its committed generator, in a scratch tree, and probe what its seeds decide.

usage: python3 -I regen.py choose-any|include-both <path to the generator file in the scratch tree>

The generator is loaded as a module. Its __main__ block, which writes files, is never run; only its functions are
called, in the order that block calls them. Prints one JSON object."""
import hashlib
import importlib.util
import json
import platform
import sys

which, path = sys.argv[1], sys.argv[2]


def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(v):
    return hashlib.sha256(canonical(v)).hexdigest()


spec = importlib.util.spec_from_file_location("bank_generator", path)
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)          # for choose-any this reads ../pkg/rendering-contract.json and checks two span digests
out = {"python": platform.python_implementation() + " " + platform.python_version()}
pair = lambda i: (i["english"], i["ainglish"])

if which == "choose-any":
    worlds = M.neutral_bank()
    mapping = M.assign(worlds)
    draws = mapping.pop("_draws")
    cal = M.calibration_items()
    items = [M.render(w, mapping[w["id"]]) for w in worlds] + cal
    out.update(items_sha256=digest(items), worlds_sha256=digest(worlds), items=len(items), assignment_draws=draws,
               seeds={"world": M.WORLD_SEED, "assignment": M.ASSIGNMENT_SEED},
               constants={"frames": list(M.FRAMES), "spans": dict(M.SPANS), "dedup": M.DEDUP, "forms": list(M.FORMS)})
    # the assignment seed, moved by one: same worlds, a new deal of worlds to forms
    a0 = M.ASSIGNMENT_SEED
    M.ASSIGNMENT_SEED = a0 + 1
    mapping2 = M.assign(worlds)
    draws2 = mapping2.pop("_draws")
    M.ASSIGNMENT_SEED = a0
    items2 = [M.render(w, mapping2[w["id"]]) for w in worlds]
    out["assignment_seed_plus_one"] = {
        "worlds_digest_unchanged": digest(worlds) == out["worlds_sha256"],
        "worlds_whose_form_changed": sum(1 for k in mapping if mapping[k] != mapping2[k]),
        "real_pairs_changed": sum(1 for a, b in zip(items, items2) if pair(a) != pair(b)), "of": len(worlds),
        "assignment_draws": draws2}
    # the world seed, moved by one: new names, scores and orders inside every world
    w0 = M.WORLD_SEED
    M.WORLD_SEED = w0 + 1
    worlds3 = M.neutral_bank()
    cal3 = M.calibration_items()
    mapping3 = M.assign(worlds3)
    mapping3.pop("_draws")
    M.WORLD_SEED = w0
    items3 = [M.render(w, mapping3[w["id"]]) for w in worlds3]
    fixed = ("id", "domain", "frame_family", "task_family", "n")
    out["world_seed_plus_one"] = {
        "world_ids_domains_frames_tasks_sizes_changed": sum(1 for a, b in zip(worlds, worlds3) if any(a[k] != b[k] for k in fixed)),
        "worlds_whose_text_changed": sum(1 for a, b in zip(worlds, worlds3) if a["context"] != b["context"]),
        "worlds_whose_form_changed": sum(1 for k in mapping if mapping[k] != mapping3[k]),
        "real_pairs_changed": sum(1 for a, b in zip(items, items3) if pair(a) != pair(b)), "of": len(worlds),
        "calibration_pairs_changed": sum(1 for a, b in zip(cal, cal3) if pair(a) != pair(b)), "calibration_of": len(cal)}
else:
    real, cal = M.real_items(), M.calibration_items()
    items = real + cal
    out.update(items_sha256=digest(items), items=len(items), seeds={"bank": M.BANK_SEED})
    b0 = M.BANK_SEED
    M.BANK_SEED = b0 + 1
    real2, cal2 = M.real_items(), M.calibration_items()
    M.BANK_SEED = b0
    out["bank_seed_plus_one"] = {
        "real_pairs_changed": sum(1 for a, b in zip(real, real2) if pair(a) != pair(b)), "of": len(real),
        "real_ids_questions_answers_changed": sum(1 for a, b in zip(real, real2) if any(a[k] != b[k] for k in ("id", "question", "answer", "gold_position"))),
        "real_option_orders_changed": sum(1 for a, b in zip(real, real2) if a["options"] != b["options"]),
        "calibration_pairs_changed": sum(1 for a, b in zip(cal, cal2) if pair(a) != pair(b)), "calibration_of": len(cal)}
print(json.dumps(out, ensure_ascii=False))
