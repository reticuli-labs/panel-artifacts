"""make_variant.py: write ule_variant/ule_extract_keep_internal.lean, which is the authors' extractor (the file ule_extract.lean
in the directory named by ULE_SRC) with ONE line taken out: the line that skips internal names. Their file is not kept in this
directory; this script makes the variant from their file, and stops if that line is not there exactly once."""
import hashlib, os
D = os.path.dirname(os.path.abspath(__file__)); os.chdir(D)
s = open(os.path.join(os.environ["ULE_SRC"], "ule_extract.lean"), encoding="utf-8").read()
a = "    if n.isInternal then continue\n"; assert s.count(a) == 1, "the line is not there exactly once: their file has changed"
os.makedirs("ule_variant", exist_ok=True); t = s.replace(a, ""); open("ule_variant/ule_extract_keep_internal.lean", "w", encoding="utf-8").write(t)
print("their file sha256", hashlib.sha256(s.encode()).hexdigest(), "| variant sha256", hashlib.sha256(t.encode()).hexdigest())
