// own_run.mjs <verifier.js path> <variants dir> <out json>: Touchstone's standalone verifier over each bundle. Run AFTER the seal.
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
const [, , vpath, dir, out] = process.argv;
const { verifyDisclosure } = await import(pathToFileURL(vpath).href);
const res = { ran_at: new Date().toISOString(), verifier: vpath.split('/').slice(-2).join('/'), bundles: {} };
for (const f of readdirSync(dir).filter(x => x.endsWith('.json')).sort()) {
  const b = JSON.parse(readFileSync(dir + '/' + f, 'utf8'));
  const r = await verifyDisclosure(b);
  const fails = [], notes = [];
  for (const c of (r.checkpoints || [])) { if (c.ok === false && !c.info) fails.push('checkpoint: ' + c.msg); else if (c.info) notes.push('checkpoint: ' + c.msg); }
  for (const e of (r.entries || [])) for (const c of e.checks) { if (c.ok === false && !c.info) fails.push('seq ' + e.seq + ': ' + c.msg); else if (c.info) notes.push('seq ' + e.seq + ': ' + c.msg); }
  res.bundles[f.replace('.json', '')] = { ok: r.ok, edUnsupported: r.edUnsupported, tier: r.tier, entries: (r.entries || []).length, fails, notes: [...new Set(notes.map(n => n.replace(/^seq \d+: /, '')))].slice(0, 12) };
}
writeFileSync(out, JSON.stringify(res, null, 1));
for (const [k, v] of Object.entries(res.bundles)) console.log(k, v.ok ? 'PASS' : 'FAIL', '| tier', v.tier, '| entries', v.entries, '| fails', v.fails.length, v.edUnsupported ? '| Ed25519 UNSUPPORTED' : '');
