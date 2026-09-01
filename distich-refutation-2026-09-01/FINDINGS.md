# The "Fable 5.1 solved the Cyphral Distich" claim does not survive contact with the 1653 book
Reticuli, 2026-09-01. Independent replication attempt of https://www.vals.ai/blogs/fable-solves-cyphral-distich (Geby Jaff, 2026-08-31).

## The claim (verbatim from the post)
1. "At the end of Urquhart's Logopandecteision is a cryptogram consisting of two lines of 32 numbers each, called the Cyphral Distich."
2. "the cryptogram is printed immediately after Urquhart's 32 Proquiritations"
3. Method: "for each number in a cipher line, go to the i-th Proquiritation, use that number as a word index, and take the first letter of that word. With this, you get: O GOD UPHOLD KING CHARLS THE SECOND AND / MAKE HIM THE SUPREME RULER OF THIS LAND"

## Finding 1 — the 1653 book ends with no cryptogram
British Library film of Logopandecteision (1653), archive.org item
bim_early-english-books-1641-1700_logopandecteision-or-an_urquhart-sir-thomas_1653,
final leaves: Proquiritations 30-32 -> printer's ornament row -> "Parva peto" epigraph
("Little I ask...") -> FINIS -> errata. No numeric distich anywhere (endleaf-162.jpg;
whole-film OCR contains no dotted number runs). The gap-free EEBO-TCP transcription
(A64608) agrees: 32 parts, epigraph, trailer FINIS, errata — zero <gap> elements in the span.

## Finding 2 — the claimed method cannot produce the claimed plaintext
From the actual text of the 32 Proquiritations (TCP A64608; five leaves print-verified
against the film, sections 8-26 and 30-32), TEN positions are hard-infeasible: the required
letter begins NO word in the target section, so no word-index convention of any kind can
yield it. L1: pos2 G, pos5 U, pos9 L, pos11 K (KING's K: Proquiritation 11 has 80 words,
none starting with K — print-verified, endleaf-157.jpg), pos31 N. L2: pos1 M, pos3 K,
pos4 E, pos19 U, pos31 N. A 65-convention grid (tokenization x section-map x index-base x
first/last letter x letter-index) tops out at 8/64 matches — chance level.
Re-run: python3 replicate_distich.py A64608.xml

## Finding 3 — provenance contradicts in-book placement
Klaus Schmeh (Cipherbrain, 2019): both Urquhart cryptograms survive via John Wilcock's 1899
biography; the original source is not established. Neither the distich, the octastich, the
"decagram", nor their companion verses appear in the TCP transcriptions of Logopandecteision
(A64608) or of The Jewel/Ekskybalauron 1652 (A95749).

## What checks out
The post's number sequences match Cipherbrain's record exactly, the Urquhart quote about
"Two and thirty" is genuine (it introduces the Proquiritations), and the post's octastich
premise that the 1652 Jewel "has exactly 284 numbered pages" is TRUE (TCP page numbers run
1..284). The ciphers are real and remain, per the primary record, UNSOLVED.

## What would change this verdict
A published artifact showing a Logopandecteision copy with the distich printed after the
Proquiritations AND Proquiritation texts containing the ten missing initials. The post
mentions internal files (transcription.txt, SOLUTION.md); none are published.

## Hash manifest (sha256)
f44504e83332019c70d5061bfc60d2d030a8ce0cb74fe1c094edcf851da036f4  replicate_distich.py
fe1255c3f2a7f6ee9ae2b723d751121c8d04a0d5fe914d3bdf1bb9d0eb2a502b  replication_report.json
d8a4f191d180163d7122c9288fd0c59af07833addcfe6c04b15f35935fcf1788  proquiritations.json
a99c64baa51ab09e97118069a2dfa110dd4df2c7267f45d7c9b4322df741a3a0  A64608.xml
c828ecb5c2a99f67c795f893feb0c44eff5996684a3fb1fec6dda0166570dcdf  A95749.xml
12c54a0c5552c8bd8a30b1fbf33f07bfde2674bd7ab1cf08c48ecd4b77d072ce  vals_raw.html
a814ca3e85d8fb5c4c82e193b1ab80b763ac2df40e911fcda35e47561ae66fe5  logo_ocr.txt
d3b22e529b1c82ec08662c242c12fc85b0d9af356377c9b7c9a4ed04f3a58bd6  endleaf-157.jpg
73ae302aeaf1c5965400ef55a3f5631f16e0a3b357c81302fc2e02fc8ce8470f  endleaf-162.jpg
