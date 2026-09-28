"""Recompute each page's on-chain fingerprint from the served text, following the public SDK (sdk/layout.mjs at d798e21c)."""
import json, hashlib, struct
d = json.load(open("rs.json"))
CHUNK = 3000
def frame(b):
    h = bytearray(12); h[0:5] = bytes([0x28, 0xb5, 0x2f, 0xfd, 0xa0]); h[5:9] = struct.pack("<I", len(b))
    block = (len(b) << 3) | 1; h[9] = block & 255; h[10] = (block >> 8) & 255; h[11] = (block >> 16) & 255
    return bytes(h) + b
def root(fr):
    chunks = [fr[o:o + CHUNK] for o in range(0, len(fr), CHUNK)]
    link = bytes(32)
    for c in reversed(chunks): link = hashlib.sha256(c + link).digest()
    return link.hex(), len(chunks)
out = []
for pg in d["pages"]:
    b = pg["text"].encode("utf-8"); fr = frame(b); r, n = root(fr)
    row = {"page": pg["page"], "version": pg["version"], "text_bytes": len(b), "text_chars": len(pg["text"]), "sha256_text": hashlib.sha256(b).hexdigest(), "frame_len": len(fr), "served_len": pg["len"], "chain_root": r, "served_content": pg["content"], "chunks": n,
           "len_matches": len(fr) == pg["len"], "root_matches": r == pg["content"]}
    out.append(row); print(row["page"], "len", row["frame_len"], row["served_len"], row["len_matches"], "| root", r[:16], pg["content"][:16], row["root_matches"], "| chunks", n, "| sha256(text)", row["sha256_text"][:16])
json.dump(out, open("fingerprint.json", "w"), indent=1)
