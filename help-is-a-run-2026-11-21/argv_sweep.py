"""argv_sweep.py: for every Python file tracked at one commit of a git repository, say by READING it (the syntax tree, nothing
is imported and nothing is run) what `--help` on its command line would be.

  parser      the file does work when run and imports an argument parser (argparse, click, optparse, getopt, typer, fire, docopt)
  by hand     the file does work when run and reads sys.argv itself, with no parser
  never       the file does work when run and never looks at the command line: any flag, --help included, is a plain run
  library     the file only defines things: running it does nothing

and, beside the class: whether a run of the file can reach a line that opens something for writing or removes or moves files
(reached by name from the code outside functions), and whether the file imports a module that reaches out of the process (a
subprocess, the network, a client of a service).

usage: argv_sweep.py --repo PATH [--commit REV] [--exclude PREFIX ...] [--out FILE]
Without --out it prints the summary and writes nothing. The file contents are read with `git show REV:path`."""
import argparse, ast, collections, hashlib, json, subprocess, sys

PARSERS = {"argparse", "click", "optparse", "getopt", "typer", "fire", "docopt"}
REACH_OUT = {"subprocess", "urllib", "requests", "http", "httpx", "socket", "smtplib", "ftplib", "ainglish", "colony_sdk", "openai", "ollama", "web3", "solana", "solders"}
MODE_SECOND = {"io", "codecs", "gzip", "bz2", "lzma"}                      # module.open(path, mode): the mode is the second argument
CHANGES_FILES = {("shutil", "copy"), ("shutil", "copy2"), ("shutil", "copyfile"), ("shutil", "copytree"), ("shutil", "move"), ("shutil", "rmtree"),
                 ("os", "remove"), ("os", "unlink"), ("os", "rename"), ("os", "replace"), ("os", "rmdir")}
WRITE_METHODS = {"write_text", "write_bytes", "to_csv", "to_parquet", "savefig"}
SERVICE_WRITES = {"mint_attempt", "measure", "submit_measurement", "vote", "replace_vote", "withdraw_vote", "second", "withdraw_second", "propose", "amend_current", "retract_measurement", "retire_proposal",
                  "abort_attempt", "set_author_work_notice", "create_post", "create_comment", "update_post", "delete_post", "update_comment", "send_message", "vote_post", "vote_comment", "react_post",
                  "react_comment", "follow", "unfollow", "mark_notifications_read", "mark_notification_read", "update_profile", "vote_poll"}    # method names that change something at a service I use


def const_str(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None


def has_call(node):
    return any(isinstance(n, ast.Call) for n in ast.walk(node))


def does_work(tree):
    """True when running the file as a program executes something beyond definitions, imports and call-free assignments."""
    for i, n in enumerate(tree.body):
        if isinstance(n, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)): continue
        if isinstance(n, ast.Expr) and const_str(n.value) is not None: continue                                   # a docstring or a bare string
        if isinstance(n, (ast.Assign, ast.AnnAssign, ast.AugAssign)) and not has_call(n): continue
        return True
    return False


def lines_run(tree):
    """The line numbers of the code that a run of the file can reach, by name: everything outside a function body, and the body of
    every function or method whose name is called from code already reached. A name that two functions share reaches both. This
    errs toward reaching too much, never too little, except for a function that is only passed around and called under another name."""
    defs = collections.defaultdict(list)
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)): defs[n.name].append(n)

    def outside(node):                                                  # the nodes of a block that are not inside a nested function body
        out = []; stack = list(node.body) if hasattr(node, "body") and isinstance(node.body, list) else [node]
        while stack:
            x = stack.pop()
            if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef)): out.extend(x.decorator_list); continue
            out.append(x); stack.extend(ast.iter_child_nodes(x))
        return out
    reached = outside(tree); seen = set(); queue = list(reached)
    while queue:
        x = queue.pop()
        if isinstance(x, ast.Call):
            name = x.func.id if isinstance(x.func, ast.Name) else x.func.attr if isinstance(x.func, ast.Attribute) else None
            if name in defs and name not in seen:
                seen.add(name)
                for d in defs[name]:
                    inner = outside(d); reached.extend(inner); queue.extend(inner)
    return {n.lineno for n in reached if hasattr(n, "lineno")}


def classify(source):
    tree = ast.parse(source)
    mods = set(); argv = False; writes = []; mode_unknown = []; changes = []; appends = []; service = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): mods |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom):
            mods.add((n.module or "").split(".")[0])
            if n.module == "sys" and any(a.name == "argv" for a in n.names): argv = True
        elif isinstance(n, ast.Attribute) and n.attr == "argv" and isinstance(n.value, ast.Name) and n.value.id == "sys": argv = True
        elif isinstance(n, ast.Call):
            f = n.func; mode = None; is_open = False
            if isinstance(f, ast.Name) and f.id == "open":
                is_open = True; mode = n.args[1] if len(n.args) > 1 else None
            elif isinstance(f, ast.Attribute) and f.attr == "open":
                is_open = True; second = isinstance(f.value, ast.Name) and f.value.id in MODE_SECOND
                if isinstance(f.value, ast.Name) and f.value.id == "os": is_open = False                           # os.open takes flags, not a mode string: not counted
                else: mode = (n.args[1] if len(n.args) > 1 else None) if second else (n.args[0] if n.args else None)
            if is_open:
                for k in n.keywords:
                    if k.arg == "mode": mode = k.value
                if mode is not None:
                    m = const_str(mode)
                    if m is None: mode_unknown.append(n.lineno)
                    elif any(ch in m for ch in "wax+"): writes.append(n.lineno)
                    if m is not None and "a" in m: appends.append(n.lineno)
            if isinstance(f, ast.Attribute) and f.attr in WRITE_METHODS: writes.append(n.lineno)
            if isinstance(f, ast.Attribute) and f.attr in SERVICE_WRITES: service.append((n.lineno, f.attr))
            if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and (f.value.id, f.attr) in CHANGES_FILES: changes.append(n.lineno)
    work = does_work(tree); live = lines_run(tree)
    cls = "library" if not work else "parser" if mods & PARSERS else "by hand" if argv else "never"
    at_run = sorted(l for l in set(writes) if l in live); moved = sorted(l for l in set(changes) if l in live)
    svc = sorted({name for l, name in service if l in live})
    return {"class": cls, "writes": bool(writes), "writes_when_run": bool(at_run), "write_lines_when_run": at_run[:8], "removes_or_moves_when_run": bool(moved), "appends_when_run": any(l in live for l in appends),
            "service_write_calls_when_run": svc, "mode_not_literal": bool(mode_unknown), "changes_files": bool(changes),
            "reaches_out": sorted(mods & REACH_OUT), "main_guard": any(isinstance(n, ast.If) and "__name__" in ast.dump(n.test) for n in tree.body)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True); ap.add_argument("--commit", default="HEAD"); ap.add_argument("--exclude", nargs="*", default=[]); ap.add_argument("--out")
    a = ap.parse_args()
    git = lambda *x: subprocess.run(["git", "-C", a.repo] + list(x), capture_output=True, check=True).stdout
    commit = git("rev-parse", a.commit).decode().strip()
    files = [f for f in git("ls-tree", "-r", "--name-only", commit).decode().split("\n") if f.endswith(".py")]
    rows = []; excluded = []; unparsed = []
    for f in files:
        if any(f.startswith(p) or ("/" + p) in ("/" + f) for p in a.exclude): excluded.append(f); continue
        blob = git("show", "%s:%s" % (commit, f))
        try: r = classify(blob.decode("utf-8"))
        except (SyntaxError, UnicodeDecodeError) as e: unparsed.append({"file": f, "why": type(e).__name__}); continue
        rows.append(dict(r, file=f, sha256=hashlib.sha256(blob).hexdigest()))
    by = collections.Counter(r["class"] for r in rows); n = lambda cls, key: sum(1 for r in rows if r["class"] == cls and r[key])
    summary = {"commit": commit, "python_files": len(files), "excluded": len(excluded), "not_parsed": len(unparsed), "read": len(rows), "by_class": dict(by),
               "writes_a_file_when_run": {c: n(c, "writes_when_run") for c in by}, "removes_or_moves_files_when_run": {c: n(c, "removes_or_moves_when_run") for c in by},
               "writes_removes_or_moves_when_run": {c: sum(1 for r in rows if r["class"] == c and (r["writes_when_run"] or r["removes_or_moves_when_run"])) for c in by},
               "has_a_write_somewhere": {c: n(c, "writes") for c in by},
               "imports_a_module_that_reaches_out": {c: n(c, "reaches_out") for c in by},
               "appends_to_a_file_when_run": {c: n(c, "appends_when_run") for c in by}, "calls_a_method_that_changes_a_service_when_run": {c: n(c, "service_write_calls_when_run") for c in by},
               "neither_writes_when_run_nor_imports_one": {c: sum(1 for r in rows if r["class"] == c and not r["writes_when_run"] and not r["removes_or_moves_when_run"] and not r["reaches_out"]) for c in by},
               "mode_not_literal": {c: n(c, "mode_not_literal") for c in by}}
    print(json.dumps(summary, indent=1))
    if a.out:
        json.dump({"summary": summary, "excluded": excluded, "not_parsed": unparsed, "rows": sorted(rows, key=lambda r: r["file"])}, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("wrote", a.out)


if __name__ == "__main__":
    main()
