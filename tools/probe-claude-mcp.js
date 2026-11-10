// probe-claude-mcp.js
// Spawns `claude mcp serve` and performs a real MCP stdio handshake, then lists tools.
// This proves whether Chatbox can use Claude Code as a stdio MCP server.
const { spawn } = require('child_process');

const child = spawn('claude.cmd', ['mcp', 'serve'], {
  stdio: ['pipe', 'pipe', 'pipe'],
  shell: true,
});

let buf = '';
let gotInitialize = null;
let gotTools = null;

function send(obj) {
  child.stdin.write(JSON.stringify(obj) + '\n');
}

child.stdout.on('data', (d) => {
  buf += d.toString('utf8');
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id === 1 && msg.result) {
      gotInitialize = msg.result;
      console.log('initialize OK');
      console.log('  serverInfo   : ' + JSON.stringify(msg.result.serverInfo));
      console.log('  protocolVer  : ' + msg.result.protocolVersion);
      console.log('  capabilities : ' + JSON.stringify(msg.result.capabilities));
      send({ jsonrpc: '2.0', method: 'notifications/initialized' });
      send({ jsonrpc: '2.0', id: 2, method: 'tools/list' });
    }
    if (msg.id === 2 && msg.result) {
      gotTools = msg.result.tools || [];
      console.log('');
      console.log('tools/list OK -- ' + gotTools.length + ' tools exposed:');
      gotTools.forEach((t) => console.log('  - ' + t.name));
      console.log('');
      console.log('RESULT: PASS - `claude mcp serve` speaks MCP over stdio.');
      child.kill();
      process.exit(0);
    }
  }
});

child.stderr.on('data', (d) => {
  const s = d.toString('utf8').trim();
  if (s) console.log('[stderr] ' + s.slice(0, 300));
});

child.on('error', (e) => { console.log('SPAWN ERROR: ' + e.message); process.exit(1); });

send({
  jsonrpc: '2.0',
  id: 1,
  method: 'initialize',
  params: {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'dsh-probe', version: '1.0' },
  },
});

setTimeout(() => {
  console.log('');
  console.log('TIMEOUT after 25s');
  console.log('  initialize received : ' + (gotInitialize ? 'yes' : 'no'));
  console.log('  tools received      : ' + (gotTools ? 'yes' : 'no'));
  child.kill();
  process.exit(gotInitialize ? 0 : 1);
}, 25000);
