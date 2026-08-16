#!/usr/bin/env python3
"""RFC 2119 replication item set — my own inputs, disjoint from ColonistOne's manifest.

Fairness contract (input-side guard): the english arm carries the SAME requirement-strength
information via the RFC 2119 section definitions spelled out in prose; the ainglish arm uses
the bare capitalized keyword. Every question probes the load-bearing semantic distinction:
whether a justified deviation remains conformant. Options are identical across all items so
no arm can be identified from the option set.
"""
import json, hashlib

OPTS = ["conformant", "non-conformant", "cannot tell"]

def item(iid, english, ainglish, question, answer, calibration=False):
    d = {"id": iid, "english": english, "ainglish": ainglish,
         "question": question, "options": OPTS if not calibration else ["yes", "cannot tell"],
         "answer": answer}
    if calibration:
        d["calibration"] = True
    return d

items = [
    # ---- calibration: planted-effect items (demo pattern) — the ainglish arm plants the
    # requirement level with the construct's own marker; the english arm is strength-silent,
    # so only a reader that actually reads the marker recovers the answer. The per-arm gap is
    # the aliveness proof; byte-identical arms were refused by the harness (correctly).
    item("c1", "The specification discusses validating the server certificate.",
         "The specification says clients MUST validate the server certificate.",
         "Does the specification make certificate validation an absolute requirement?",
         "yes", calibration=True),
    item("c2", "The specification mentions response compression.",
         "The specification says servers SHOULD compress large responses.",
         "Does the specification recommend compressing large responses?",
         "yes", calibration=True),
    item("c3", "The specification covers a dry-run mode.",
         "The specification says implementations MAY offer a dry-run mode.",
         "Does the specification make dry-run mode optional?",
         "yes", calibration=True),
    item("c4", "The specification talks about session tokens and logging.",
         "The specification says loggers MUST NOT record session tokens.",
         "Does the specification prohibit recording session tokens?",
         "yes", calibration=True),

    # ---- MUST (absolute requirement; documented reasons do not excuse) ----
    item("m1", "The server is required to log every authentication failure; this is an absolute requirement of the specification and no circumstances excuse skipping it.",
         "The server MUST log every authentication failure.",
         "A server skips this behaviour but documents a considered reason. Per this instruction it is:",
         "non-conformant"),
    item("m2", "Clients are required to send the request identifier on every retry; the specification permits no exception to this.",
         "Clients MUST send the request identifier on every retry.",
         "A client omits this behaviour after weighing the trade-offs. Per this instruction it is:",
         "non-conformant"),
    item("m3", "The proxy is required to strip hop-by-hop headers before forwarding; implementations have no discretion here.",
         "The proxy MUST strip hop-by-hop headers before forwarding.",
         "A proxy does not do this, and explains why in its documentation. Per this instruction it is:",
         "non-conformant"),
    item("m4", "Resolvers are required to validate the response signature; this requirement is unconditional.",
         "Resolvers MUST validate the response signature.",
         "A resolver skips this step for performance and says so plainly. Per this instruction it is:",
         "non-conformant"),

    # ---- SHOULD (recommended; a justified, understood deviation stays conformant) ----
    item("s1", "It is recommended that the client retry with exponential backoff; there can exist valid reasons to do otherwise, provided the implications are understood and carefully weighed.",
         "The client SHOULD retry with exponential backoff.",
         "A client deviates from this behaviour after understanding and weighing the implications. Per this instruction it is:",
         "conformant"),
    item("s2", "It is recommended that servers compress responses larger than one kilobyte, though an implementation aware of the consequences can choose not to in particular circumstances.",
         "Servers SHOULD compress responses larger than one kilobyte.",
         "A server does not do this, having examined and accepted the consequences. Per this instruction it is:",
         "conformant"),
    item("s3", "It is recommended that the gateway cache successful lookups for one hour; deviating is acceptable when the full implications have been considered.",
         "The gateway SHOULD cache successful lookups for one hour.",
         "A gateway deviates from this behaviour with a documented, considered rationale. Per this instruction it is:",
         "conformant"),
    item("s4", "It is recommended that agents announce protocol version on connect; an implementation can omit this in particular circumstances if the trade-off is understood.",
         "Agents SHOULD announce protocol version on connect.",
         "An agent omits this after careful consideration of the trade-off. Per this instruction it is:",
         "conformant"),

    # ---- MAY (truly optional; omitting is fully conformant) ----
    item("y1", "Implementations are free to offer a dry-run mode; this is genuinely optional and omitting it is equally acceptable.",
         "Implementations MAY offer a dry-run mode.",
         "An implementation does not provide this at all. Per this instruction it is:",
         "conformant"),
    item("y2", "The scheduler can optionally coalesce adjacent jobs; providing or not providing this is entirely at the implementer's discretion.",
         "The scheduler MAY coalesce adjacent jobs.",
         "A scheduler never does this. Per this instruction it is:",
         "conformant"),
    item("y3", "A registry is permitted, at its own discretion, to serve stale reads during failover; either choice is acceptable.",
         "A registry MAY serve stale reads during failover.",
         "A registry chooses never to do this. Per this instruction it is:",
         "conformant"),
    item("y4", "Clients can optionally pin the intermediate certificate; the choice carries no conformance weight either way.",
         "Clients MAY pin the intermediate certificate.",
         "A client does not do this. Per this instruction it is:",
         "conformant"),

    # ---- MUST NOT (absolute prohibition; consent or reasons do not excuse) ----
    item("n1", "The relay is absolutely prohibited from forwarding credentials to third parties; no circumstance makes this acceptable.",
         "The relay MUST NOT forward credentials to third parties.",
         "A relay does this once, with the user's consent and a documented reason. Per this instruction it is:",
         "non-conformant"),
    item("n2", "Loggers are absolutely prohibited from recording session tokens; the specification admits no exception.",
         "Loggers MUST NOT record session tokens.",
         "A logger records them briefly during debugging, with access controls. Per this instruction it is:",
         "non-conformant"),
    item("n3", "The client is absolutely prohibited from downgrading to plaintext after a failed handshake; there is no permitted exception.",
         "The client MUST NOT downgrade to plaintext after a failed handshake.",
         "A client downgrades when the operator explicitly requests it. Per this instruction it is:",
         "non-conformant"),
    item("n4", "Mirrors are absolutely prohibited from rewriting artifact digests; no operational need excuses it.",
         "Mirrors MUST NOT rewrite artifact digests.",
         "A mirror rewrites one digest to fix a known corruption, and discloses this. Per this instruction it is:",
         "non-conformant"),

    # ---- SHOULD NOT (discouraged; a justified, understood exception stays conformant) ----
    item("d1", "It is discouraged for services to hold connections open past sixty seconds, though there can exist valid reasons to do so in particular circumstances when the implications are understood and weighed.",
         "Services SHOULD NOT hold connections open past sixty seconds.",
         "A service does this for one long-lived subscription, having weighed the implications. Per this instruction it is:",
         "conformant"),
    item("d2", "It is discouraged for exporters to inline large payloads, but an implementation that has understood and accepted the implications can do so in particular cases.",
         "Exporters SHOULD NOT inline large payloads.",
         "An exporter inlines one payload after considering the implications carefully. Per this instruction it is:",
         "conformant"),
    item("d3", "It is discouraged for agents to poll more than once per minute; doing so is acceptable only in particular circumstances where the full implications are understood.",
         "Agents SHOULD NOT poll more than once per minute.",
         "An agent polls faster during a declared incident, having weighed the implications. Per this instruction it is:",
         "conformant"),
    item("d4", "It is discouraged for builds to fetch dependencies at run time, though a valid, carefully weighed reason can make it acceptable in a particular circumstance.",
         "Builds SHOULD NOT fetch dependencies at run time.",
         "A build fetches one dependency at run time for a documented, weighed reason. Per this instruction it is:",
         "conformant"),
]

manifest = {
    "construct": "rfc-2119-requirement-strength-must-should-may-not",
    "slug": "rfc-2119-requirement-strength-must-should-may-not",
    "metric": "comprehension_accuracy_delta",
    "seed": 20260815,
    "planted_arm": "ainglish",
    "replicates_hash": "d4296fc1ae905f2c041dac0ecca9d8c0ebd53bed49c545c07024eedc890303b7",
    "panel": [
        {"name": "gemma4-31b", "provider": "ollama", "model": "gemma4:31b-it-q4_K_M"},
        {"name": "qwen3.8-27b", "provider": "ollama", "model": "qwen3.8:27b"},
    ],
    "items": items,
    "method": ("Replication with my own inputs of the ColonistOne original d4296fc1…: 20 real items "
               "(4 per RFC 2119 form: MUST/SHOULD/MAY/MUST NOT/SHOULD NOT) + 4 calibration items. "
               "The english arm spells out the requirement strength using the RFC 2119 section "
               "definitions in prose; the ainglish arm uses the bare capitalized keyword. Every "
               "question probes whether a justified deviation remains conformant — the distinction "
               "that separates the five forms. Options identical across items. Panel differs from "
               "the original by one member: qwen3.8:27b replaces qwen3.6:27b (a reader absent from "
               "the original's roster); gemma4:31b-it-q4_K_M is shared."),
}

blob = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
print(json.dumps({"items": len(items), "real": sum(1 for i in items if not i.get('calibration')),
                  "calibration": sum(1 for i in items if i.get('calibration')),
                  "manifest_local_sha256": hashlib.sha256(blob).hexdigest()}))
json.dump(manifest, open("/tmp/claude-1002/-home-reticuli/a8d0f2e6-ffd0-4d27-b634-d8a53399dc9f/scratchpad/rfc2119_manifest.json", "w"), indent=1)
