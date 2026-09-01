#!/usr/bin/env python3
"""Independent replication attempt of the vals.ai 2026-08-31 Cyphral Distich claim.
Input: EEBO-TCP A64608 (Logopandecteision, 1653). Method under test, verbatim from the post:
"for each number in a cipher line, go to the i-th Proquiritation, use that number as a word
index, and take the first letter of that word."
Re-run: python3 replicate_distich.py A64608.xml"""
import re, sys, json, itertools, hashlib

L1 = [5,3,27,38,32,14,21,8,66,8,70,39,5,9,12,18,2,3,56,5,1,7,3,2,13,19,3,25,9,3,16,6]
L2 = [25,15,13,6,11,20,5,1,2,12,1,20,20,49,20,20,35,33,4,6,8,35,5,33,5,5,18,10,3,11,32,42]
E1, E2 = "OGODUPHOLDKINGCHARLSTHESECONDAND", "MAKEHIMTHESUPREMERULEROFTHISLAND"

def extract(data, split_hyphen, amp_as_and, include_signed):
    s = data.find('<div n="1" type="part">'); e = data.find('<div type="epigraph">', s)
    chunk = data[s:e]
    divs = re.split(r'<div n="(\d+)" type="part">', chunk)
    parts = {}
    for i in range(1, len(divs), 2):
        n, body = int(divs[i]), divs[i+1]
        body = re.sub(r'<g ref="char:EOLhyphen"/>\s*', '', body)
        sig = re.search(r'<signed>(.*?)</signed>', body, re.S)
        sig_txt = re.sub(r'<[^>]+>', ' ', sig.group(1)) if sig else ""
        body = re.sub(r'<signed>.*?</signed>', ' ', body, flags=re.S)
        body = re.sub(r'<head>.*?</head>', ' ', body, flags=re.S)
        txt = re.sub(r'<[^>]+>', ' ', body)
        if include_signed: txt += " " + sig_txt
        txt = txt.replace('&amp;', ' zzand ' if amp_as_and else ' ')
        if split_hyphen: txt = txt.replace('-', ' ')
        ws = re.findall(r"[A-Za-z][A-Za-z']*", txt)
        parts[n] = ['and' if w == 'zzand' else w for w in ws]
    return parts

def main(path):
    data = open(path).read()
    report = {"input_sha256": hashlib.sha256(open(path,'rb').read()).hexdigest(),
              "claim": {"L1": L1, "L2": L2, "plaintext": [E1, E2]}, "grid": [], "infeasible": {}}
    base_parts = extract(data, 0, 0, 0)
    # Infeasibility: positions whose expected letter starts NO word in the target section
    for name, nums, exp in (("L1", L1, E1), ("L2", L2, E2)):
        bad = []
        for i, (n, c) in enumerate(zip(nums, exp), 1):
            if not any(w[0].upper() == c for w in base_parts[i]):
                bad.append({"pos": i, "num": n, "needs": c, "section_words": len(base_parts[i])})
        report["infeasible"][name] = bad
    # Convention grid
    for sh, amp, sig, smn, base, letter in itertools.product([0,1],[0,1],[0,1],["i","33-i"],[0,1],["first","last"]):
        parts = extract(data, sh, amp, sig)
        sm = (lambda i: i) if smn == "i" else (lambda i: 33-i)
        def dec(nums):
            out = []
            for i, n in enumerate(nums, 1):
                ws = parts[sm(i)]; idx = n - base
                out.append(ws[idx][0 if letter=="first" else -1].upper() if 0 <= idx < len(ws) else '?')
            return "".join(out)
        d1, d2 = dec(L1), dec(L2)
        s = sum(a==b for a,b in zip(d1,E1)) + sum(a==b for a,b in zip(d2,E2))
        report["grid"].append({"conv": f"hyph{sh} amp{amp} sig{sig} sec:{smn} base{base} {letter}", "score": s, "out": [d1, d2]})
    # letter-index variant
    letters = {k: re.sub(r"[^A-Za-z]", "", "".join(ws)) for k, ws in base_parts.items()}
    d1 = "".join(letters[i][n-1].upper() if n-1 < len(letters[i]) else '?' for i, n in enumerate(L1, 1))
    d2 = "".join(letters[i][n-1].upper() if n-1 < len(letters[i]) else '?' for i, n in enumerate(L2, 1))
    report["grid"].append({"conv": "letter-index base1", "score": sum(a==b for a,b in zip(d1,E1))+sum(a==b for a,b in zip(d2,E2)), "out": [d1, d2]})
    report["grid"].sort(key=lambda r: -r["score"])
    report["best_score"] = report["grid"][0]["score"]
    json.dump(report, open("replication_report.json", "w"), indent=1)
    print("best convention score:", report["best_score"], "/64 (chance ~4-8)")
    print("hard-infeasible positions:", {k: [(b['pos'], b['needs']) for b in v] for k, v in report["infeasible"].items()})

main(sys.argv[1] if len(sys.argv) > 1 else "A64608.xml")
