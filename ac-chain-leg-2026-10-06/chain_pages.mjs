// Chain-side page state for Artifact Council artifacts, read over a Solana RPC with the MIT relay SDK (account reads only; no
// transaction history, no relay, no gateway). Run from the relay package directory: node chain_pages.mjs <rpc-url> <artifact>...
import { RpcTransport } from './sdk/transport.mjs';
import { Council } from './sdk/index.mjs';
const [rpc, ...artifacts] = process.argv.slice(2);
const t = new RpcTransport(rpc);
const c = new Council({ transport: t, program: '77wHqALWwA7UTJqd7hFAsFbaPy2MAyiNUdrqhqkecKh1' });
const out = { rpc, program: c.program.toBase58(), read_at: new Date().toISOString(), artifacts: {} };
for (const a of artifacts) {
  const art = await c.artifact(a);
  const records = await c.records(a);
  const pages = await c.pages(a, { text: false, records });
  out.artifacts[a] = {
    head: Buffer.from(art.head).toString('hex'), history: art.history, versions: art.versions, members: art.members?.length ?? art.members,
    records: records.length,
    pages: pages.map(p => ({ page: p.page, version: p.version, content: Buffer.from(p.content).toString('hex'), len: p.len, record: p.record, upload: typeof p.upload === 'string' ? p.upload : p.upload?.toBase58?.() ?? String(p.upload) })),
  };
  console.error(`${a.slice(0, 12)} history ${art.history} records ${records.length} pages ${pages.map(p => `${p.page}.v${p.version}`).join(' ')}`);
}
console.log(JSON.stringify(out, null, 1));
