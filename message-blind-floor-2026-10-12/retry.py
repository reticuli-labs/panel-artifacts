import json, urllib.request, time, os
I = json.load(open("bank_index.json"))
for b in I["banks"]:
    if not b["status"].startswith("error"): continue
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(b["url"], headers={"User-Agent": "reticuli-scan/1"}), timeout=60) as r:
                data = r.read(50_000_000); open(b["path"], "wb").write(data); b["status"] = f"http {r.status}"; b["bytes"] = len(data); break
        except Exception as e:
            b["status"] = "error: " + repr(e)[:160]; time.sleep(8 * (attempt + 1))
    time.sleep(4)
json.dump(I, open("bank_index.json", "w"), indent=1)
import collections; print(collections.Counter(b["status"].split(":")[0] for b in I["banks"]))
