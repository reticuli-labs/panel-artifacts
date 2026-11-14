"""totext.py <in file> <out file>: plain text of a saved HTML page or a JATS XML full text. Parses only; runs nothing from the input."""
import html, re, sys
src, dst = sys.argv[1], sys.argv[2]
raw = open(src, "rb").read().decode("utf-8", "replace")
raw = re.sub(r"(?is)<(script|style|noscript|svg)\b.*?</\1>", " ", raw)
raw = re.sub(r"(?i)</(p|div|sec|title|h[1-6]|li|tr|caption|abstract|ref)>", "\n", raw)
txt = html.unescape(re.sub(r"<[^>]+>", " ", raw))
txt = re.sub(r"[ \t\r\f\v]+", " ", txt); txt = re.sub(r"\n\s*\n+", "\n", txt).strip()
open(dst, "w", encoding="utf-8").write(txt); print(dst.split("/")[-1], len(txt), "chars")
