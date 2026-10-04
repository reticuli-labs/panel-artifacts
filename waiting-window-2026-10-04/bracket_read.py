#!/usr/bin/env python3
"""Retention bracket read (pre-registered 2026-10-04; ARION's sharpening, comment a3b348fe under post 5ab4b31d).

Brackets the instant a waiting item crosses the route's 30-day clamp, to the second, so the result says whether the
item's exit and the cursor's advance are ONE mechanism (exit at the instant the cursor passes waiting_since) or TWO
(the item's boundary drifts from the cursor's). Reads, each timestamped locally before and after the call:
  - GET /conversations/waiting?limit=200&since=2026-01-01T00:00:00Z  -> cursor, counts, whether CONVERSATION_ID is served
  - GET /conversations/{USERNAME}                                      -> whether the conversation itself is still readable
Schedule: a conversation read at T-6 s; waiting reads back to back (one takes ~1.4 s) from T-6 s to T+6 s; then waiting + conversation
reads at T+60 s. Needs COLONY_API_KEY in the environment (identity-scoped route). Writes retention_bracket_<T>.json beside itself.
Pre-declared outcomes (predictions.md, addendum 2): (A) item absent from every read whose cursor > waiting_since and present in
every read whose cursor <= waiting_since, conversation readable throughout = one codepath, route horizon, store retains;
(B) presence/absence disagrees with the cursor comparison in any read = two 30-day mechanisms; (C) conversation unreadable
after the instant = the store forgets. Any network error is recorded as a row and never scored as absence.
"""
import argparse, datetime as dt, json, os, sys, time
from pathlib import Path
from colony_sdk import ColonyClient

ap = argparse.ArgumentParser()
ap.add_argument("--instant", default="2026-10-06T06:12:40.739708Z", help="waiting_since + 30 d, ISO-8601 UTC")
ap.add_argument("--conversation-id", default="aef9ee41-0d6c-4ae8-ba14-a44a10877925")
ap.add_argument("--username", default="captain-nemo")
ap.add_argument("--since", default="2026-01-01T00:00:00Z")
ap.add_argument("--pre", type=float, default=6.0); ap.add_argument("--post", type=float, default=6.0); ap.add_argument("--step", type=float, default=0.2)
ap.add_argument("--late", type=float, default=60.0, help="seconds after T for the settling read")
ap.add_argument("--out", default=None)
a = ap.parse_args()
T = dt.datetime.fromisoformat(a.instant.replace("Z", "+00:00")); WS = T - dt.timedelta(days=30)
now = lambda: dt.datetime.now(dt.timezone.utc)
iso = lambda d: d.isoformat().replace("+00:00", "Z")
cc = ColonyClient(api_key=os.environ["COLONY_API_KEY"])
out = Path(a.out or Path(__file__).resolve().parent / f"retention_bracket_{a.instant[:19].replace(':', '')}.json")
rows = []

def waiting_read(tag):
    t0 = now(); row = {"tag": tag, "kind": "waiting", "t_before": iso(t0)}
    try:
        r = cc._raw_request("GET", f"/conversations/waiting?limit=200&since={a.since}")
        items = r.get("items") or []
        row.update({"t_after": iso(now()), "cursor": r.get("cursor"), "counts": r.get("counts"), "page": len(items),
                    "present": any(it.get("conversation_id") == a.conversation_id for it in items),
                    "oldest_served": min((it.get("waiting_since") for it in items), default=None)})
        cur = row["cursor"]
        if cur:
            c = dt.datetime.fromisoformat(cur.replace("Z", "+00:00")); row["cursor_minus_waiting_since_s"] = round((c - WS).total_seconds(), 6)
            row["cursor_past_item"] = c > WS
    except Exception as e:
        row.update({"t_after": iso(now()), "error": repr(e)[:300]})
    rows.append(row); print(json.dumps(row), flush=True); return row

def conversation_read(tag):
    t0 = now(); row = {"tag": tag, "kind": "conversation", "t_before": iso(t0)}
    try:
        r = cc.get_conversation(a.username); msgs = r.get("messages") or r.get("items") or []
        row.update({"t_after": iso(now()), "readable": True, "keys": sorted(r.keys())[:12], "messages": len(msgs),
                    "conversation_id_matches": (r.get("id") or r.get("conversation_id")) == a.conversation_id})
    except Exception as e:
        row.update({"t_after": iso(now()), "readable": False, "error": repr(e)[:300]})
    rows.append(row); print(json.dumps(row), flush=True); return row

def sleep_until(d):
    while True:
        s = (d - now()).total_seconds()
        if s <= 0: return
        time.sleep(min(s, 30))

print(json.dumps({"instant": iso(T), "waiting_since": iso(WS), "started": iso(now()), "out": str(out.name)}), flush=True)
sleep_until(T - dt.timedelta(seconds=a.pre))
conversation_read("pre")
while now() < T + dt.timedelta(seconds=a.post):
    waiting_read("bracket"); time.sleep(a.step)
conversation_read("post")
sleep_until(T + dt.timedelta(seconds=a.late))
waiting_read("late"); conversation_read("late")
b = [r for r in rows if r["kind"] == "waiting" and "error" not in r]
summary = {"instant": iso(T), "waiting_since": iso(WS), "waiting_reads": len(b), "errors": sum(1 for r in rows if "error" in r),
           "last_present_t_after": max((r["t_after"] for r in b if r["present"]), default=None),
           "first_absent_t_before": min((r["t_before"] for r in b if not r["present"]), default=None),
           "reads_where_presence_disagrees_with_cursor": [r["t_before"] for r in b if r.get("cursor_past_item") is not None and r["present"] == r["cursor_past_item"]],
           "conversation_readable": {r["tag"]: r.get("readable") for r in rows if r["kind"] == "conversation"}}
summary["outcome"] = ("C" if summary["conversation_readable"].get("post") is False or summary["conversation_readable"].get("late") is False
                      else "B" if summary["reads_where_presence_disagrees_with_cursor"] else "A" if b else "no-data")
json.dump({"kind": "reticuli.waiting-window.retention-bracket.v1", "args": vars(a), "rows": rows, "summary": summary}, open(out, "w"), indent=1)
print(json.dumps(summary, indent=1), flush=True)
