// Test for fold_verify.html: runs the page's own inline script under node and holds it to fold_check.py's outputs.
//   node fold_verify_test.mjs                 exit 0 = every check passed, 1 = a failure (named)
//   FOLD_EXTRA_TEXT=FILE FOLD_EXTRA_ROOT=HEX node fold_verify_test.mjs   also folds one more file against one more root
// What it checks: (1) the page loads nothing external; (2) the inline script's built-in vectors pass under the script itself;
// (3) those vectors and the fold_vectors_*.json beside this file (fold_check.py's stdout, parsed) agree byte for byte;
// (4) the five frozen texts fold to META.json's backward roots, forward counterfactuals, header bytes and text sha256;
// (5) the FILED_ROOTS the page offers equal META.json and the external root in the vectors file;
// (6) mutations fail: one flipped byte, a CRLF copy, the forward root offered as expected, a 63-character root.
import fs from "node:fs";
import path from "node:path";
import { webcrypto } from "node:crypto";

const here = path.dirname(new URL(import.meta.url).pathname);
const html = fs.readFileSync(path.join(here, "fold_verify.html"), "utf8");
let failures = 0;
const check = (ok, what) => { console.log((ok ? "ok   " : "FAIL ") + what); if (!ok) failures++; };

// (1) nothing external
const scripts = html.match(/<script\b[^>]*>/g) || [];
check(scripts.length === 1 && !/src=/.test(scripts[0]), "exactly one inline script, no src");
check(!/<link\b/i.test(html) && !/@import/.test(html) && !/url\(/.test(html), "no stylesheet link, no @import, no url()");
check(!/\b(fetch|XMLHttpRequest|WebSocket|importScripts)\s*\(/.test(html), "no fetch, XMLHttpRequest, WebSocket or importScripts call");

// run the inline script in this realm with no document, so the DOM wiring is skipped and module.exports carries the core
const src = html.match(/<script>([\s\S]*?)<\/script>/)[1];
const core = new Function("module", "crypto", "TextEncoder", src + "\nreturn module.exports;")({ exports: {} }, webcrypto, TextEncoder);
const R = core.FILED_RECIPE;
const enc = s => new TextEncoder().encode(s);
const hexToBytes = core.hexToBytes;

// (2) built-in vectors under the script itself
const st = await core.runSelfTest(R);
check(st.passed === st.total && st.total === 7, "built-in self-test " + st.passed + " of " + st.total);
for (const r of st.rows) if (!r.pass) console.log("   vector failed:", r.name, r.got.header_hex, r.got.backward_root, r.got.forward_root);

// (3) the Python tool's vectors file
const vecFile = fs.readdirSync(here).filter(f => /^fold_vectors_\d{4}-\d{2}-\d{2}\.json$/.test(f)).sort().pop();
check(!!vecFile, "vectors file present: " + vecFile);
const V = JSON.parse(fs.readFileSync(path.join(here, vecFile), "utf8"));
check(V.vectors.length === core.SELFTEST.length, "vector count equals the page's built-in count (" + V.vectors.length + ")");
for (let i = 0; i < V.vectors.length; i++) {
  const v = V.vectors[i]; const s = core.SELFTEST[i];
  const raw = hexToBytes(v.bytes_hex);
  const d = await core.describe(raw, R);
  const sameAsPy = d.header_hex === v.header_hex && d.backward_root === v.backward_root && d.forward_root === v.forward_root && d.sha256_raw === v.sha256_raw && d.frame_bytes === v.frame_bytes && d.chunk_count === v.chunks;
  check(sameAsPy, "python vector " + i + " reproduced by the page script: " + v.name);
  const sameEmbedded = s && s.name === v.name && Buffer.from(enc(s.text)).equals(Buffer.from(raw)) && s.header_hex === v.header_hex && s.backward === v.backward_root && s.forward === v.forward_root;
  check(sameEmbedded, "page's built-in vector " + i + " is byte-identical to the python vector and carries its roots");
}

// (4) the five frozen texts against META.json
const META = JSON.parse(fs.readFileSync(path.join(here, "META.json"), "utf8"));
const FR = META.frame_recipe;
check(FR.magic_descriptor_hex === R.magic_descriptor_hex && FR.chunk_bytes === R.chunk_bytes && FR.link_seed_hex === R.link_seed_hex && FR.fold_direction === R.fold_direction && FR.header_bytes === R.header_bytes && FR.link === R.link, "page's typed recipe equals META.json frame_recipe");
const FILES = { page1_v11: "page1_v11_served.md", page3_v3: "page3_v3.md", page3_v4: "page3_v4_draft.md", page1_repoint_to_v3: "page1_repoint_to_v3.md", page1_repoint_to_v4: "page1_repoint_to_v4.md" };
const sha256hex = async u8 => core.bytesToHex(new Uint8Array(await webcrypto.subtle.digest("SHA-256", u8)));
for (const [k, f] of Object.entries(FILES)) {
  const raw = new Uint8Array(fs.readFileSync(path.join(here, f)));
  const d = await core.verify(raw, FR.backward_fold_gives[k], R);
  const meta = META[k] || {};
  const ok = d.verdict === "match" && d.forward_root === FR.forward_fold_counterfactual_not_a_root[k] && (!FR.header_hex[k] || d.header_hex === FR.header_hex[k]) && (!meta.sha256_text || (await sha256hex(raw)) === meta.sha256_text) && (!meta.fingerprint_if_filed || d.backward_root === meta.fingerprint_if_filed);
  check(ok, "frozen text " + k + " (" + f + "): backward root, forward counterfactual, header and sha256 match META.json");
}

// (5) the roots the page offers
for (const r of core.FILED_ROOTS) {
  if (r.key === "page2_v2_section9") check(r.root === V.external_roots.page2_v2_section9.root, "offered root page2_v2_section9 equals the vectors file's external root");
  else check(r.root === FR.backward_fold_gives[r.key], "offered root " + r.key + " equals META.json backward_fold_gives");
}
check(core.FILED_ROOTS.length === Object.keys(FILES).length + 1, "the page offers the five frozen roots plus one external root");

// (6) mutations must fail
{
  const raw = new Uint8Array(fs.readFileSync(path.join(here, FILES.page3_v3)));
  const flipped = new Uint8Array(raw); flipped[Math.floor(flipped.length / 2)] ^= 0x01;
  const d1 = await core.verify(flipped, FR.backward_fold_gives.page3_v3, R);
  check(d1.verdict === "mismatch" && !d1.wrong_direction, "one flipped byte in page3_v3 reads MISMATCH");
  const crlf = enc(Buffer.from(raw).toString("utf8").replace(/\n/g, "\r\n"));
  const d2 = await core.verify(crlf, FR.backward_fold_gives.page3_v3, R);
  check(d2.verdict === "mismatch" && d2.cr_count > 0, "a CRLF copy of page3_v3 reads MISMATCH with CR bytes counted (" + d2.cr_count + ")");
  const d3 = await core.verify(raw, FR.forward_fold_counterfactual_not_a_root.page3_v3, R);
  check(d3.verdict === "mismatch" && d3.wrong_direction === true, "the forward counterfactual offered as the expected root reads MISMATCH and is named as the wrong direction");
  const d4 = await core.verify(raw, FR.backward_fold_gives.page3_v3.slice(0, 63), R);
  check(d4.verdict === "no_root", "a 63-character root gives no verdict");
  const d5 = await core.verify(raw, FR.backward_fold_gives.page3_v3.toUpperCase(), R);
  check(d5.verdict === "match", "an upper-case copy of the root still matches");
  const d6 = await core.verify(raw, FR.backward_fold_gives.page3_v3, { ...R, chunk_bytes: 2999 });
  check(d6.verdict === "mismatch", "an edited chunk size reads MISMATCH");
}

// optional: one more file against one more root
if (process.env.FOLD_EXTRA_TEXT && process.env.FOLD_EXTRA_ROOT) {
  const raw = new Uint8Array(fs.readFileSync(process.env.FOLD_EXTRA_TEXT));
  const d = await core.verify(raw, process.env.FOLD_EXTRA_ROOT, R);
  check(d.verdict === "match", "extra file " + path.basename(process.env.FOLD_EXTRA_TEXT) + " (" + raw.length + " bytes, " + d.chunk_count + " chunks) folds to " + process.env.FOLD_EXTRA_ROOT.slice(0, 8));
}

console.log(failures === 0 ? "ALL CHECKS PASSED" : failures + " CHECK(S) FAILED");
process.exit(failures === 0 ? 0 : 1);
