// add-mcp-server-to-chatbox.js
// Generic helper: register (or update) an MCP server in Chatbox's config.json.
//
//   node add-mcp-server-to-chatbox.js --name "X" --command "C:\path\to.exe" [--args "a,b"] [--dry-run]
//
// Schema source (Chatbox repo, src/shared/types/mcp.ts):
//   MCPServerConfig { id, name, enabled, protocolMode?, transport }
//   transport: { type:'stdio', command, args, env? } | { type:'http', url, headers? }
//   stored at settings.mcp.servers[]
//
// Windows note: Chatbox uses @modelcontextprotocol/sdk StdioClientTransport, which spawns the
// command WITHOUT a shell. A `.cmd` shim therefore fails with ENOENT; always give a real .exe.
//
// Run only while Chatbox is CLOSED.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function arg(flag, def) {
  const i = process.argv.indexOf(flag);
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : def;
}
const NAME = arg('--name');
const COMMAND = arg('--command');
const ARGS = (arg('--args', '') || '').split(',').map((s) => s.trim()).filter(Boolean);
const DRY = process.argv.includes('--dry-run');

const CONFIG = path.join(process.env.APPDATA, 'xyz.chatboxapp.app', 'config.json');

if (!NAME || !COMMAND) {
  console.error('usage: node add-mcp-server-to-chatbox.js --name <name> --command <exe> [--args "a,b"] [--dry-run]');
  process.exit(2);
}
if (!fs.existsSync(COMMAND)) {
  console.error('FATAL: command does not exist: ' + COMMAND);
  process.exit(1);
}
const running = require('node:child_process')
  .execSync('tasklist /FI "IMAGENAME eq Chatbox.exe" /NH', { encoding: 'utf8' });
if (/Chatbox\.exe/i.test(running)) {
  console.error('FATAL: Chatbox is running. Close it first, or it will overwrite this change on exit.');
  process.exit(1);
}

const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
cfg.settings = cfg.settings || {};
cfg.settings.mcp = cfg.settings.mcp || { servers: [], enabledBuiltinServers: [] };
cfg.settings.mcp.servers = cfg.settings.mcp.servers || [];

const entry = {
  id: crypto.randomUUID(),
  name: NAME,
  enabled: true,
  protocolMode: 'auto',
  transport: { type: 'stdio', command: COMMAND, args: ARGS },
};

const idx = cfg.settings.mcp.servers.findIndex((s) => s.name === NAME);
const existed = idx >= 0;
if (existed) {
  entry.id = cfg.settings.mcp.servers[idx].id || entry.id;
  cfg.settings.mcp.servers[idx] = entry;
} else {
  cfg.settings.mcp.servers.push(entry);
}

if (!DRY) fs.writeFileSync(CONFIG, JSON.stringify(cfg, null, 2), 'utf8');

console.log((DRY ? '[dry-run] ' : '') + (existed ? 'updated' : 'added') + ' MCP server');
console.log('  config   : ' + CONFIG);
console.log('  name     : ' + entry.name);
console.log('  id       : ' + entry.id);
console.log('  command  : ' + entry.transport.command);
console.log('  args     : ' + JSON.stringify(entry.transport.args));
console.log('  servers  : [' + cfg.settings.mcp.servers.map((s) => s.name).join(', ') + ']');
if (!DRY) {
  const check = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
  console.log('  verified : providers=[' + Object.keys(check.settings.providers).join(', ') +
              ']  mcpServers=' + check.settings.mcp.servers.length +
              '  configVersion=' + check.configVersion);
}
