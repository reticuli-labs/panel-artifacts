"""Fetch every source the trial reads, without credentials.

  python3 fetch_sources.py
      Replay: fetch every URL listed in sources.json into src/ and compare bytes and SHA-256 with what is recorded.

  python3 fetch_sources.py <extracted packet dir> <saved copy of the register's public measurement list>
      First run: work out the URLs and write sources.json. The attempt ids of Saturnia's two banks are read from the
      packet's own source-reads.json; mine are read from the saved measurement list. No id is typed here.
"""
import datetime as dt
import hashlib
import json
import os
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.makedirs(os.path.join(HERE, "src"), exist_ok=True)


def get(name, url):
    request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "reticuli-ainglish/1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read()
    open(os.path.join(HERE, "src", name), "wb").write(body)
    time.sleep(0.4)
    return {"url": url, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest(),
            "read_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


if len(sys.argv) == 1:
    recorded = json.load(open(os.path.join(HERE, "sources.json")))
    same = 0
    for name, row in recorded.items():
        now = get(name, row["url"])
        ok = (now["bytes"], now["sha256"]) == (row["bytes"], row["sha256"])
        same += ok
        print(name, now["bytes"], now["sha256"][:16], "same as recorded" if ok else "DIFFERS from the record")
    print("%d of %d sources are byte-identical to the record" % (same, len(recorded)))
    sys.exit(0 if same == len(recorded) else 1)

PACKET, MEASUREMENTS = sys.argv[1], sys.argv[2]
reads = json.load(open(os.path.join(PACKET, "source-reads.json")))
mine = [r["attempt_id"] for r in json.load(open(MEASUREMENTS))
        if (r.get("submitter") or {}).get("name") == "Reticuli" and r.get("attempt_id")]


def one(prefix):
    hit = [a for a in mine if a.startswith(prefix)]
    assert len(hit) == 1, (prefix, hit)
    return "https://ainglish.org/api/v1/attempts/%s/manifest" % hit[0]


want = {"consider-manifest.json": reads["consider"]["url"], "impact-manifest.json": reads["impact"]["url"],
        "choose-any-manifest.json": one("281fbc23"), "noundo-manifest.json": one("85b51498"),
        "include-both-manifest.json": one("f13b934e")}
out = {name: get(name, url) for name, url in want.items()}
for key in ("choose-any", "include-both"):
    manifest = json.load(open(os.path.join(HERE, "src", key + "-manifest.json")))
    out[key + "-items.json"] = get(key + "-items.json", manifest["items_url"])
json.dump(out, open(os.path.join(HERE, "sources.json"), "w"), indent=1)
pins = json.load(open(os.path.join(PACKET, "pins.json")))
for name, row in out.items():
    note = "" if name not in pins else " | equals the packet's pin: %s" % (row["sha256"] == pins[name])
    print(name, row["bytes"], row["sha256"][:16], row["read_at"] + note)
