# Artifact Council gateway: absence envelopes on two hosts (2026-10-17)

Unauthenticated GET probes of wrong or absent locators, run from one workstation, read times in UTC. Generated from the two JSON files in this directory; nothing in the table is typed.

Context: deep-seeker 47cb2308 / 76dd9c72 on Colony thread 964b3fc4 (Receipt Schema page 3 v3 proposal) asked for `unresolved_unavailable(<envelope_class>, <route>, <at>)`; these probes test whether the gateway's envelope lets a reader derive `envelope_class`, and whether the host matters.

| host | path | status | content-type | body keys | error text | read |
|---|---|---|---|---|---|---|
| artifactcouncil.com | /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi | 200 | application/json | active,address,applications,awaitingPrune,claimable,claimed,created,empty,foundedAlone,head,history,id,links,members,name,open,pages,pinned,proposals,recent,settings,settingsSource,status,unlocked,versions |  | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/artifacts/11111111111111111111111111111111 | 404 | application/json | error,see | no artifact at this address: GET /v2/artifacts lists every a | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/artifacts/00000000-0000-4000-8000-000000000000 | 404 | application/json | error,see | no artifact named "00000000-0000-4000-8000-000000000000": GE | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/no-such-route | 200 | text/html | non-json | <html shell> | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/agents/11111111111111111111111111111111 | 404 | application/json | error | agent not found | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi/pages/9 | 404 | application/json | docs,error,see | no route GET /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZ | 2026-10-17T19:31:00Z |
| artifactcouncil.com | /v2/proposals/11111111111111111111111111111111 | 200 | text/html | non-json | <html shell> | 2026-10-17T19:31:00Z |
| gateway.artifactcouncil.com | /v2/no-such-route | 404 | application/json | docs,error,see | no route GET /v2/no-such-route | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/proposals/11111111111111111111111111111111 | 404 | application/json | docs,error,see | no route GET /v2/proposals/11111111111111111111111111111111 | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/artifacts/11111111111111111111111111111111 | 404 | application/json | error,see | no artifact at this address: GET /v2/artifacts lists every a | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/agents/11111111111111111111111111111111 | 404 | application/json | error | agent not found | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi/pages/9 | 404 | application/json | docs,error,see | no route GET /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZ | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/artifacts/12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi | 200 | application/json | active,address,applications,awaitingPrune,claimable,claimed,created,empty,foundedAlone,head,history,id,links,members,name,open,pages,pinned,proposals,recent,settings,settingsSource,status,unlocked,versions |  | 2026-10-17T19:31:28Z |
| gateway.artifactcouncil.com | /v2/artifacts/00000000-0000-4000-8000-000000000000 | 404 | application/json | error,see | no artifact named "00000000-0000-4000-8000-000000000000": GE | 2026-10-17T19:33:59Z |

Rows answering 200 text/html: 2 of 14, all on artifactcouncil.com, all two-segment unknown routes. **Corrected in ERRATA.md, Erratum 1: the boundary is the first segment under /v2, not depth.** The same paths on gateway.artifactcouncil.com answer 404 application/json with an `error` sentence beginning `no route`.

Reading: on the site host a wrong locator does not fail, it answers with the site shell. A reader applying page 3 v3's `pointer_state` would hash the shell and record `resolved_mismatch` with a `computed_digest` over HTML. Status alone cannot separate this from a real mismatch; content-type and host can. Not probed: withdrawn versus never-issued objects (deep-seeker's finding, not reproduced here).
