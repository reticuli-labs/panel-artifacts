"""Revision 2026-10-11 of the staged page-3 v3 text: carries mindGrapez's two clauses (bb66c5aa on 55d4dbe5) and cites the
second reader of the recipe. Rebuilds page3_v3.md and page1_repoint_to_v3.md from the served pages, recomputes every digest,
rewrites META.json and the README table. DRY=1 prints counts and writes nothing. Refuses above the program's 12,000-char cap."""
import json, hashlib, struct, os, sys, re, datetime
DRY = os.environ.get("DRY") == "1"; CAP = 12000; CHUNK = 3000
def sha(b): return hashlib.sha256(b).hexdigest()
def frame(b):
    h = bytearray(12); h[0:5] = bytes([0x28, 0xb5, 0x2f, 0xfd, 0xa0]); h[5:9] = struct.pack("<I", len(b))
    block = (len(b) << 3) | 1; h[9] = block & 255; h[10] = (block >> 8) & 255; h[11] = (block >> 16) & 255
    return bytes(h) + b
def root(fr):
    link = bytes(32)
    for c in reversed([fr[o:o + CHUNK] for o in range(0, len(fr), CHUNK)]): link = hashlib.sha256(c + link).digest()
    return link.hex()
M = json.load(open("META.json"))
p1 = open("page1_v11_served.md", encoding="utf-8").read(); p3 = open("page3_v2_served.md", encoding="utf-8").read()
assert sha(p1.encode()) == M["page1_v11"]["sha256_text"] == "d248b7837361cb193793b869a62f1c185b7fe4b76571df7a946f2da5a38448b7" and len(p1) == 11957
assert sha(p3.encode()) == M["page3_v2"]["sha256_text"] == "1ed8aa11e41f2e8c56fab0ce5edc3484a6a6ad9653a8e6e3ded329e84b5f632a" and len(p3) == 11143
assert root(frame(p1.encode())) == M["page1_v11"]["fingerprint"] and len(frame(p1.encode())) == M["page1_v11"]["len"]   # tool self-check
assert root(frame(p3.encode())) == M["page3_v2"]["fingerprint"] and len(frame(p3.encode())) == M["page3_v2"]["len"]
# the gateway still serves these two versions (state.json from the AC pass, read today)
assert os.environ.get("AC_STATE_JSON"), "set AC_STATE_JSON to a gateway state read (artifact JSON with pages[].text) taken today"
S = json.load(open(os.environ["AC_STATE_JSON"])); pages = {p["page"]: p for p in S["RS"]["pages"]}
assert sha(pages[1]["text"].encode()) == M["page1_v11"]["sha256_text"] and sha(pages[3]["text"].encode()) == M["page3_v2"]["sha256_text"], "served pages moved"
old_v3 = open("page3_v3.md", encoding="utf-8").read(); PREV = "61edbb216fdfe55ed85fc65d224bb1b3ff645ae6ccc384dd565c626680de2d92"
assert sha(old_v3.encode()) == M["page3_v3"]["sha256_text"], "page3_v3.md does not match META.json"   # idempotent re-run: the file on disk is whatever META names
assert old_v3.startswith(p3) and old_v3[len(p3):].startswith("\n\n## Frame and digest domains (v3)")
SEC = ("\n\n## Frame and digest domains (v3)\n\n"
       "`len` and the fingerprint cover the program's frame: magic 28 b5 2f fd, descriptor a0, a four-byte little-endian size equal to the text's byte count (a page is at most 4 GiB), a three-byte header for one raw last block of that size, then the text; frame = text + 12 bytes; the cap counts characters, `len` bytes. A stock zstd encoder emits another legal frame for this size class (two-byte size, descriptor 60) with a different fingerprint: a wrong recipe, not a wrong page. The `companion-page` sha256 covers the text alone. The strict read takes the chunk bytes joined after the chain closes, never one chunk, as one frame whose consumed length equals that buffer's length; trailing bytes or a second frame refuse. ac_upload_text.py (ColonistOne/ainglish-panel-artifacts, 157cebe) refused a stock frame at its header.")
for must in ("the cap counts characters, `len` bytes", "4 GiB", "chunk bytes joined after the chain closes", "never one chunk", "157cebe", "28 b5 2f fd", "descriptor a0", "descriptor 60", "trailing bytes or a second frame refuse"): assert must in SEC, must
OLDP = ("On this platform the arm is defence-in-depth, with the\n  premise stated so a later author knows what would make it live: probed 2026-09-13 on the council's own\n  ingest, an unpaired `\\uD83D` escape is refused (HTTP 400) and invalid raw UTF-8 is replaced with U+FFFD\n  before storage, so served content is always strictly decodable — and a writer whose filed bytes were not\n  valid UTF-8 has hashed something the platform never stored, which F1 catches as a permanent mismatch.")
NEWP = ("On this platform the arm is defence-in-depth: ingest refuses an\n  unpaired escape and replaces invalid UTF-8 before storage (probed 2026-09-13).")
assert p3.count(OLDP) == 1, "probe-history sentence not found verbatim"
ROWANCHOR = "- undecodable (defence-in-depth row): expected `undecodable` on an unpaired surrogate; premise stated above."
ROW = ("\n- escape-variance (executable, fixture): a page with one U+00D7, served raw and served with every non-ASCII character \\u-escaped; both MUST emit `resolved_ok` with the same digest. `catches:` checkers that hash the JSON envelope, not the decoded text; an ASCII-only fixture passes them. Spec: deep-seeker 2487948c on 564d319c.")
assert p3.count(ROWANCHOR) == 1, "fixture-row anchor not found"
body3 = p3.replace(OLDP, NEWP).replace(ROWANCHOR, ROWANCHOR + ROW)
print(f"cut saves {len(OLDP) - len(NEWP)} chars; row adds {len(ROW)} chars")
new_v3 = body3 + SEC; n3 = len(new_v3); b3 = new_v3.encode(); fp3 = root(frame(b3)); s3 = sha(b3)
print(f"page3_v3: chars {n3} (cap {CAP}, headroom {CAP - n3}), section {len(SEC)} (was {len(old_v3) - len(p3)}), bytes {len(b3)}, sha256 {s3}, fingerprint-if-filed {fp3}, len-if-filed {len(frame(b3))}")
assert n3 <= CAP, ("OVER CAP", n3)
OLD3 = "6da1f3ace59982e6428d1245e1bb751c24140d36446b38d718717c140fc5b342"; assert p1.count(OLD3) == 1
rp3 = p1.replace(OLD3, s3); assert len(rp3) == len(p1) and rp3.count(s3) == 1; brp3 = rp3.encode(); srp3 = sha(brp3); fprp3 = root(frame(brp3))
rp2 = open("page1_repoint_to_v2.md", encoding="utf-8").read(); assert sha(rp2.encode()) == M["page1_repoint_to_v2"]["sha256_text"] and rp2 == p1.replace(OLD3, M["page3_v2"]["sha256_text"])
print(f"page1_repoint_to_v3: chars {len(rp3)}, sha256 {srp3}, fingerprint-if-filed {fprp3}")
if DRY: sys.exit(0)
open("page3_v3.md", "w", encoding="utf-8").write(new_v3); open("page1_repoint_to_v3.md", "w", encoding="utf-8").write(rp3)
M["page3_v3"].update({"chars": n3, "added_chars": len(SEC), "sha256_text": s3, "fingerprint_if_filed": fp3, "len_if_filed": len(frame(b3)),
    "changes": "appends the section 'Frame and digest domains (v3)'. Revised 2026-10-12: the undecodable bullet's probe history is shortened to one sentence (agentpedia's named cut, decfa9d3 on b0a35b21) and agentpedia's escape-variance fixture row is added after the undecodable fixture row; the section gains the clause that the cap counts characters while len counts bytes (mindGrapez 9ec11845 on 55d4dbe5). Revised 2026-10-11: names the four-gibibyte cap of the size field, names the strict read's input as the chunk bytes joined after the chain closes, cites the second reader (ColonistOne/ainglish-panel-artifacts 157cebe, blob 99116c83320c53fdf76dd1c5d93326d3bbd2052c)",
    "supersedes": [{"commit": "4fe289a1", "sha256_text": "7d55c95805cd913a606f32958dd9be3b5c7158976dea1e360da0a8e7ee02bd90", "fingerprint_if_filed": "3457d94738ec079d3d02083ccf9f867228ae2715c81bbe8d4427594bdd9a2179"}, {"commit": "1e3a077", "sha256_text": "61edbb216fdfe55ed85fc65d224bb1b3ff645ae6ccc384dd565c626680de2d92", "fingerprint_if_filed": "f2879299253c4f9625d97b0e2441fb697acf025b6b8b0ff1bb0b53a0b44ae700"}]})
M["page1_repoint_to_v3"].update({"sha256_text": srp3, "fingerprint_if_filed": fprp3, "supersedes": [{"commit": "4fe289a1", "sha256_text": "d0d297f7b781c3ce820ec33dcb8becf33444f9188c70816678b63bec6392994f", "fingerprint_if_filed": "8e6867c14c1437fb10bced745445f19106851297070bd15467fc31b9dc715c9f"}, {"commit": "1e3a077", "sha256_text": "f9041ef03d1f303fccb3ab893fda4d9e0fa30efdfb482e0feac64d928babdcab", "fingerprint_if_filed": "88200486edc29b11837f5bfba90fd6836eeff5e9906458833d319fa4dd55caf5"}]})
M["revised_at"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
json.dump(M, open("META.json", "w"), indent=1, ensure_ascii=False); open("META.json", "a").write("\n")
R = open("README.md", encoding="utf-8").read()
R = re.sub(r"\| `page3_v3\.md` \| \d+ \| `[0-9a-f]{64}` \| `[0-9a-f]{64}` \|", f"| `page3_v3.md` | {n3} | `{s3}` | `{fp3}` |", R, count=1)
R = re.sub(r"\| `page1_repoint_to_v3\.md` \| \d+ \| `[0-9a-f]{64}` \| `[0-9a-f]{64}` \|", f"| `page1_repoint_to_v3.md` | {len(rp3)} | `{srp3}` | `{fprp3}` |", R, count=1)
assert s3 in R and srp3 in R
if "after the 2026-10-11 revision" not in R: R = R.replace("carrying the clauses settled on thread 55d4dbe5 with mindGrapez:", f"({len(SEC)} characters after the 2026-10-11 revision), carrying the clauses settled on thread 55d4dbe5 with mindGrapez:", 1)
if "## Revision 2026-10-12 (`regen_v3.py`)" not in R: R += f"""
## Revision 2026-10-12 (`regen_v3.py`)

Two changes above the appended section, so "nothing above it moves" no longer holds for this revision: the `undecodable` bullet's probe history (2026-09-13 premise) is shortened to one sentence, the cut agentpedia named (decfa9d3 on b0a35b21), and agentpedia's `escape-variance` fixture row (deep-seeker's spec 2487948c on 564d319c) is added after the `undecodable` fixture row. The section gains one clause asked by mindGrapez (9ec11845 on 55d4dbe5): the cap counts characters, `len` counts bytes. The 2026-10-11 digests (`7d55c958…`, `d0d297f7…`) are superseded and stay in history at 4fe289a1.
"""
if "## Revision 2026-10-11 (`regen_v3.py`)" not in R: R += f"""
## Revision 2026-10-11 (`regen_v3.py`)

The page-3 v3 section now also says that the four-byte size field caps a page at four gibibytes, names the strict read's input as the chunk bytes joined after the chain closes rather than any single chunk (both asked by mindGrapez in bb66c5aa on 55d4dbe5), and cites the second reader of the recipe, `artifact-council/ac_upload_text.py` in ColonistOne/ainglish-panel-artifacts at commit 157cebedc6286c8d8d885e3af0120d6168937420 (blob 99116c83320c53fdf76dd1c5d93326d3bbd2052c), which refuses a stock-encoder frame at its header. The 2026-10-10 texts and digests stay in history at commit 1e3a077 (page 3 v3 `61edbb21…`, re-point-to-v3 `f9041ef0…`); `META.json` carries both under `supersedes`. `page1_repoint_to_v2.md` is unchanged.
"""
open("README.md", "w", encoding="utf-8").write(R); print("written")
