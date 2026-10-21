#!/usr/bin/env python3
"""Reader tool: the frame fold reimplemented from META.json `frame_recipe` alone.

Two modes, no network, no writes unless --json:
  python3 fold_check.py [--json]
      calibration: fold the five frozen texts in this directory; every backward root must equal
      `backward_fold_gives`, every forward root `forward_fold_would_give`, every page text's sha256 its
      META row. Exit 0 = all match, 1 = a mismatch. --json writes fold_calibration_<date>.json beside it.
  python3 fold_check.py --text FILE --expect ROOT
      one file against one root (mindGrapez 8b686e5a on 964b3fc4, 2026-10-20): frame FILE's bytes, fold
      the chunks, compare the backward root with ROOT (64 hex). Exit 0 = match, 1 = mismatch, 2 = usage.
      On a mismatch the forward root is printed too, and named if ROOT equals it (wrong direction).
      For filing day: FILE = the text reassembled from the thread by the note's reader rule, ROOT = the
      gateway's payload.content for the page. The reassembly and the GET stay the reader's own steps.
      FILE is read as raw bytes with no newline translation and its sha256 is printed beside the verdict, so a
      CRLF copy shows as a different sha AND a different root instead of passing silently.
The direction, link seed, chunk size and header bytes are READ from the recipe's fields, not assumed."""
import json, hashlib, struct, sys, os, datetime as dt
D = os.path.dirname(os.path.abspath(__file__)); M = json.load(open(os.path.join(D, "META.json"), encoding="utf-8")); R = M["frame_recipe"]
assert R["header_bytes"] == 12 and R["link"] == "sha256(chunk + link)", "recipe shape"
assert R["fold_direction"] == "last_to_first", "this tool implements the last-to-first fold only; the recipe says %r" % R.get("fold_direction")
CHUNK = int(R["chunk_bytes"]); MAGIC = bytes.fromhex(R["magic_descriptor_hex"]); SEED = bytes.fromhex(R["link_seed_hex"]); assert len(MAGIC) == 5 and len(SEED) == 32
def frame(text):
    b = text.encode("utf-8"); n = len(b)
    return MAGIC + struct.pack("<I", n) + struct.pack("<I", n * 8 + 1)[:3] + b   # magic+descriptor, size LE32, (count*8+1) LE24, text
def chunks(fr): return [fr[i:i + CHUNK] for i in range(0, len(fr), CHUNK)]
def fold(cs, backward=True):
    link = SEED
    for c in (reversed(cs) if backward else cs): link = hashlib.sha256(c + link).digest()
    return link.hex()
def read_text(path):
    """Raw bytes, decoded as UTF-8, NO newline translation: a CRLF copy is a different text and folds to a different root (mindGrapez 11f5117b, 2026-10-21). Returns (text, raw_bytes)."""
    b = open(path, "rb").read(); return b.decode("utf-8"), b
def describe(t, raw=None):
    fr = frame(t); cs = chunks(fr); raw = t.encode("utf-8") if raw is None else raw
    return {"chars": len(t), "bytes": len(t.encode("utf-8")), "raw_bytes_on_disk": len(raw), "sha256_raw_file": hashlib.sha256(raw).hexdigest(), "cr_count": raw.count(b"\r"), "frame_bytes": len(fr), "chunks": len(cs), "header_hex": fr[:12].hex(), "sha256_text": hashlib.sha256(t.encode("utf-8")).hexdigest(), "backward_root": fold(cs, True), "forward_root": fold(cs, False)}
def usage(msg):
    print("usage error:", msg, file=sys.stderr); print(__doc__, file=sys.stderr); sys.exit(2)
args = sys.argv[1:]
if "--text" in args or "--expect" in args:
    try: f = args[args.index("--text") + 1]; root = args[args.index("--expect") + 1].strip().lower()
    except (ValueError, IndexError): usage("--text FILE and --expect ROOT are both required")
    if len(root) != 64 or any(ch not in "0123456789abcdef" for ch in root): usage("ROOT must be 64 hex characters (a prefix can false-match)")
    if not os.path.isfile(f): usage("no such file: %s" % f)
    t, raw = read_text(f); d = describe(t, raw); match = d["backward_root"] == root
    print(f"{'MATCH   ' if match else 'MISMATCH'} {os.path.basename(f)} chars {d['chars']} bytes {d['bytes']} frame {d['frame_bytes']} B {d['chunks']} chunks hdr {d['header_hex']}")
    print(f"  raw file  sha256 {d['sha256_raw_file']}  ({d['raw_bytes_on_disk']} bytes on disk, {d['cr_count']} CR bytes; the fold is over these exact bytes, no newline translation)")
    print(f"  backward root {d['backward_root']}\n  expected      {root}")
    if not match:
        print(f"  forward root  {d['forward_root']}" + ("  <- expected EQUALS the forward fold: wrong direction, the roots that bind are backward" if root == d["forward_root"] else ""))
    sys.exit(0 if match else 1)
FILES = {"page1_v11": "page1_v11_served.md", "page3_v3": "page3_v3.md", "page3_v4": "page3_v4_draft.md", "page1_repoint_to_v3": "page1_repoint_to_v3.md", "page1_repoint_to_v4": "page1_repoint_to_v4.md"}
out, ok = {}, True
for k, f in FILES.items():
    t, raw = read_text(os.path.join(D, f)); d = describe(t, raw); meta = M.get(k) or {}
    good = d["backward_root"] == R["backward_fold_gives"][k] and d["forward_root"] == R["forward_fold_would_give"][k] and (not meta.get("sha256_text") or d["sha256_text"] == meta["sha256_text"]) and (not meta.get("fingerprint_if_filed") or d["backward_root"] == meta["fingerprint_if_filed"]) and (k not in R["header_hex"] or d["header_hex"] == R["header_hex"][k])
    ok = ok and good; out[k] = dict(file=f, matches_meta=good, **d)
    print(f"{'ok  ' if good else 'FAIL'} {k:22s} chars {d['chars']:5d} frame {d['frame_bytes']:5d} B {d['chunks']} chunks hdr {d['header_hex']} back {d['backward_root'][:8]} fwd {d['forward_root'][:8]} sha {d['sha256_text'][:8]}")
print("ALL MATCH" if ok else "MISMATCH")
if "--json" in args:
    p = os.path.join(D, f"fold_calibration_{dt.date.today().isoformat()}.json"); json.dump({"ran": dt.datetime.now(dt.timezone.utc).isoformat()[:19] + "Z", "all_match": ok, "texts": out}, open(p, "w"), indent=1); print("wrote", os.path.basename(p))
sys.exit(0 if ok else 1)
