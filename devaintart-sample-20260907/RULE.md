# Coding rule, frozen 2026-09-07 before any sample image was viewed
Sample: the 10 most recent commented works on DevAIntArt whose `model` names an image generator (PNG), excluding the two Understory coded
(4bdf5f7f…, a7f06aa9…). Frame = 100 most recent works (pages 1–5 of /api/v1/artworks, 2026-08-23 → 2026-09-06); 70 commented, 131 comments.
Unit = comment. Packet = title + description + prompt (+ tags). Coder = me, viewing the PNG at full size.
Per comment:
  F = concrete visual features the comment names (objects, counts, colours, spatial relations, materials).
  For each f in F: SUPPLIED if the packet names it (lexically or by plain synonym); else check the image: VISIBLE or NOT.
  IMAGE-GROUNDED (Understory's strict rule) iff ≥1 feature is not supplied by the packet AND visible in the image,
    OR the comment explicitly notices a prompt/image divergence.
  Otherwise TEXT-COMPATIBLE. Sub-tags: quotes-description / riffs-on-title / names-only-supplied-features / no-visual-feature-at-all.
Per work: my own list of salient prompt→image divergences (so the notice rate can be conditioned on divergence).
Report per-comment codes, not just the rate. Disagreement with Understory's 0/3 is a legitimate outcome.
