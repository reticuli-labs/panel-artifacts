"""blind_read.py <items.jsonl> <reads.jsonl>: put each line of the first file to one local reader and append its answer to the
second. Lines need: id, question, options, and the text under `blind` or `text`. A line whose id is already in the output is not
asked again, so the run can be stopped and started. The prompt is the one the Ainglish panel harness sends (panel.py, ask(),
answer protocol opaque-choice-v1), copied here so that this file runs alone; the request settings are in READER below.
Talks only to the model server on this machine (READER_URL, default the local Ollama). WORKERS (default 4) reads at once."""
import concurrent.futures as cf, json, os, sys, threading, time, urllib.request
URL = os.environ.get("READER_URL", "http://localhost:11434/v1/chat/completions")
READER = {"model": os.environ.get("READER_MODEL", "qwen3.8:27b"), "temperature": 0, "seed": 0, "reasoning_effort": "none", "max_tokens": 1024}
CODES = [chr(c) for c in range(ord("A"), ord("Z") + 1)]


def prompt_for(text, question, options):
    choices = "\n".join("%s: %s" % (CODES[i], o) for i, o in enumerate(options))
    return ("Read this message written by one agent to another:\n\n---\n%s\n---\n\nQuestion: %s\nChoices:\n%s\nAnswer with EXACTLY one choice code and nothing else." % (text, question, choices))


def ask(row):
    text = row["blind"] if "blind" in row else row["text"]; body = dict(READER, messages=[{"role": "user", "content": prompt_for(text, row["question"], row["options"])}])
    t = time.time(); last = None
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(URL, json.dumps(body).encode("utf-8"), {"Content-Type": "application/json"}), timeout=300)); break
        except Exception as e: last = e; time.sleep(2 + 3 * attempt)
    else: return {"id": row["id"], "fault": "%s: %s" % (type(last).__name__, str(last)[:120])}
    ch = d["choices"][0]; out = (ch["message"].get("content") or "").strip(); code = out.upper()
    picked = row["options"][CODES.index(code)] if code in CODES[:len(row["options"])] else None
    return {"id": row["id"], "out": out[:40], "picked": picked, "truncated": ch.get("finish_reason") == "length", "ms": int(1000 * (time.time() - t))}


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]; rows = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
    done = {json.loads(l)["id"] for l in open(dst, encoding="utf-8") if l.strip()} if os.path.exists(dst) else set()
    todo = [r for r in rows if r["id"] not in done]; lock = threading.Lock(); n = 0; t0 = time.time()
    print("reader %s | %d lines, %d already read, %d to read" % (json.dumps(READER), len(rows), len(done), len(todo)), flush=True)
    with open(dst, "a", encoding="utf-8") as f, cf.ThreadPoolExecutor(int(os.environ.get("WORKERS", "4"))) as ex:
        for res in ex.map(ask, todo):
            with lock:
                f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush(); n += 1
                if n % 500 == 0: print("%d of %d read, %.0f s" % (n, len(todo), time.time() - t0), flush=True)
    print("read %d in %.0f s" % (n, time.time() - t0))
