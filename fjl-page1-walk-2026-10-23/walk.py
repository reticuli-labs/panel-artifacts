"""walk.py: my own implementation of Facet Judgment Layer page 1 (v0.1, text sha256 8752c5b0…) section 6, run on the section-10 vectors as I read them, then the section-7 re-walk. No network. Two readings of the budget stop are implemented: STOP_RULE 'would_pass' (stop when the NEXT path/inspection would exceed the budget) and 'reached' (stop as soon as the count equals the budget)."""
import json, itertools, unicodedata, hashlib, re, sys
class Reject(Exception): pass
EDGE_KEYS = {"witness", "facet", "subject", "evidence", "package"}; BRIDGE_KEYS = {"witness", "their_facet", "my_facet", "weight", "evidence"}
VERDICT_KEYS = {"reader", "facet", "subject", "floor", "depth", "decay", "min_cut", "stop", "verdict", "chains", "edge_budget", "path_budget", "loss", "walked_at"}
AGG = {"score", "total", "rating", "trust", "index", "facets", "grade", "rank", "confidence"}
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"); HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$"); T_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
def facet_ok(s): return isinstance(s, str) and 1 <= len(s) <= 64 and s != "*" and unicodedata.normalize("NFC", s) == s
def pointer_ok(p, bytes_by_url=None):
    if not isinstance(p, dict): return False
    if p.get("kind") == "aer1": return set(p) == {"kind", "id"} and isinstance(p.get("id"), str) and bool(UUID_RE.match(p["id"]))
    if p.get("kind") == "url-hash":
        if set(p) != {"kind", "url", "hash"} or not isinstance(p.get("url"), str) or not re.match(r"^[a-z][a-z0-9+.-]*://", p["url"]) or not isinstance(p.get("hash"), str) or not HASH_RE.match(p["hash"]): return False
        if bytes_by_url is not None and p["url"] in bytes_by_url: return "sha256:" + hashlib.sha256(bytes_by_url[p["url"]]).hexdigest() == p["hash"]
        return True
    return False
def check_edge(e, bytes_by_url=None):
    if not isinstance(e, dict): return "bad_shape"
    if set(e) & AGG: return "aggregate"
    if not set(e) <= EDGE_KEYS: return "bad_key"
    if not {"witness", "facet", "subject", "evidence"} <= set(e): return "bad_shape"
    if not facet_ok(e["facet"]): return "bad_facet"
    if e["witness"] == e["subject"]: return "self_edge"
    if not pointer_ok(e["evidence"], bytes_by_url): return "bad_evidence"
    if "package" in e and not (isinstance(e["package"], str) or pointer_ok(e["package"])): return "bad_evidence"
    return None
def check_bridge(b, reader):
    if not isinstance(b, dict) or not set(b) <= BRIDGE_KEYS: return "bad_key"
    if not {"witness", "their_facet", "my_facet", "weight"} <= set(b): return "bad_shape"
    if b["witness"] != reader: return "not_reader"
    if not (facet_ok(b["their_facet"]) and facet_ok(b["my_facet"]) and b["their_facet"] != b["my_facet"]): return "bad_facet"
    if not (num(b["weight"]) and 0 < b["weight"] <= 1): return "bad_weight"
    if "evidence" in b and not pointer_ok(b["evidence"]): return "bad_evidence"
    return None
def check_verdict(v):
    if not isinstance(v, dict): return "bad_shape"
    if set(v) & AGG: return "aggregate"
    if not set(v) <= VERDICT_KEYS: return "bad_key"
    if "loss" not in v: return "loss_omitted"
    if not (isinstance(v.get("walked_at"), str) and T_RE.match(v["walked_at"])): return "bad_time"
    if v["loss"] != "unassigned" and any(h["role"] == "edge" and h["witness"] == v["loss"] for c in v.get("chains", []) for h in c["hops"]): return "loss_is_witness"
    return None
def internal(path, reader, subject):
    s = set()
    for h in path: s.add(h["witness"]); s.add(h["subject"])
    return s - {reader, subject}
def max_disjoint(paths, reader, subject):
    nodes = [internal(p, reader, subject) for p in paths]; n = len(paths)
    for k in range(n, 0, -1):
        for combo in itertools.combinations(range(n), k):  # lexicographic = caller (discovery) order first
            seen = set(); ok = True
            for i in combo:
                if nodes[i] & seen: ok = False; break
                seen |= nodes[i]
            if ok: return k, list(combo)
    return 0, []
class _Stop(Exception): pass
def walk(reader, roots, edges, bridges, facet, subject, floor, depth, decay, walked_at, edge_budget=None, path_budget=None, bytes_by_url=None, stop_rule="would_pass"):
    if not (isinstance(floor, int) and floor >= 2): raise Reject("bad_floor")
    if not (isinstance(depth, int) and depth >= 1): raise Reject("bad_depth (page names no code)")
    if not (num(decay) and 0 < decay <= 1): raise Reject("bad_decay (page names no code)")
    for b in (edge_budget, path_budget):
        if b is not None and not (isinstance(b, int) and b >= 1): raise Reject("bad_budget")
    if not facet_ok(facet): raise Reject("bad_facet")
    dropped = []; E = []; B = []
    for i, e in enumerate(edges):
        c = check_edge(e, bytes_by_url); (dropped.append(("edge", i, c)) if c else E.append(e))
    for i, b in enumerate(bridges):
        c = check_bridge(b, reader); (dropped.append(("bridge", i, c)) if c else B.append(b))
    bridge_for = {}
    for b in B:
        if b["my_facet"] == facet and b["their_facet"] not in bridge_for: bridge_for[b["their_facet"]] = b
    def entering(e):
        if e["facet"] == facet: return None, True
        if e["facet"] in bridge_for: return bridge_for[e["facet"]], True
        return None, False
    paths = []; st = {"inspections": 0, "stop": None}
    def record(path):
        if path_budget is not None and stop_rule == "would_pass" and len(paths) + 1 > path_budget: st["stop"] = "capped"; raise _Stop()
        paths.append(path); k, _ = max_disjoint(paths, reader, subject)
        if k >= floor: st["stop"] = "floor_met"; raise _Stop()
        if path_budget is not None and stop_rule == "reached" and len(paths) >= path_budget: st["stop"] = "capped"; raise _Stop()
    def dfs(node, hops, visited):
        if len(hops) >= depth: return
        for e in E:
            if e["witness"] != node: continue
            br, ok = entering(e)
            if not ok: continue
            if edge_budget is not None and stop_rule == "would_pass" and st["inspections"] + 1 > edge_budget: st["stop"] = "capped"; raise _Stop()
            st["inspections"] += 1; last = edge_budget is not None and stop_rule == "reached" and st["inspections"] >= edge_budget
            if e["subject"] in visited:
                if last: st["stop"] = "capped"; raise _Stop()
                continue
            hop = {"role": "edge", "witness": e["witness"], "facet": facet, "subject": e["subject"], "evidence": e["evidence"], "applied_discount": (br["weight"] if br else 1) * decay}
            if br: hop["source_facet"] = e["facet"]; hop["bridge_weight"] = br["weight"]
            if "package" in e: hop["package"] = e["package"]
            if e["subject"] == subject:
                record(hops + [hop])
                if last: st["stop"] = "capped"; raise _Stop()
                continue
            if last: st["stop"] = "capped"; raise _Stop()
            dfs(e["subject"], hops + [hop], visited | {e["subject"]})
    try:
        seen_roots = set()
        for r in roots:
            if r == reader or r in seen_roots: continue
            seen_roots.add(r); root_hop = {"role": "root", "witness": reader, "facet": facet, "subject": r, "applied_discount": 1}
            if r == subject: record([root_hop]); continue
            dfs(r, [root_hop], {reader, r})
        st["stop"] = "complete"
    except _Stop: pass
    k, sel = max_disjoint(paths, reader, subject); stop = st["stop"]
    if stop == "floor_met": chains = [paths[i] for i in sel]; verdict = "admitted"
    elif stop == "complete": chains = paths; verdict = "insufficient_evidence"
    else: chains = paths; verdict = "unresolved"
    disc = lambda p: __import__("functools").reduce(lambda a, h: a * h["applied_discount"], p, 1.0)
    v = {"reader": reader, "facet": facet, "subject": subject, "floor": floor, "depth": depth, "decay": decay, "min_cut": k, "stop": stop, "verdict": verdict, "chains": [{"hops": p, "chain_discount": disc(p)} for p in chains], "loss": "unassigned", "walked_at": walked_at}
    if edge_budget is not None: v["edge_budget"] = edge_budget
    if path_budget is not None: v["path_budget"] = path_budget
    v["_dropped"] = dropped; v["_inspections"] = st["inspections"]; v["_paths_found"] = len(paths)
    return v
def rewalk(v, stop_rule):
    """Section 7: re-walk the PUBLISHED chains under the published parameters. Roots, edges and bridges are what the chains carry; nothing dark."""
    roots = []; edges = []; bridges = []
    for c in v["chains"]:
        for h in c["hops"]:
            if h["role"] == "root":
                if h["subject"] not in roots: roots.append(h["subject"])
            else:
                e = {"witness": h["witness"], "facet": h.get("source_facet", h["facet"]), "subject": h["subject"], "evidence": h["evidence"]}
                if e not in edges: edges.append(e)
                if "bridge_weight" in h:
                    b = {"witness": v["reader"], "their_facet": h["source_facet"], "my_facet": h["facet"], "weight": h["bridge_weight"]}
                    if b not in bridges: bridges.append(b)
    return walk(v["reader"], roots, edges, bridges, v["facet"], v["subject"], v["floor"], v["depth"], v["decay"], v["walked_at"], v.get("edge_budget"), v.get("path_budget"), stop_rule=stop_rule)
# ---------------- fixtures as I read section 10 (reader R, subject S, facet f, aer1 pointers) ----------------
_n = [0]
def ptr():
    _n[0] += 1; return {"kind": "aer1", "id": f"00000000-0000-4000-8000-{_n[0]:012d}"}
def ed(w, s, facet="f", **kw): d = {"witness": w, "facet": facet, "subject": s, "evidence": ptr()}; d.update(kw); return d
W = "2026-10-23T11:00:00Z"
def base(**kw):
    d = dict(reader="R", roots=["A", "B"], edges=[], bridges=[], facet="f", subject="S", floor=2, depth=3, decay=1, walked_at=W); d.update(kw); return d
FX = [
 ("ring-outside", base(roots=[], edges=[ed("X", "Y"), ed("Y", "X"), ed("X", "S")]), dict(stop="complete", verdict="insufficient_evidence", min_cut=0, chains=0)),
 ("one-chain", base(roots=["A"], edges=[ed("A", "S")]), dict(stop="complete", verdict="insufficient_evidence", min_cut=1)),
 ("two-disjoint", base(edges=[ed("A", "S"), ed("B", "S")]), dict(stop="floor_met", verdict="admitted", min_cut=2)),
 ("shared-node", base(edges=[ed("A", "M"), ed("B", "M"), ed("M", "S")]), dict(stop="complete", verdict="insufficient_evidence", min_cut=1, chains=2)),
 ("floor-met", base(roots=["A", "B", "C"], edges=[ed("A", "S"), ed("B", "S"), ed("C", "S")]), dict(stop="floor_met", verdict="admitted", roots_published=["A", "B"])),
 ("caller-order", base(roots=["C", "B", "A"], edges=[ed("A", "S"), ed("B", "S"), ed("C", "S")]), dict(stop="floor_met", verdict="admitted", roots_published=["C", "B"])),
 ("order-flip", base(edges=[ed("A", "M"), ed("M", "S"), ed("B", "S")]), dict(stop="floor_met", min_cut=2)),
 ("shared-then-disjoint", base(roots=["A", "B", "C"], edges=[ed("A", "M"), ed("B", "M"), ed("M", "S"), ed("C", "S")]), dict(stop="floor_met", roots_published=["A", "C"])),
 ("capped", base(roots=["A", "B", "C"], edges=[ed("A", "S"), ed("B", "S"), ed("C", "S")], path_budget=1), dict(stop="capped", verdict="unresolved", min_cut=1)),
 ("floor-before-budget", base(roots=["A", "B", "C"], edges=[ed("A", "S"), ed("B", "S"), ed("C", "S")], path_budget=3), dict(stop="floor_met", chains=2)),
 ("other-facet", base(roots=["A"], edges=[ed("A", "S", facet="g")]), dict(min_cut=0)),
 ("star-facet (edge)", base(roots=["A"], edges=[ed("A", "S", facet="*")]), dict(min_cut=0, dropped="bad_facet")),
 ("overall-rating", base(roots=["A"], edges=[{"witness": "A", "subject": "S", "evidence": ptr(), "facets": {"f": 1}}, {"witness": "A", "subject": "S", "evidence": ptr(), "rating": 1}]), dict(min_cut=0, dropped="aggregate")),
 ("reader-bridge", base(edges=[ed("A", "S", facet="wages"), ed("B", "S", facet="wages")], bridges=[{"witness": "R", "their_facet": "wages", "my_facet": "labor", "weight": 0.5}], facet="labor"), dict(stop="floor_met", min_cut=2, discount=0.5)),
 ("witness-bridge", base(edges=[ed("A", "S", facet="wages"), ed("B", "S", facet="wages")], bridges=[{"witness": "X", "their_facet": "wages", "my_facet": "labor", "weight": 0.5}], facet="labor"), dict(min_cut=0)),
 ("bridge-compose", base(roots=["A"], edges=[ed("A", "S", facet="a")], bridges=[{"witness": "R", "their_facet": "a", "my_facet": "b", "weight": 1}, {"witness": "R", "their_facet": "b", "my_facet": "c", "weight": 1}], facet="c"), dict(min_cut=0)),
 ("self-edge", base(roots=["A"], edges=[ed("A", "A"), ed("A", "S")]), dict(dropped="self_edge", min_cut=1)),
 ("cycle", base(roots=["A"], edges=[ed("A", "M", facet="g"), ed("M", "N", facet="g"), ed("N", "M", facet="g"), ed("N", "S", facet="g")], bridges=[{"witness": "R", "their_facet": "g", "my_facet": "f", "weight": 1}], depth=4), dict(min_cut=1, chains=1)),
 ("depth", base(edges=[ed("A", "S"), ed("B", "M"), ed("M", "S")], depth=2), dict(min_cut=1, chains=1)),
 ("dark-cone", base(edges=[ed("A", "S"), ed("B", "X")]), dict(min_cut=1, chains=1, roots_published=["A"])),
 ("decay (root+1 edge hop)", base(roots=["A"], edges=[ed("A", "S")], decay=0.5), dict(discount=0.5)),
 ("decay (root+2 edge hops)", base(roots=["A"], edges=[ed("A", "M"), ed("M", "S")], decay=0.5), dict(discount=0.25)),
 ("bad-pointer (no hash)", base(roots=["A"], edges=[{"witness": "A", "facet": "f", "subject": "S", "evidence": {"kind": "url-hash", "url": "https://x/y"}}]), dict(dropped="bad_evidence")),
 ("bad-pointer (mismatch)", base(roots=["A"], edges=[{"witness": "A", "facet": "f", "subject": "S", "evidence": {"kind": "url-hash", "url": "https://x/y", "hash": "sha256:" + "0" * 64}}], bytes_by_url={"https://x/y": b"abc"}), dict(dropped="bad_evidence")),
]
REJ = [("floor-one", base(floor=1)), ("bad-budget", base(path_budget=0)), ("star-facet (walk facet)", base(facet="*"))]
def summarize(v): return dict(stop=v["stop"], verdict=v["verdict"], min_cut=v["min_cut"], chains=len(v["chains"]), roots_published=[c["hops"][0]["subject"] for c in v["chains"]], discount=[round(c["chain_discount"], 9) for c in v["chains"]], dropped=[d[2] for d in v["_dropped"]], inspections=v["_inspections"])
def agree(exp, got):
    for k, x in exp.items():
        g = got[k]
        if k == "dropped": ok = x in g
        elif k == "discount": ok = all(abs(d - x) < 1e-9 for d in g) and g
        else: ok = g == x
        if not ok: return False, k
    return True, None
out = {"fixtures": {}, "rejects": {}, "rewalks": {}}
for rule in ("would_pass", "reached"):
    print(f"\n================ STOP_RULE = {rule}")
    n_ok = 0
    for name, args, exp in FX:
        v = walk(stop_rule=rule, **args); g = summarize(v); ok, why = agree(exp, g); n_ok += ok
        out["fixtures"][f"{rule}:{name}"] = {"got": g, "expected": exp, "agree": ok, "why": why}
        print(f"{'OK ' if ok else 'XX '} {name:28} stop={g['stop']:10} verdict={g['verdict']:22} min_cut={g['min_cut']} chains={g['chains']} roots={g['roots_published']} disc={g['discount']} dropped={g['dropped']} insp={g['inspections']}" + ("" if ok else f"   <-- differs on {why}: expected {exp[why]}"))
    print(f"fixtures agreeing with the page's stated outcome: {n_ok}/{len(FX)}")
    for name, args in REJ:
        try: walk(stop_rule=rule, **args); r = "NO REJECT"
        except Reject as e: r = f"Reject {e}"
        out["rejects"][f"{rule}:{name}"] = r; print(f"   {name:28} -> {r}")
    # section 7 re-walks
    print("--- section 7 re-walk of each verdict from its PUBLISHED chains only (section 9: the dark cone is not available to the re-walker)")
    for name, args, exp in FX:
        if "(" in name and "decay" not in name: continue
        v = walk(stop_rule=rule, **args)
        if not v["chains"] and v["stop"] != "capped": continue
        r = rewalk(v, rule); same = (r["stop"], r["verdict"], r["min_cut"], [c["hops"] for c in r["chains"]]) == (v["stop"], v["verdict"], v["min_cut"], [c["hops"] for c in v["chains"]])
        out["rewalks"][f"{rule}:{name}"] = {"original": (v["stop"], v["verdict"], v["min_cut"]), "rewalk": (r["stop"], r["verdict"], r["min_cut"]), "reproduced": same}
        print(f"   {'reproduced' if same else 'REFUTED   '} {name:28} original {v['stop']}/{v['verdict']}/min_cut {v['min_cut']} -> re-walk {r['stop']}/{r['verdict']}/min_cut {r['min_cut']}")
    # edge_budget capped case with a dark inspection before the last path
    eb = base(roots=["A", "B"], edges=[ed("A", "X"), ed("A", "S"), ed("B", "S")], edge_budget=2); v = walk(stop_rule=rule, **eb); r = rewalk(v, rule)
    same = (r["stop"], r["verdict"], r["min_cut"]) == (v["stop"], v["verdict"], v["min_cut"])
    out["rewalks"][f"{rule}:edge-budget-dark-inspection"] = {"original": (v["stop"], v["verdict"], v["min_cut"], v["_inspections"]), "rewalk": (r["stop"], r["verdict"], r["min_cut"], r["_inspections"]), "reproduced": same}
    print(f"   {'reproduced' if same else 'REFUTED   '} {'edge_budget 2, dark A->X first':28} original {v['stop']}/{v['verdict']}/min_cut {v['min_cut']} insp {v['_inspections']} -> re-walk {r['stop']}/{r['verdict']}/min_cut {r['min_cut']} insp {r['_inspections']}")
# verdict shape checks (section 4/8 and the sum-field vector)
v = walk(**base(edges=[ed("A", "S"), ed("B", "S")])); clean = {k: x for k, x in v.items() if not k.startswith("_")}
checks = {"clean": check_verdict(clean), "sum-field": check_verdict(dict(clean, score=1)), "loss omitted": check_verdict({k: x for k, x in clean.items() if k != "loss"}), "bad walked_at": check_verdict(dict(clean, walked_at="2026-10-23 11:00")), "loss = edge witness": check_verdict(dict(clean, loss="A")), "loss = reader": check_verdict(dict(clean, loss="R"))}
out["verdict_checks"] = checks; print("\nverdict checks:", checks)
json.dump(out, open("walk_results.json", "w"), indent=1, default=str)
print("\nsha256 of this script's subject text:", hashlib.sha256(open("text_fjl_p1_proposal.txt", "rb").read()).hexdigest())
