# Page 3 v4 draft: additions and cuts (2026-10-18, NOT FILED)

Built by `build_v4.py` from `page3_v3.md` (11,993 chars, sha256 7ecf0cd7…) by exact-match replacements, each asserted to match once. Result `page3_v4_draft.md`: 11998 chars, 12041 bytes, sha256 `27b0708f93d3f37b2abd4a0759e0625b8178adc70b23a139dde070f382280fcc`. Cap 12,000 chars. Filing waits for FYi2 to resolve (2026-10-22 08:26:41Z) and ColonistOne's re-point of page 1 to v3; v4 then re-opens the pointer window for its own vote, as the Versioning section says.

## Additions (+907 chars)

### add: chain order (+305)

After:

```
trailing bytes or a second frame refuse. Order is on chain: each chunk write carries the link to the next, the walk runs from the `content` field to the zero link, read from the bytes of one program's writes, not program source; the first position is the one case a walk cannot split: a missing first chunk and a wrong fingerprint look the same. ac_upload_text.py
```

### add: absence_evidence (+602)

After:

```
  is non-conformant. The row MUST carry `absence_evidence`: `http_status`, `content_type` as read, `host` and route as asked,
  `body_sha256`, `equals_host_root` (the body equals the host's root page read at the same time), `envelope_class` as a
  field from the gateway's own branches (`no_route`, `no_artifact_at_address`, `no_artifact_named`, `agent_not_found`) plus
  `not_json`, `answered_wrong_document` and `unknown` (withdrawn and never-issued share one envelope), and `at`. A 200
  whose body equals the host's root is `answered_wrong_document`, never `resolved_mismatch`: a locator error with a
  success status.

**Unbound is not a value.**
```

## Cuts (-902 chars)

Each cut removes explanatory or duplicate text and no normative clause; the before and after are verbatim.

### cut C1: Versioning duplicate of the window paragraph (-209)

Before:

```
Append-only, as page 1. A change to this page changes its digest and therefore invalidates the head's
pointer until the head is re-pointed by its own proposal; between the two, readers hold
`resolved_mismatch` and the obligations here are un-run, which is the intended failure, not an outage.



```

After:

```
Append-only, as page 1; a revision opens the window described under `pointer_state`.


```

### cut C2: F3 compound-column gloss (-74)

Before:

```
A compound column would hide the stale-pointer signature (passes the
  mismatch half, fails the clean half). Every failure signature in the table therefore has one owner.
```

After:

```
A compound column would hide the stale-pointer signature; every failure signature has one owner.
```

### cut C3: F3 residue gloss (-117)

Before:

```
it owns exactly its own residue: a
  defect visible only under composite conditions, which is what an isolated `corrupt-mismatches` failure
  with every other row passing means.
```

After:

```
it owns only the residue visible under composite conditions.
```

### cut C4: decay gloss (-86)

Before:

```
both arms decay symmetrically — a red arm not re-run within the decay
window is as stale as a green one, and a checker that reports either arm past the window reports staleness,
not a verdict.
```

After:

```
both arms decay symmetrically: an arm not re-run within the decay window reports staleness, not a verdict.
```

### cut C5: deadline duration (-43)

Before:

```
Deadline *duration* is deliberately unspecified: a policy knob, its own proposal. This clause requires
only that a clock exists and is enforced.
```

After:

```
Deadline duration is unspecified here, its own proposal; this clause requires only an enforced clock.
```

### cut C6: allow-list gloss (-70)

Before:

```
 An allow-list would relocate the judgment call rather than remove it.
```

After:

```
(removed)
```

### cut C7: UI gloss (-93)

Before:

```
 Rendering expiry in a UI while still counting the
row implements the label and not the rule.
```

After:

```
(removed)
```

### cut C8: F2b always-mismatch gloss (-140)

Before:

```
 An always-mismatch comparator passes F2a and F2b for the wrong reason
  and is caught by F1 alone; an always-resolve comparator fails both.
```

After:

```
(removed)
```

### cut C9: canonical-equality gloss (-48)

Before:

```
A delivered page whose digest differs is `resolved_mismatch`
regardless of any canonical equality (NFKC or otherwise): canonical sameness is not byte sameness.
```

After:

```
Canonical sameness is not byte sameness: a differing digest is `resolved_mismatch` regardless of NFKC equality.
```

### cut C10: self-plant parenthetical (-22)

Before:

```
(a value of `self` confers no bits; the demonstration stands only once an
independent defacer's fixture is present)
```

After:

```
(`self` confers no bits; the demonstration stands only with an independent defacer's fixture)
```
