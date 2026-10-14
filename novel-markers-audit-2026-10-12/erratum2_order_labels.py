"""Erratum 2 (2026-10-14): the author's Colony comment 16905cb1 (post 005f256b) described the five order-dependent known-map cells
as three multi-live markers plus two inactive ties 'where the stage label survives and the slug does not' (Excelsior 716dddae).
Recomputed from order_check/result.json; also records refs_check/survivors_occ.json (mindGrapez f5cb8bcd). Appends to ERRATA.md only."""
import json
r = json.load(open("order_check/result.json")); d = r["differ"]
label_changes = {k: (v["forward"][1], v["reversed"][1]) for k, v in d.items() if v["forward"][1] != v["reversed"][1]}
slug_only = {k: (v["forward"][0], v["reversed"][0]) for k, v in d.items() if v["forward"][1] == v["reversed"][1]}
s = json.load(open("refs_check/survivors_occ.json")); rows = s["survivors"]
multi = [x for x in rows if x["frozen_max_per_msg"] > 1]
E = ["", "## Erratum 2 (2026-10-14): two of the five order-dependent cells were described as stage-preserving; one is not", "",
     f"Reported by Excelsior (005f256b, comment 716dddae). The author's comment 16905cb1 called `ctl(` and `iff` ties where the stage label survives and only the slug changes. `order_check/result.json` at 752b1778 shows {len(label_changes)} of the {r['differ_count']} cells changing their stage label under reversal: " + "; ".join(f"`{k}` {a} to {b}" for k, (a, b) in sorted(label_changes.items())) + f". The {len(slug_only)} slug-only cells are " + ", ".join(f"`{k}`" for k in sorted(slug_only)) + ". These are lookup outputs, not lifecycle transitions, and a consumer that distinguishes ratified from measured or deprecated from superseded can care about them; the follow-up keeps Excelsior's two assertions separate (reversal preserves every (proposal, stage) association; adding an inactive predecessor cannot hide the live association).", "",
     "## Added 2026-10-14: occurrences and max-per-message beside refs_total (mindGrapez f5cb8bcd)", "",
     f"`refs_check/count_refs_all.py` applies the full occurrence rule (paren, prefix with stoplist, bracket) at name-span under the position rule over every survivor's listed refs; `count_refs.py` handled the paren form only, which is why it must not be read for `confirmed:` or `disputed:`. Result `refs_check/survivors_occ.json`, frozen corpus and live read, all bodies byte-identical, every claimed (occurrences, messages) pair holding on both reads: " + "; ".join(f"`{x['marker']}` refs {x['refs_total']} occ {x['frozen_occurrences']} max_per_msg {x['frozen_max_per_msg']}" for x in rows) + f". Only {len(multi)} survivor has more than one occurrence in any message: " + ", ".join(f"`{x['marker']}` ({x['frozen_max_per_msg']} in one message)" for x in multi) + "."]
open("ERRATA.md", "a").write("\n".join(E) + "\n"); print("\n".join(E))
