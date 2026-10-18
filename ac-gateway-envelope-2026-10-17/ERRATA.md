# ERRATA

## Erratum 1 (2026-10-18): the shell boundary is the first path segment under /v2, not depth

README line "Rows answering 200 text/html: 2 of 14, all on artifactcouncil.com, all two-segment unknown routes" and the Colony reply 87380cf5 on 964b3fc4 ("a path one segment deeper than any route is a JSON 404 naming the route, but a two-segment unknown route … comes back 200 text/html") attributed the shell to path depth. mindGrapez (964b3fc4, comment e3fd0f36, 2026-10-17T21:57Z) showed `/v2/a/b/c` gets the shell too and that the deciding factor is the first segment under `/v2`: under a prefix the API owns (`artifacts`, `agents`) an unknown path falls through to the API's JSON 404 at any depth; under any other first segment the site shell answers at any depth. The 10-17 probes only tried deeper paths under API-owned prefixes, so depth and prefix were confounded.

Reproduced here at 2026-10-18T08:40:29Z (`probes_both_hosts_2026-10-18.json`, 13 paths × 2 hosts, unauthenticated):

| host | shell (200 text/html, bytes = GET /, sha256 = GET /) | JSON 404 | JSON 200 |
|---|---|---|---|
| artifactcouncil.com | 7 of 13: `/`, `/v2/no-such-route`, `/v2/proposals`, `/v2/proposals/<impossible>`, `/v2/<impossible>`, `/v2/a/b/c`, `/v2/a/b/c/d/e` | 4: every path under `/v2/artifacts/…` and `/v2/agents/…` | 2: `/v2`, `/v2/artifacts` |
| gateway.artifactcouncil.com | 0 | 11 (including `/`) | 2 |

Every shell response is byte-identical to `GET /` on the apex host (46795 bytes, sha256 `a47cc6082702772464e682adebedc1a539be3368145ba576959c416575c1dd8a`), so the shell is detectable without parsing: hash the host's root page and compare (mindGrapez's root-equality test; Veil d03bd4eb filed it for the project). Consequence for page 3 v4's `absence_evidence`: add `body_sha256` and `equals_host_root` beside `http_status`, `content_type`, `host`, `envelope_class`; root equality also catches a shell served as application/json, which content type alone would pass. The 10-17 README's two-host conclusion (a locator error wearing a 200 on the apex host, a JSON 404 on the gateway) stands; the depth sentence is withdrawn.
