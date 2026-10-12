"""Collect every item-bank pin from the served comprehension manifests and download each distinct URL into banks/ (raw bytes, untrusted).
Writes bank_index.json: one row per bank id (items_sha256 or inline manifest hash) with its pin, source kind, download status, and the measurements that use it."""
import json, urllib.request, hashlib, os, time, collections
rows = json.load(open("comp_measurements.json")); M = json.load(open("manifests.json"))
banks = {}; no_manifest = []; unpinned = []
for m in rows:
    mh = m.get("manifest_hash"); mb = (M.get(mh) or {}).get("body")
    if not mb: no_manifest.append(mh); continue
    sha = mb.get("items_sha256"); url = mb.get("items_url"); kind = None
    if mb.get("items"): kind = "inline"
    elif mb.get("items_ref"): kind = "items_ref"; sha = sha or mb["items_ref"].get("sha256"); url = url or mb["items_ref"].get("url")
    elif mb.get("test_set"): kind = "test_set"
    elif url: kind = "url"
    bid = sha or ("manifest:" + mh)
    if kind is None: unpinned.append(mh); continue
    b = banks.setdefault(bid, {"bank_id": bid, "kind": kind, "url": url, "items_sha256": sha, "manifest_hashes": [], "item_counts": mb.get("item_counts")})
    b["manifest_hashes"].append(mh)
    if kind in ("inline", "test_set") and "inline_from" not in b: b["inline_from"] = mh
print("rows", len(rows), "manifests", len(M), "no_manifest", len(no_manifest), "unpinned", len(unpinned), "banks", len(banks), collections.Counter(b["kind"] for b in banks.values()))
for bid, b in banks.items():
    if b["kind"] in ("inline", "test_set"):
        mb = M[b["inline_from"]]["body"]; items = mb.get("items") or mb.get("test_set")
        path = f"banks/{bid.replace(':','_')[:24]}.json"; open(path, "w").write(json.dumps({"items": items, "_from_manifest": b["inline_from"]}, ensure_ascii=False)); b["path"] = path; b["status"] = "inline"; continue
    url = b["url"]; path = f"banks/{bid[:24]}.json"; b["path"] = path
    if os.path.exists(path): b["status"] = "cached"; continue
    if not str(url).startswith("https://"): b["status"] = "non-https"; continue
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "reticuli-scan/1"}), timeout=60) as r:
            data = r.read(50_000_000); open(path, "wb").write(data); b["status"] = f"http {r.status}"; b["bytes"] = len(data)
    except Exception as e: b["status"] = "error: " + repr(e)[:160]
    time.sleep(0.2)
json.dump({"banks": list(banks.values()), "no_manifest": no_manifest, "unpinned": unpinned}, open("bank_index.json", "w"), indent=1)
print(collections.Counter(b["status"].split(":")[0] for b in banks.values()))
for b in banks.values():
    if b["status"].startswith("error") or b["status"] == "non-https": print(b["bank_id"][:16], b["status"][:120], str(b["url"])[:100])
