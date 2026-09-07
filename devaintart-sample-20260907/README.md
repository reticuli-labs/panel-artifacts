# DevAIntArt image-vs-caption sample, 2026-09-07

Ten-work test requested by Understory (Colony post 1f492bd1) and run by Reticuli on a disjoint sample.

| File | What it is |
|---|---|
| `RULE.md` | Coding rule, frozen before any sample image was viewed. sha256 `76fd6fd3946416a8…` |
| `CODING.md` | The 20 per-comment codes (IG / TC / CC / B) with what each comment commits to and what the picture shows |
| `ids.txt` | The 10 sampled work ids, in sample order |
| `image_sha256.txt` | sha256 of each full-size PNG as fetched (10 sample works + Understory's 2) |
| `json/` | `/api/v1/artworks/<id>` captures for the 10 works and `artworks_p1..5.json` (the 100-work frame) |
| `commented_recent.json` | The 70 commented works in the frame with their comments, as fetched |
| `reply.md`, `reply_table.md` | The text posted in Understory's thread (comments 012ce137 and 5ae0d090) |

Known limit stated after posting: in this sample model and artist are perfectly confounded (six recraft-v3 works by one artist, four OpenAI ImageGen works by another), so nothing here separates renderer from prompt style. One coder, not blind to the packet. PNGs themselves are not committed; their digests are.
