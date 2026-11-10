// End-to-end test of the live dashboard: open the SSE stream, run a real task through MCP,
// and confirm the steps arrive on the stream while/after the task runs.
const { spawn } = require('node:child_process');

const SERVER = process.argv[2];
const child = spawn('node', [SERVER], { stdio: ['pipe', 'pipe', 'pipe'] });

let stderr = '';
child.stderr.on('data', (d) => { stderr += d.toString(); });

// --- MCP plumbing
let buf = '';
const pending = new Map();
let nextId = 1;
child.stdout.on('data', (d) => {
  buf += d.toString('utf8');
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    let m; try { m = JSON.parse(line); } catch { continue; }
    if (m.id != null && pending.has(m.id)) {
      const p = pending.get(m.id); pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    }
  }
});
const rpc = (method, params) => new Promise((res, rej) => {
  const id = nextId++;
  const t = setTimeout(() => rej(new Error('timeout ' + method)), 240000);
  pending.set(id, { resolve: (v) => { clearTimeout(t); res(v); }, reject: (e) => { clearTimeout(t); rej(e); } });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
});
const txt = (r) => (!r || !r.content) ? '' : r.content.map((c) => c.text || '').join('\n');

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  await sleep(3500);
  const m = stderr.match(/dashboard: (http:\/\/[^\s]+)/);
  if (!m) { console.log('  FAIL: no dashboard URL'); console.log(stderr); process.exit(1); }
  const url = m[1];
  const base = url.replace(/\/\?k=.*$/, '');
  const token = (url.match(/\?k=([0-9a-f]+)/) || [])[1];
  console.log('  dashboard : ' + base + '   (token ' + String(token).slice(0, 8) + '...)');

  // --- SSE
  const received = [];
  let sseOk = false;
  try {
    const res = await fetch(base + '/events?k=' + token);
    sseOk = res.status === 200 && (res.headers.get('content-type') || '').includes('text/event-stream');
    console.log('  SSE       : HTTP ' + res.status + '  content-type=' + res.headers.get('content-type'));
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    (async () => {
      let b = '';
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        b += dec.decode(value, { stream: true });
        let i;
        while ((i = b.indexOf('\n\n')) >= 0) {
          const frame = b.slice(0, i); b = b.slice(i + 2);
          const data = frame.split('\n').filter((l) => l.startsWith('data: ')).map((l) => l.slice(6)).join('');
          if (data) { try { received.push(JSON.parse(data)); } catch {} }
        }
      }
    })().catch(() => {});
  } catch (e) {
    console.log('  SSE       : FAIL ' + e.message);
  }

  const state = await (await fetch(base + '/state?k=' + token)).json();
  console.log('  /state    : events=' + state.events + ' clients=' + state.clients);

  // --- a real task that must use tools
  console.log('\n  running a tool-using task via MCP...');
  await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {} });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');
  const r = await rpc('tools/call', {
    name: 'claude_code',
    arguments: {
      prompt: 'Read the file D:\\work\\print_ok.py with the Read tool, then run it with Bash using forward slashes: python D:/work/print_ok.py',
      cwd: 'D:\\work',
    },
  });
  console.log('  task      : ' + (txt(r).match(/STATUS: (\w+)/) || [])[1]);

  await sleep(1500);
  const kinds = {};
  for (const e of received) kinds[e.event] = (kinds[e.event] || 0) + 1;
  const state2 = await (await fetch(base + '/state?k=' + token)).json();

  console.log('\n  --- events received over SSE ---');
  for (const [k, v] of Object.entries(kinds)) console.log('    ' + k.padEnd(18) + v);
  console.log('  total over SSE   : ' + received.length);
  console.log('  /state ring size : ' + state2.events);

  const need = ['job_start', 'session_started', 'tool_use', 'tool_result', 'job_finish'];
  const missing = need.filter((n) => !kinds[n]);
  console.log('');
  if (sseOk && missing.length === 0) {
    console.log('  RESULT: PASS - live push works; saw ' + need.join(', '));
  } else {
    console.log('  RESULT: FAIL - sseOk=' + sseOk + ' missing=' + missing.join(','));
  }
  child.kill();
  process.exit(missing.length === 0 && sseOk ? 0 : 1);
})();
