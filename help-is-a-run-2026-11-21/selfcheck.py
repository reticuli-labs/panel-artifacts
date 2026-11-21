"""selfcheck.py: argv_sweep.classify on small made-up sources whose class is known by construction, and on the one script this
directory is about, as it stood before and after its fix. Prints one line per case and exits 1 if any differs from what is
expected. It writes nothing. usage: selfcheck.py --repo PATH   (the repository that holds lineage-census-2026-10-02)"""
import argparse, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from argv_sweep import classify

CASES = [  # (name, source, expected class, expected writes, expected mode_not_literal)
 ("a parser, and a write", "import argparse, json\nap = argparse.ArgumentParser()\na = ap.parse_args()\njson.dump({}, open('out.json', 'w'))\n", "parser", True, False),
 ("argv by hand, and a write", "import sys\nif '--check' in sys.argv: print('check')\nelse: open('results.json', 'w').write('x')\n", "by hand", True, False),
 ("from sys import argv", "from sys import argv\nprint(argv[1])\n", "by hand", False, False),
 ("never looks, and writes", "import json\nrows = [1, 2]\njson.dump(rows, open('table.json', 'w'))\n", "never", True, False),
 ("never looks, reads only", "import json\nprint(len(json.load(open('table.json'))))\n", "never", False, False),
 ("never looks, work under the main guard", "def run():\n    open('a.txt', 'a').write('x')\nif __name__ == '__main__':\n    run()\n", "never", True, False),
 ("only definitions", "import os\nX = 3\nNAMES = ['a', 'b']\ndef f(p):\n    return open(p, 'w')\nclass C:\n    pass\n", "library", True, False),
 ("a docstring and constants", '"""a module"""\nA = 1\nB = "two"\n', "library", False, False),
 ("an assignment that calls", "import json\nDATA = json.load(open('d.json'))\n", "never", False, False),
 ("Path.write_text", "from pathlib import Path\nPath('o.txt').write_text('x')\n", "never", True, False),
 ("Path.open for reading", "from pathlib import Path\nprint(Path('o.txt').open().read())\n", "never", False, False),
 ("Path.open for writing", "from pathlib import Path\nPath('o.txt').open('w').write('x')\n", "never", True, False),
 ("gzip.open, text write", "import gzip\ngzip.open('o.gz', 'wt').write('x')\n", "never", True, False),
 ("gzip.open, read", "import gzip\nprint(gzip.open('o.gz', 'rt').read())\n", "never", False, False),
 ("the mode in a variable", "import sys\nm = 'w' if len(sys.argv) > 1 else 'r'\nopen('o.txt', m)\n", "by hand", False, True),
 ("mode by keyword", "open('o.txt', mode='x').write('1')\n", "never", True, False),
 ("os.open is not counted", "import os\nfd = os.open('o.txt', os.O_RDONLY)\n", "never", False, False),
 ("read and write, r+", "open('o.txt', 'r+').write('1')\n", "never", True, False),
]
ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--repo", required=True); a = ap.parse_args()
bad = 0
RUN = [  # (name, source, a write, a removal or a move is reached when the file is run)
 ("a write in a function nobody calls", "def save():\n    open('o.txt', 'w').write('x')\nprint('hello')\n", False),
 ("a write in a function called under the main guard", "def save():\n    open('o.txt', 'w').write('x')\nif __name__ == '__main__':\n    save()\n", True),
 ("a write two calls deep", "def a():\n    b()\ndef b():\n    open('o.txt', 'w').write('x')\na()\n", True),
 ("a write in a method, called on an object", "class T:\n    def save(self):\n        open('o.txt', 'w').write('x')\nT().save()\n", True),
 ("a write outside every function", "import json\njson.dump([], open('o.json', 'w'))\n", True),
 ("a removal in a function called from a loop", "import os\ndef clean(p):\n    os.remove(p)\nfor p in ['a', 'b']:\n    clean(p)\n", True),
 ("a read only", "print(open('o.txt').read())\n", False),
 ("a nested function inside a called one, itself not called", "def a():\n    def inner():\n        open('o.txt', 'w')\n    return 1\na()\n", False),
]
MORE = [  # (name, source, appends when run, service calls when run)
 ("an append outside every function", "open('ERRATA.md', 'a').write('x')\n", True, []),
 ("a write, no append", "open('o.txt', 'w').write('x')\n", False, []),
 ("an append in a function nobody calls", "def add():\n    open('ERRATA.md', 'a').write('x')\nprint(1)\n", False, []),
 ("a vote on a client", "from colony_sdk import ColonyClient\nc = ColonyClient('k')\nc.vote_post('id', 1)\n", False, ["vote_post"]),
 ("a measurement filed in a called function", "def file(c):\n    c.measure('slug', payload={})\nfile(None)\n", False, ["measure"]),
 ("a measurement in a function nobody calls", "def file(c):\n    c.measure('slug', payload={})\n", False, []),
 ("a read on a client", "c = object()\nc.proposal('slug')\n", False, []),
]
for name, src, app, svc in MORE:
    r = classify(src); ok = (r["appends_when_run"], r["service_write_calls_when_run"]) == (app, svc); bad += not ok
    print("%-4s %-58s expected append %-5s service %-14s | got %s %s" % ("ok" if ok else "BAD", name, app, svc, r["appends_when_run"], r["service_write_calls_when_run"]))
for name, src, want in RUN:
    r = classify(src); got = r["writes_when_run"] or r["removes_or_moves_when_run"]; ok = got == want; bad += not ok
    print("%-4s %-58s expected reached %-5s | got %s" % ("ok" if ok else "BAD", name, want, got))
for name, src, cls, writes, unknown in CASES:
    r = classify(src); ok = (r["class"], r["writes"], r["mode_not_literal"]) == (cls, writes, unknown); bad += not ok
    print("%-4s %-40s expected %-8s writes %-5s | got %-8s writes %-5s mode not literal %s" % ("ok" if ok else "BAD", name, cls, writes, r["class"], r["writes"], r["mode_not_literal"]))
REL = "lineage-census-2026-10-02/path_leak_pass.py"
for label, rev in (("the script before its fix (b41a40f)", "b41a40f"), ("the script after its fix (486d658)", "486d658")):
    src = subprocess.run(["git", "-C", a.repo, "show", "%s:%s" % (rev, REL)], capture_output=True, check=True).stdout.decode("utf-8"); r = classify(src)
    ok = (r["class"], r["writes"], r["writes_when_run"]) == ("by hand", True, True); bad += not ok
    print("%-4s %-40s expected by hand writes True  | got %-8s writes %-5s (the fix is a refusal written by hand: the class cannot show it)" % ("ok" if ok else "BAD", label, r["class"], r["writes"]))
r = classify(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "argv_sweep.py"), encoding="utf-8").read()); ok = (r["class"], r["writes"]) == ("parser", True); bad += not ok
print("%-4s %-40s expected parser  writes True  | got %-8s writes %s" % ("ok" if ok else "BAD", "argv_sweep.py itself", r["class"], r["writes"]))
print("cases that differ:", bad); sys.exit(1 if bad else 0)
