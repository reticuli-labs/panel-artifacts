"""kwic.py <text file> <width> <pattern> [pattern ...]: every match of each regex with its surroundings, so a number is read in its sentence."""
import re, sys
t = open(sys.argv[1], encoding="utf-8").read().replace("\n", " "); w = int(sys.argv[2])
for pat in sys.argv[3:]:
    ms = list(re.finditer(pat, t)); print("### %r: %d match(es)" % (pat, len(ms)))
    last = -10**9
    for m in ms[:12]:
        if m.start() - last < w: continue
        last = m.start(); print("   ...", t[max(0, m.start() - w): m.end() + w].strip(), "...")
