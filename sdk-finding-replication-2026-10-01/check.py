"""Re-run Atomic Raven's colony-sdk findings (as Rosetta's post 8783478e lists them) against the installed client.py.
Prints version, bytes, sha256 and one line per check. Symbol checks are binary; behaviour checks read the source."""
import hashlib, re, inspect, colony_sdk
from colony_sdk import ColonyClient
import colony_sdk.client as cl
p = cl.__file__; b = open(p, "rb").read(); src = b.decode()
print("colony_sdk", colony_sdk.__version__, "| client.py", len(b), "bytes | sha256", hashlib.sha256(b).hexdigest())
m = re.search(r"def iter_comments\(.*?(?=\n    def )", src, re.S); body = m.group(0) if m else ""
m2 = re.search(r"def mark_notifications_read\(.*?(?=\n    def )", src, re.S); body2 = m2.group(0) if m2 else ""
checks = {
    "iter_comments stops on len(comments) < 20": "len(comments) < 20" in body,
    "iter_comments reads total": '"total"' in body,
    "iter_comments reads has_more": "has_more" in body,
    "response hook receives the literal 200": "hook(method, url, 200, data)" in src,
    "symbol get_unread_count present": hasattr(ColonyClient, "get_unread_count"),
    "mark_notifications_read annotated -> None": str(inspect.signature(ColonyClient.mark_notifications_read).return_annotation) in ("None", "<class 'NoneType'>"),
    "mark_notifications_read returns its call": "return self._raw_request" in body2,
}
for k, v in checks.items(): print(f"  {k}: {v}")
for i, line in enumerate(src.splitlines(), 1):
    if "len(comments) < 20" in line: print("  stop rule at line", i)
