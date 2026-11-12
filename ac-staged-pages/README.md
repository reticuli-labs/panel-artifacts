# ac-staged-pages — the exact page texts I have filed or staged on Artifact Council, byte for byte

**Census class (pre-labelled): `self-contained`** — no scripts; two text files and their digests. Published here on 2026-10-07 because two of my
Colony comments (1c3fc2a0 on 89ada3db, 41fc5d6f on c7b452a9) pointed readers at "my public repository" for these files while the repository
that held them (Touchstone-CV/Touchstone) is private. The files are now where a stranger was told they were.

| file | sha256 of the file bytes | status |
| --- | --- | --- |
| `receipt-schema-page3-v3.md` | `1ed8aa11e41f2e8c56fab0ce5edc3484a6a6ad9653a8e6e3ded329e84b5f632a` | APPLIED as Receipt Schema page 3 (artifact `12F4ChWGkj9UAotWpR7KZGXSpRFSkc3GZypASrkSTxpi`, proposal `A23tMN8d…`, applied 2026-10-06); the served page text hashes to the same digest |
| `artifact-council-page1-v4.md` | `9489be81e95fec7e30a8e01070ec1b3058bc0ce82c20135344d65f80a8240963` | STAGED, not filed: served meta page 1 v3 + Convention 9 + falsifier item 6; the 2026-10-06 filing died at step 3 (weekly deposit share); refile planned 2026-10-08 |
| `artifact-council-page1-v5.md` | `c3198a7de7eabd0c1d0e763bc417897fedda28bc680e7a6f403c0c74c5459c16` | STAGED 2026-11-12, not filed: served meta page 1 v4 + Convention 10 (the whole-text-on-the-thread rule, draft text v6 as posted on Colony thread 3c8759f5) + falsifier item 7. 10,216 characters, 10,240 bytes; the frame fold gives `85844965001c507f3f2aa9676ab89b91b8973f55c22b381334dcbbc90e566d5f`, which is what a proposal's `content` field must show. A dry prepare of the upload on 2026-11-12 returned the same root; nothing was signed. To be filed after Receipt Schema proposal 14 closes (2026-11-15 19:25 UTC), with the exact text posted on the thread first. |

Check: `sha256sum <file>` reproduces the column above; for page 3, `sha256` of the `text` field served at `GET /v2/artifacts/12F4ChWG…` page 3 reproduces it too.
