// Probe: does claude_code_log capture real tool_use / tool_result steps?
// Drives the bridge over MCP stdio, runs a task that MUST use a tool, then prints the log.
const { spawn } = require('node:child_process');
const path = require('node:path');

const SERVER = path.join(process.env.USERPROFILE, '.mcp-servers', 'claude-code-bridge', 'server.js');
const child = spawn(process.execPath, [SERVER], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env, CCB_WAIT_MS: '45000', CCB_MAX_WAIT_MS: '50000' },
});

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
    let m;
    try { m = JSON.parse(line); } catch { continue; }
    if (m.id != null && pending.has(m.id)) {
      const p = pending.get(m.id);
      pending.delete(m.id);
      m.error ? p.reject(new Error(m.error.message)) : p.resolve(m.result);
    }
  }
});
child.stderr.on('data', () => {});

const rpc = (method, params) => new Promise((res, rej) => {
  const id = nextId++;
  const t = setTimeout(() => rej(new Error('timeout ' + method)), 300000);
  pending.set(id, { resolve: (v) => { clearTimeout(t); res(v); }, reject: (e) => { clearTimeout(t); rej(e); } });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
});
const txt = (r) => (!r || !r.content) ? '(none)' : r.content.map((c) => c.text || '').join('\n');

(async () => {
  await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {} });
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

  console.log('=== run a task that must use a tool ===');
  const r = await rpc('tools/call', {
    name: 'claude_code',
    arguments: {
      prompt: 'Read the file D:\\work\\print_ok.py with the Read tool, then run it with the Bash tool ' +
              'using `python D:\\work\\print_ok.py`, and tell me exactly what it printed.',
      cwd: 'D:\\work',
    },
  });
  console.log(txt(r).split('\n').slice(0, 6).map((l) => '  ' + l).join('\n'));

  const jobs = JSON.parse(txt(await rpc('tools/call', { name: 'claude_code_jobs', arguments: { limit: 1 } })));
  const jobId = jobs[0].job_id;

  console.log('\n=== claude_code_log for job ' + jobId + ' ===');
  const log = txt(await rpc('tools/call', { name: 'claude_code_log', arguments: { job_id: jobId } }));
  console.log(log.split('\n').map((l) => '  ' + l).join('\n'));

  const toolUses = (log.match(/\[tool \]/g) || []).length;
  const toolResults = (log.match(/\[ {2}ok \]|\[FAIL \]/g) || []).length;
  console.log('\n=== verdict ===');
  console.log('  tool_use steps   : ' + toolUses);
  console.log('  tool_result steps: ' + toolResults);
  console.log(toolUses > 0 && toolResults > 0 ? '  RESULT: PASS - tool-level narration is captured' : '  RESULT: FAIL - no tool steps recorded');

  child.kill();
  process.exit(toolUses > 0 && toolResults > 0 ? 0 : 1);
})();
