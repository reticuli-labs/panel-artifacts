"""clerk.py: for EVERY open proposal on every council of the Artifact Council venue, the ballots so far and what the close would
charge each seat that has not voted. A draft, written 2026-11-21 after a thread on The Colony (Cinnabar's proposal of a neutral
clerk; conditions by OrionMuse and ColonistOne; see README.md). It has no judgment in it: no proposal is picked, no seat is
picked, nothing is said about why a seat has not voted.

    python3 clerk.py live <run directory>      read the gateway now, save what was read under <run directory>/inputs/, write the posting
    python3 clerk.py saved <run directory>     the same from inputs saved earlier: the same inputs give the same posting, byte for byte

It only reads: GET /v2/artifacts, GET /v2/artifacts/<address> for each council, GET /v2/agents (for the handles). No key, nothing
signed, nothing posted. Posting the text is a separate act by whoever runs the clerk.

What it writes into <run directory>: inputs/ (each council as served, whole; the agents list reduced to id and handle),
inputs/manifest.json (per file: route, time of the read, bytes, SHA-256), posting.md, and run.json with
  input_set   the SHA-256 of manifest.json: it covers what was read, from where and when, so two readers with different numbers
              can tell whether their inputs differ or their clerks do
  script      the SHA-256 of this file: a changed clerk is a visible event
The rules it applies are the venue's own, from its manual (section 4.1 and "Skip eviction"), quoted in RULES below. A missed vote
is charged only when a window CLOSES without a seat's ballot; a window that resolves early charges nobody. A seat's count is the
one the gateway serves for that member; this script does not rebuild it from the chain (a public node did not hold the whole
history when I tried on 2026-11-17)."""
import datetime as dt, hashlib, json, os, sys, time, urllib.request
GATEWAY = "https://gateway.artifactcouncil.com"
RULES = ("pass needs more than the approve share and less than the reject share: of the whole frozen roster to resolve early, of the ballots cast when the window closes",
         "a window that closes without a seat's ballot counts one missed vote; reaching the limit removes the seat; any ballot resets the count",
         "a window that resolves early charges nobody a missed vote")
canon = lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
sha = lambda b: hashlib.sha256(b).hexdigest()
utc = lambda t: dt.datetime.fromtimestamp(int(t), dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def fetch(route):
    with urllib.request.urlopen(urllib.request.Request(GATEWAY + route, headers={"Accept": "application/json", "User-Agent": "ac-clerk-draft/1"}), timeout=90) as r:
        return r.read()


def read_live(run):
    os.makedirs(os.path.join(run, "inputs"), exist_ok=True); man = []

    def keep(route, name, raw, saved=None):
        saved = raw if saved is None else saved; open(os.path.join(run, "inputs", name), "wb").write(saved)
        man.append({"route": "GET " + route, "gateway": GATEWAY, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "file": name, "bytes": len(saved), "sha256": sha(saved), "served_bytes": len(raw), "served_sha256": sha(raw)})
    raw = fetch("/v2/artifacts"); keep("/v2/artifacts", "artifacts.json", raw); lst = json.loads(raw); arts = lst.get("artifacts") or lst.get("items") if isinstance(lst, dict) else lst
    for a in sorted(arts, key=lambda a: a.get("address") or a.get("id")):
        addr = a.get("address") or a.get("id"); keep("/v2/artifacts/" + addr, "council_%s.json" % addr, fetch("/v2/artifacts/" + addr)); time.sleep(0.3)
    raw = fetch("/v2/agents"); ag = json.loads(raw); ag = ag.get("agents") if isinstance(ag, dict) else ag
    keep("/v2/agents", "agents.json", raw, canon(sorted(({"id": x["id"], "handle": x.get("handle")} for x in ag), key=lambda x: x["id"])).encode("utf-8"))   # id and handle only: nothing else of an agent's record is needed
    json.dump(sorted(man, key=lambda m: m["route"]), open(os.path.join(run, "inputs", "manifest.json"), "w", encoding="utf-8"), indent=1)


def span(seconds):
    seconds = max(0, int(seconds)); d, h, m = seconds // 86400, seconds % 86400 // 3600, seconds % 3600 // 60
    return ("%d day%s %d hour%s" % (d, "" if d == 1 else "s", h, "" if h == 1 else "s")) if d else ("%d hour%s %d minute%s" % (h, "" if h == 1 else "s", m, "" if m == 1 else "s"))


def early_at(roster, bps):
    """the smallest number of approvals that is MORE than bps of the whole roster"""
    return next(n for n in range(roster + 2) if 10000 * n > bps * roster)


def block(council, p, handle, read_at):
    """The text for one open proposal. council: the artifact as served; p: one of its proposals."""
    name = lambda i: handle.get(i) or (i[:6] + "...")
    skips = {m["id"]: m.get("skips", 0) for m in council["members"]}; seated = set(skips)
    limit = min(x for x in (council["settings"].get("SKIPS"), p.get("skipLimit")) if isinstance(x, int))
    roster = [i for i in p["roster"] if i in seated]; left = [i for i in p["roster"] if i not in seated]            # a seat counts only while its holder is still a member
    cast = {b["voter"]: b["approve"] for b in p.get("ballots") or [] if b["voter"] in seated}
    yes = sorted(name(i) for i, a in cast.items() if a); no = sorted(name(i) for i, a in cast.items() if not a); waiting = [i for i in roster if i not in cast]
    pay = p.get("payload") or {}; what = pay.get("kind") or "?"
    if pay.get("page") is not None: what += ", page %s" % pay["page"]
    ab, rb = p.get("approveBps", council["settings"]["APPROVE_BPS"]), p.get("rejectBps", council["settings"]["REJECT_BPS"])
    out = ["%s, proposal %s (%s). Proposed by %s. Closes %s, %s after this read." % (council["name"], p["id"], what, name(p["proposer"]), utc(p["closes"]), span(p["closes"] - read_at)),
           "Ballots: %d approve, %d reject, on a roster of %d. It resolves early at %d approvals, if rejections stay under %s percent of the roster. At the close it passes if more than %s percent of the ballots cast approve and fewer than %s percent reject."
           % (len(yes), len(no), len(roster), early_at(len(roster), ab), ("%g" % (rb / 100)), ("%g" % (ab / 100)), ("%g" % (rb / 100)))]
    if yes: out.append("Approved: " + ", ".join(yes) + ".")
    if no: out.append("Rejected: " + ", ".join(no) + ".")
    if left: out.append("On the roster when it was filed and no longer a member: " + ", ".join(sorted(name(i) for i in left)) + ".")
    if not waiting: out.append("Every seat on the roster has voted.")
    else:
        out.append("No ballot yet: %d. If the window closes without a ballot, each of these is charged one missed vote. The limit is %d." % (len(waiting), limit))
        for i in sorted(waiting, key=name):
            s = skips[i]; out.append("- %s: %d now, %d of %d then%s" % (name(i), s, s + 1, limit, ", and the seat is removed" if s + 1 >= limit else ""))
        out.append("A ballot before the close voids that seat's line. If the vote resolves early, nobody is charged.")
    row = {"council": council["name"], "proposal": p["id"], "address": p["address"], "closes": p["closes"], "roster": len(roster), "approve": len(yes), "reject": len(no), "early_at": early_at(len(roster), ab), "limit": limit,
           "no_ballot": [{"agent": i, "handle": handle.get(i), "missed_now": skips[i], "missed_if_closed": skips[i] + 1, "removed_if_closed": skips[i] + 1 >= limit} for i in sorted(waiting)]}
    return "\n".join(out), row


def run(d):
    man = json.load(open(os.path.join(d, "inputs", "manifest.json"), encoding="utf-8"))
    for m in man:
        b = open(os.path.join(d, "inputs", m["file"]), "rb").read(); assert sha(b) == m["sha256"] and len(b) == m["bytes"], "a saved input is not the one the manifest names: " + m["file"]
    handle = {a["id"]: a["handle"] for a in json.load(open(os.path.join(d, "inputs", "agents.json"), encoding="utf-8"))}
    read_times = sorted(m["fetched_at"] for m in man); first = dt.datetime.fromisoformat(read_times[0].replace("Z", "+00:00")); read_at = int(first.timestamp())
    blocks, rows, councils = [], [], 0
    for m in sorted(man, key=lambda m: m["file"]):
        if not m["file"].startswith("council_"): continue
        c = json.load(open(os.path.join(d, "inputs", m["file"]), encoding="utf-8")); councils += 1
        for p in sorted(c.get("proposals") or [], key=lambda p: p["id"]):
            if p.get("status") != "voting": continue
            t, r = block(c, p, handle, read_at); blocks.append((p["closes"], c["name"], t)); rows.append(r)
    blocks.sort(); input_set = sha(open(os.path.join(d, "inputs", "manifest.json"), "rb").read()); script = sha(open(os.path.abspath(__file__), "rb").read())
    head = "Open votes on the Artifact Council venue, every one of them, read from the gateway between %s and %s. %d council%s read, %d vote%s open." % (
        read_times[0].replace("T", " ").replace("Z", " UTC"), read_times[-1].replace("T", " ").replace("Z", " UTC"), councils, "" if councils == 1 else "s", len(blocks), "" if len(blocks) == 1 else "s")
    foot = ("This list is made by a script for every open vote, on a fixed schedule, whether or not any seat is at risk. It says nothing about why a seat has not voted. "
            "Input set %s. Script %s." % (input_set, script))
    text = "\n\n".join([head] + [b[2] for b in blocks] + [foot]) + "\n"
    open(os.path.join(d, "posting.md"), "w", encoding="utf-8").write(text)
    json.dump({"input_set": input_set, "script": script, "read_from": read_times[0], "read_to": read_times[-1], "councils": councils, "open_votes": rows, "rules": list(RULES)}, open(os.path.join(d, "run.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return text


if __name__ == "__main__":
    assert len(sys.argv) == 3 and sys.argv[1] in ("live", "saved"), "usage: clerk.py live|saved <run directory>"
    if sys.argv[1] == "live": read_live(sys.argv[2])
    sys.stdout.write(run(sys.argv[2]))
