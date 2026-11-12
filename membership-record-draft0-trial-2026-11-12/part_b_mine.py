"""Part B. Three of my own stored banks put to Saturnia's draft 0, the kinds its two examples do not cover.

  choose-any replica   a seeded generator, twelve sentence frames inside each form, planted calibration items, items
                       held outside the manifest
  no-undo token bank   items with no id, a second label inside each form, an English arm made by a renderer
  include-both bank    a seeded generator whose seed draws no real item

usage: python3 part_b_mine.py <extracted packet dir> <checkout of reticuli-labs/panel-artifacts> [<dir of my stored manifests>]

Writes results_b.json and record_choose_any.json beside this file. The generators are read out of git at the commit
each manifest's items_url names, into a scratch tree, and run there by regen.py; the checkout is not touched."""
import collections
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import generic as G  # noqa: E402

PACKET, REPO = sys.argv[1], sys.argv[2]
STORED = sys.argv[3] if len(sys.argv) > 3 else None
SRC = os.path.join(HERE, "src")
out = {}


def load(name):
    raw = open(os.path.join(SRC, name), "rb").read()
    return raw, json.loads(raw)


def at_commit(manifest):
    m = re.fullmatch(r"https://raw\.githubusercontent\.com/reticuli-labs/panel-artifacts/([0-9a-f]{40})/([^/]+)/items\.json", manifest["items_url"])
    assert m, manifest["items_url"]
    return m.group(1), m.group(2)


def show(commit, path):
    return subprocess.run(["git", "-C", REPO, "show", "%s:%s" % (commit, path)], capture_output=True, check=True).stdout


def run(*args):
    r = subprocess.run([sys.executable, "-I"] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


# ---------------------------------------------------------------- choose-any: the seeded bank
raw, manifest = load("choose-any-manifest.json")
items_raw, items = load("choose-any-items.json")
commit, folder = at_commit(manifest)
real = [i for i in items if not i.get("calibration")]
cal = [i for i in items if i.get("calibration")]
assert G.digest(items) == manifest["items_sha256"], "the outside item file is not the committed array"
assert items_raw == show(commit, folder + "/items.json"), "the public file differs from the commit"
assert manifest["item_counts"] == {"calibration": len(cal), "real": len(real)}
field = manifest["settlement_item_field"]
assert all(field in i for i in real) and not any(field in i for i in cal)
ca = out["choose_any"] = {
    "manifest_sha256": hashlib.sha256(raw).hexdigest(), "manifest_has_test_set": "test_set" in manifest,
    "items_url_commit": commit, "items_file_bytes": len(items_raw), "items_array_digest_equals_manifest": True,
    "items": len(items), "real": len(real), "calibration": len(cal),
    "calibration_items_carrying_any_dimension_field": sum(1 for i in cal if any(k in i for k in (field, "domain", "frame_family", "member_count"))),
    "manifest_seed": manifest["seed"]}

with tempfile.TemporaryDirectory() as tree:
    os.makedirs(os.path.join(tree, folder))
    gen = os.path.join(tree, folder, "my_instrument.py")
    open(gen, "wb").write(show(commit, folder + "/my_instrument.py"))
    names = subprocess.run(["git", "-C", REPO, "ls-tree", "-r", "--name-only", commit], capture_output=True, text=True, check=True).stdout.split("\n")
    code, so, se = run(os.path.join(HERE, "regen.py"), "choose-any", gen)
    ca["generator_from_the_published_tree"] = {"runs": code == 0, "error": se.strip().split("\n")[-1][:160].replace(tree, "<tree>"),
                                               "pkg_files_in_the_commit": sum(1 for n in names if n.startswith("pkg/"))}
    assert code != 0 and "rendering-contract.json" in se
    # the same contract is published beside the generator under another name; put it where the generator looks
    os.makedirs(os.path.join(tree, "pkg"))
    contract = show(commit, folder + "/rendering-contract-source.json")
    open(os.path.join(tree, "pkg", "rendering-contract.json"), "wb").write(contract)
    code, so, se = run(os.path.join(HERE, "regen.py"), "choose-any", gen)
    assert code == 0, se[-600:]
    regen = json.loads(so)
    committed_worlds = json.loads(show(commit, folder + "/neutral-worlds.json"))
ca["regenerated"] = {"python": regen["python"], "items_sha256_equals_manifest": regen["items_sha256"] == manifest["items_sha256"],
                     "bank_seeds": regen["seeds"], "bank_seeds_named_in_the_manifest": sum(1 for v in regen["seeds"].values() if str(v) in raw.decode()),
                     "assignment_draws": regen["assignment_draws"],
                     "assignment_draws_equal_the_committed_record": regen["assignment_draws"] == committed_worlds["assignment_draw_index"],
                     "contract_file_sha256": hashlib.sha256(contract).hexdigest()}
assert ca["regenerated"]["items_sha256_equals_manifest"] and ca["regenerated"]["assignment_draws_equal_the_committed_record"]
ca["assignment_seed_plus_one"] = regen["assignment_seed_plus_one"]
ca["world_seed_plus_one"] = regen["world_seed_plus_one"]

# the record, in the draft's shape as far as it goes
C = regen["constants"]
COMMON = ("\nThe frozen roster lists these eligible {member_type} identities, in recorded order: {members}. "
          "Recorded {criterion} scores, in the same order: {scores}. The reference {set_ref} resolves uniquely to this "
          "finite, nonempty snapshot of distinct identities. The snapshot was fixed before any selection, and {outsider} "
          "is not in it. Nothing else has been required of the selection, and no outcome has been observed yet.") + C["dedup"]


def template(form, frame):
    head = C["frames"][frame] + COMMON + "\nRequest: "
    return {"english": head + re.sub(r"\bS\b", "{set_ref}", C["spans"][form]), "ainglish": head + form + "({set_ref})."}


def dimension(name, definition, paths, key_of, procedure):
    groups = {}
    for i in real:
        key = key_of(i)
        groups.setdefault(G.canonical(key), {"id": "sha256:" + G.digest(key), "key": key, "members": []})["members"].append(i["id"])
    return {"id": name, "definition": definition, "basis": {"source_paths": paths, "procedure": procedure},
            "membership_mode": "partition", "groups": [groups[k] for k in sorted(groups)]}


frame_no = lambda i: int(i["frame_family"].rsplit("-", 1)[1])
record = {
    "kind": "example.ainglish.membership-record.draft0", "status": "discussion_only",
    "source": {"packet_bank_key": "choose-any-replica", "manifest_sha256": hashlib.sha256(raw).hexdigest(),
               "items_sha256": manifest["items_sha256"], "items_path": None, "item_id_field": "id", "unit": "complete_test_set_item",
               # not in draft 0: where the items are, and which of them the dimensions are about
               "items_locator": {"url": manifest["items_url"], "file_sha256": hashlib.sha256(items_raw).hexdigest()},
               "population": {"rule": "items that carry the manifest's settlement_item_field", "field": field,
                              "inside": len(real), "outside": len(cal), "outside_are": "planted calibration items"}},
    "declaration": {"author": "Reticuli", "timing": "post_outcome_projection",
                    "timing_basis": "Written on 2026-11-12, after the bank's result was filed. The generator and its seeds were committed before the mint; this record was not."},
    "construction": {"mode": "seeded_generator",
                     "description": "144 world skeletons (6 domains x 24, sizes 2 to 8, 12 frames, 6 tasks per domain) are fixed by the code. One seed draws the names, scores and orders inside each world; a second seed deals the worlds to the two forms by rejection sampling under balance rules.",
                     "seed_state": "two_bank_seeds_and_one_run_seed",
                     "seed_basis": "World seed and assignment seed are constants of the generator at the pinned commit. The manifest's own seed is the run seed and is neither of them.",
                     # not in draft 0
                     "generator": {"path": folder + "/my_instrument.py", "commit": commit,
                                   "sha256": hashlib.sha256(show(commit, folder + "/my_instrument.py")).hexdigest(),
                                   "reads": [{"expects": "../pkg/rendering-contract.json", "published_as": folder + "/rendering-contract-source.json",
                                              "sha256": hashlib.sha256(contract).hexdigest()}],
                                   "regenerates_committed_items_on": regen["python"]},
                     "seeds": [{"name": "world", "value": regen["seeds"]["world"], "decides": "names, scores, weighted member and option orders inside each world; the text of every calibration item", "stream": "one per world, keyed by seed and world id"},
                               {"name": "assignment", "value": regen["seeds"]["assignment"], "decides": "which form each world is rendered in", "stream": "one for the whole bank, with rejection", "draws": regen["assignment_draws"]},
                               {"name": "run", "value": manifest["seed"], "decides": "the deal of arms to readers and the resampling; nothing in the bank", "stream": "the harness's"}]},
    "dimensions": [
        dimension("form", "Literal committed settlement stratum. Its membership is the outcome of the seeded assignment.", ["items[].settlement_stratum"], lambda i: i[field], "field"),
        dimension("domain", "Literal committed domain label.", ["items[].domain"], lambda i: i["domain"], "field"),
        dimension("frame", "Literal committed frame family: which of twelve opening sentences the item carries.", ["items[].frame_family"], lambda i: i["frame_family"], "field"),
        dimension("member_count", "Literal committed size of the item's set.", ["items[].member_count"], lambda i: i["member_count"], "field"),
        dimension("rendering_template", "Exact complete English and marked string templates; one per form and frame.", ["items[].english", "items[].ainglish"], lambda i: template(i[field], frame_no(i)), "template"),
    ]}
json.dump(record, open(os.path.join(HERE, "record_choose_any.json"), "w"), indent=1, ensure_ascii=False)
BASIS = {"form": ("field", field), "domain": ("field", "domain"), "frame": ("field", "frame_family"),
         "member_count": ("field", "member_count"), "rendering_template": ("template",)}
real_ids = [i["id"] for i in real]
try:
    G.structure(record, [i["id"] for i in items])
    over_all = "accepted"
except G.Refused as e:
    over_all = "refused: " + str(e)
assert over_all.startswith("refused")
G.structure(record, real_ids)
sizes = G.replay(record, real, lambda i: i["id"], BASIS)
cross = collections.Counter((i[field], i["frame_family"]) for i in real)
per_form = {f: sorted(n for (form, _), n in cross.items() if form == f) for f in C["forms"]}
assert sizes["rendering_template"] == sorted(cross.values())
# controls on the template replay for this bank
d = json.loads(json.dumps(record))
t = next(x for x in d["dimensions"] if x["id"] == "rendering_template")
t["groups"][0]["members"][0], t["groups"][1]["members"][0] = t["groups"][1]["members"][0], t["groups"][0]["members"][0]
try:
    G.replay(d, real, lambda i: i["id"], BASIS)
    swap = None
except G.Refused as e:
    swap = str(e)
assert swap
ca["record"] = {"digest": G.digest(record), "dimensions": len(record["dimensions"]), "assignments": len(real) * len(record["dimensions"]),
                "partition_over_all_%d_items" % len(items): over_all, "partition_over_the_%d_real_items" % len(real): "accepted",
                "generic_replay_passes": True, "group_sizes": {k: v for k, v in sizes.items() if k != "rendering_template"},
                "templates": len(sizes["rendering_template"]), "templates_per_form": {f: len(v) for f, v in per_form.items()},
                "template_group_sizes_per_form": per_form, "swap_control_refused": swap}
code, so, se = run(os.path.join(HERE, "ladder.py"), PACKET, os.path.join(HERE, "record_choose_any.json"),
                   os.path.join(SRC, "choose-any-manifest.json"), os.path.join(SRC, "choose-any-items.json"))
assert code == 0, se[-600:]
ca["packet_check_ladder"] = json.loads(so)
assert ca["packet_check_ladder"][-1]["check"] == "accepted" and all(s["check"] != "accepted" for s in ca["packet_check_ladder"][:-1])

# ---------------------------------------------------------------- include-both: a seed that draws no real item
raw, manifest = load("include-both-manifest.json")
items_raw, items = load("include-both-items.json")
commit, folder = at_commit(manifest)
with tempfile.TemporaryDirectory() as tree:
    os.makedirs(os.path.join(tree, folder))
    gen = os.path.join(tree, folder, "gen_items.py")
    open(gen, "wb").write(show(commit, folder + "/gen_items.py"))
    code, so, se = run(os.path.join(HERE, "regen.py"), "include-both", gen)
    assert code == 0, se[-600:]
    regen = json.loads(so)
assert regen["items_sha256"] == manifest["items_sha256"] == G.digest(items)
frames = collections.Counter((i["settlement_stratum"], i["frame"]) for i in items if not i.get("calibration"))
out["include_both"] = {"manifest_sha256": hashlib.sha256(raw).hexdigest(), "items_url_commit": commit,
                       "regenerated_items_sha256_equals_manifest": True, "python": regen["python"],
                       "bank_seed": regen["seeds"]["bank"], "manifest_seed": manifest["seed"],
                       "one_number_two_jobs": regen["seeds"]["bank"] == manifest["seed"],
                       "frames_per_form": sorted(collections.Counter(f for f, _ in frames).values()),
                       "bank_seed_plus_one": regen["bank_seed_plus_one"]}

# ---------------------------------------------------------------- no-undo: no item ids, a renderer for the English arm
raw, manifest = load("noundo-manifest.json")
ts = manifest["test_set"]
assert G.digest(ts) == manifest["items_sha256"]
can = [i for i in ts if i["stratum"] == "can-undo"]
plain = {"english": "{action}; I cannot reverse this.", "ainglish": "{action}, no-undo."}
one = {"english": "{action}; I can reverse this via {path}.", "ainglish": "{action}, can-undo({path})."}
window = [i for i in can if re.search(r"; \d+[dh][;)]", i["ainglish"])]
out["no_undo"] = {
    "manifest_sha256": hashlib.sha256(raw).hexdigest(), "items": len(ts), "items_with_an_id_field": sum(1 for i in ts if "id" in i),
    "stratum_by_shape": {"%s/%s" % k: v for k, v in sorted(collections.Counter((i["stratum"], i["shape"]) for i in ts).items())},
    "no_undo_items_fitting_one_shared_slot_template": sum(1 for i in ts if i["stratum"] == "no-undo" and G.read_through(plain, i)),
    "can_undo_items": len(can), "can_undo_items_fitting_the_path_only_template": sum(1 for i in can if G.read_through(one, i) and ";" not in G.read_through(one, i)["path"]),
    "can_undo_items_whose_window_is_written_differently_in_the_two_arms": len(window),
    "example": {"ainglish": window[0]["ainglish"], "english": window[0]["english"]},
    "renderer_pinned_in_the_manifest": bool(re.search(r"renderer \S+ sha256 [0-9a-f]{64}", manifest["comparison_identity"]["comparator"]))}

# ---------------------------------------------------------------- how common: item ids across my stored token banks
if STORED:
    rows = {}
    for p in sorted(glob.glob(os.path.join(STORED, "*.json"))):
        m = json.load(open(p))
        if isinstance(m.get("test_set"), list) and m["test_set"] and m.get("metric") == "token_delta":
            keys = set().union(*(set(i) for i in m["test_set"] if isinstance(i, dict)))
            rows[os.path.basename(p)[:-5]] = "id" if "id" in keys else "other id field" if any(k.endswith("_id") for k in keys) else "none"
    # each file is GET /api/v1/attempts/<attempt id>/manifest for one of my measurement rows, saved under the attempt id
    out["my_stored_token_banks"] = {"with_items_inline": len(rows), **{k: v for k, v in sorted(collections.Counter(rows.values()).items())},
                                    "item_id_field_by_attempt": rows}
json.dump(out, open(os.path.join(HERE, "results_b.json"), "w"), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
