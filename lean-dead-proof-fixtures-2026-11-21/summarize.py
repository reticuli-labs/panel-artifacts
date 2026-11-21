"""summarize.py: read what the two toolchains printed (out/<toolchain>/) and what the authors' tool listed, and write
results.json: one entry per statement I make about these fixtures, each derived here and asserted. If an output changes so that
a statement no longer holds, this script stops at that statement. It runs nothing and reads only files under out/."""
import json, os, re, sys
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
T = ("4.36.0", "4.9.0")


def reader(tag, name, v, a="1"):
    """-> (commands, roots, exit). commands: [(first line, [added names])]; roots: {name: {"reach": [...], "axioms": [...]} or None}."""
    t = open("out/%s/%s_%s.async%s.txt" % (tag, name, v, a), encoding="utf-8").read(); cmds, roots = [], {}
    for l in t.split("\n"):
        m = re.match(r"^\[(\d+)\] (.*)$", l)
        if m: cmds.append((m.group(2), [])); continue
        m = re.match(r"^      \+ (\S+) \((\w+)\)$", l)
        if m: cmds[-1][1].append(m.group(1)); continue
        m = re.match(r"^ROOT (\S+) \(\w+\) reaches in this file: \[(.*)\]$", l)
        if m: roots.setdefault(m.group(1), {})["reach"] = [x for x in m.group(2).split(", ") if x]; continue
        m = re.match(r"^ROOT (\S+) axioms: \[(.*)\]$", l)
        if m: roots.setdefault(m.group(1), {})["axioms"] = [x for x in m.group(2).split(", ") if x]; continue
        m = re.match(r"^ROOT (\S+): not a constant", l)
        if m: roots[m.group(1)] = None
    assert "constants of this file at the end" in t and t.strip().endswith("exit code 0"), (tag, name, v, a)
    return cmds, roots


def builds(tag, name, v):
    t = open("out/%s/%s_%s.build.txt" % (tag, name, v), encoding="utf-8").read(); m = re.search(r"exit code (\d+)\s*\Z", t); return m.group(1) == "0"               # the last thing in the file (a trace may end without a newline before it)


def where(cmds, const):
    """the first line of the command under which the reader first saw `const`, or None"""
    hit = [c for c, added in cmds if const in added]; assert len(hit) <= 1; return hit[0] if hit else None


def last(name):                                  # a name as printed, without the module prefix an older toolchain puts in front
    return name.split(".")[-2] + "." + name.split(".")[-1] if "._auxLemma." in name else name


R = {"toolchains": list(T), "statements": {}}; S = R["statements"]
ule = {t: {lab: json.load(open("out/%s/%s_results.json" % (t, lab), encoding="utf-8")) for lab in ("ule", "keepint")} for t in T}

# 0. the control: where the target does use a sorried lemma, the reader says so
for t in T:
    _, r = reader(t, "F0", "with"); assert "lemma1" in r["target"]["reach"] and r["target"]["axioms"] == ["sorryAx"] and r["unused"]["reach"] == []
S["control_reader_lists_a_used_lemma_and_sorry"] = True

# 1. constants made at first use
for t in T:
    cw, rw = reader(t, "F1", "with"); co, ro = reader(t, "F1", "without")
    assert where(cw, "f") .startswith("def f") and where(cw, "f.match_1").startswith("def f")                  # the reader does file what a definition makes under the definition
    for eq in ("f.eq_1", "f.eq_2"):
        assert where(cw, eq).startswith("theorem dead") and where(co, eq).startswith("theorem target"), (t, eq)
    assert sorted(rw["target"]["reach"]) == sorted(ro["target"]["reach"]) and {"f.eq_1", "f.eq_2"} <= set(rw["target"]["reach"])
    assert builds(t, "F1", "with") and builds(t, "F1", "without")
    u = ule[t]["ule"]["F1"]; assert "dead" in u["with"]["dead"] and {"f.eq_1", "f.eq_2"} <= set(u["with"]["live"]) and u["minimized"]["builds"]
S["c1_equation_theorems_appear_in_the_first_askers_command"] = {t: True for t in T}

# 2. renumbering, and sharing
c, rw = reader("4.9.0", "F2a", "with"); _, ro = reader("4.9.0", "F2a", "without")
aw = [last(x) for x in rw["target"]["reach"] if "_auxLemma" in x]; ao = [last(x) for x in ro["target"]["reach"] if "_auxLemma" in x]
assert aw == ["_auxLemma.2"] and ao == ["_auxLemma.1"], (aw, ao)
S["c2_counter_over_the_file"] = {"4.9.0": {"target_with_dead": aw[0], "target_without_dead": ao[0]}}
for a, want in (("1", "target._simp_1_1"), ("0", "target._simp_1")):
    _, rw = reader("4.36.0", "F2a", "with", a); _, ro = reader("4.36.0", "F2a", "without", a)
    assert sorted(rw["target"]["reach"]) == sorted(ro["target"]["reach"]) == ["Q", "nq", want], (a, rw["target"])
S["c2_counter_over_the_file"]["4.36.0"] = {"target_with_dead": "target._simp_1_1", "target_without_dead": "target._simp_1_1", "with_async_off": "target._simp_1"}
sh = {}
for t in T:
    _, rw = reader(t, "F2d", "with"); _, ro = reader(t, "F2d", "without")
    assert rw["liveM"]["reach"] == ["deadM.match_1"] and ro["liveM"]["reach"] == ["liveM.match_1"]
    u = ule[t]["ule"]["F2d"]["with"]; assert "deadM.match_1" in u["live"] and "deadM" in u["dead"]
    _, rw = reader(t, "F2c", "with"); _, ro = reader(t, "F2c", "without")
    sh[t] = {"match_shared_between_definitions": True, "proof_shared_between_definitions": rw["liveD"]["reach"] != ro["liveD"]["reach"], "liveD_with_dead": rw["liveD"]["reach"]}
    _, r1 = reader(t, "F2e", "with", "1"); _, r0 = reader(t, "F2e", "with", "0"); sh[t]["match_shared_between_theorems"] = {"async_on": "deadT" in r1["target"]["reach"][0], "async_off": "deadT" in r0["target"]["reach"][0]}
assert sh["4.36.0"]["proof_shared_between_definitions"] and sh["4.36.0"]["liveD_with_dead"] == ["deadD._proof_1"] and not sh["4.9.0"]["proof_shared_between_definitions"]
assert sh["4.36.0"]["match_shared_between_theorems"] == {"async_on": False, "async_off": True} and sh["4.9.0"]["match_shared_between_theorems"]["async_on"]
S["c2_sharing"] = sh

# 3. the compiler channel
cc = {}
for t in T:
    _, rw = reader(t, "F3a", "with"); _, ro = reader(t, "F3a", "without")
    assert "slow_eq_fast" not in rw["target"]["reach"] and rw["target"]["axioms"] == ro["target"]["axioms"] and rw["target"]["axioms"] and builds(t, "F3a", "with") and builds(t, "F3a", "without")
    u = ule[t]["ule"]["F3a"]; assert "slow_eq_fast" in u["with"]["dead"] and u["minimized"]["builds"]
    _, rw = reader(t, "F3c", "with")
    assert builds(t, "F3c", "with") and not builds(t, "F3c", "without") and rw["slow_eq_fast"]["axioms"] == ["sorryAx"] and "sorryAx" not in rw["target"]["axioms"] and "slow_eq_fast" not in rw["target"]["reach"]
    _, rw = reader(t, "F3d", "with"); assert builds(t, "F3d", "with") and not builds(t, "F3d", "without") and "hImpl" not in rw["target"]["reach"] and "sorryAx" not in rw["target"]["axioms"]
    for lab in ("ule", "keepint"):
        u = ule[t][lab]; assert "slow_eq_fast" in u["F3c"]["with"]["dead"] and not u["F3c"]["minimized"]["builds"] and "hImpl" in u["F3d"]["with"]["dead"] and not u["F3d"]["minimized"]["builds"]
    cc[t] = {"csimp_lemma_not_reached_axioms_equal": True, "false_csimp_lemma_by_sorry_target_builds_without_sorryAx": True, "implemented_by_at_the_definition": True,
             "implemented_by_in_a_later_attribute_command_takes_effect": builds(t, "F3b", "with"), "target_axioms": rw["target"]["axioms"]}
assert cc["4.36.0"]["implemented_by_in_a_later_attribute_command_takes_effect"] is False and cc["4.9.0"]["implemented_by_in_a_later_attribute_command_takes_effect"] is True
S["c3_compiler_channel"] = cc; S["c3_extern"] = "not tested"

# 4. found by the run: the extractor skips internal names
for t in T:
    for f in ("F2a", "F2b"):
        u, k = ule[t]["ule"][f], ule[t]["keepint"][f]
        assert "nq" in u["with"]["dead"] and u["with"]["graph"]["target"] == ["Q"] and not u["minimized"]["builds"], (t, f)
        assert "nq" in k["with"]["live"] and k["minimized"]["builds"] and "nq" not in k["with"]["graph"]["target"], (t, f)
        via = [n for n in k["with"]["graph"]["target"] if "nq" in k["with"]["graph"].get(n, [])]; assert len(via) == 1 and ("_simp_" in via[0] or "_auxLemma" in via[0]), via
    assert "nq" in ule[t]["ule"]["F2a"]["minimized"]["first_line"] and "nknown identifier" in ule[t]["ule"]["F2a"]["minimized"]["first_line"] and "unsolved goals" in ule[t]["ule"]["F2b"]["minimized"]["first_line"]
    assert "hImpl" in ule[t]["ule"]["F3d"]["minimized"]["first_line"] and "nknown constant" in ule[t]["ule"]["F3d"]["minimized"]["first_line"]
S["found_internal_names_skipped"] = {t: {"nq_listed_dead": True, "kept_file_builds": False, "with_the_skip_taken_out_kept_file_builds": True} for t in T}

# counts, their tool as published, per toolchain
cnt = {}
for t in T:
    u = ule[t]["ule"]; b = sorted(f for f in u if u[f].get("with", {}).get("builds")); fails = sorted(f for f in b if not u[f]["minimized"]["builds"])
    cnt[t] = {"fixture_files_that_build": len(b), "kept_file_does_not_build": fails}
assert cnt["4.36.0"] == {"fixture_files_that_build": 10, "kept_file_does_not_build": ["F2a", "F2b", "F3c", "F3d"]}, cnt
S["counts_their_tool"] = cnt
json.dump(R, open("results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False); print(json.dumps(cnt)); print("every statement holds; results.json written")
