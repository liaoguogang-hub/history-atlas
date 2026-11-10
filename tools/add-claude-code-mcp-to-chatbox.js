// add-claude-code-mcp-to-chatbox.js
// Registers Claude Code as a stdio MCP server inside Chatbox, so Chatbox Work Mode can call
// Claude Code's 26 tools (Bash, Read, Write, Edit, Grep, Glob, WebSearch, Agent, Workflow, ...).
//
// Schema source (Chatbox repo):
//   src/shared/types/mcp.ts
//     MCPServerConfig { id, name, enabled, protocolMode?, transport }
//     transport: { type:'stdio', command, args, env? } | { type:'http', url, headers? }
//   settings.mcp.servers is the registry array.
//
// Windows note: Chatbox uses @modelcontextprotocol/sdk StdioClientTransport, which spawns the
// command WITHOUT a shell. `claude` on Windows is a .cmd shim and would fail with ENOENT, so the
// full path to the real claude.exe is used.
//
// Run only while Chatbox is CLOSED.

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const CONFIG = path.join(process.env.APPDATA, 'xyz.chatboxapp.app', 'config.json');
const CLAUDE_EXE = path.join(process.env.APPDATA, 'npm', 'node_modules', '@anthropic-ai', 'claude-code', 'bin', 'claude.exe');
const SERVER_NAME = 'Claude Code';

if (!fs.existsSync(CLAUDE_EXE)) {
  console.error('FATAL: claude.exe not found at ' + CLAUDE_EXE);
  process.exit(1);
}

const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
cfg.settings = cfg.settings || {};
cfg.settings.mcp = cfg.settings.mcp || { servers: [], enabledBuiltinServers: [] };
cfg.settings.mcp.servers = cfg.settings.mcp.servers || [];
cfg.settings.mcp.enabledBuiltinServers = cfg.settings.mcp.enabledBuiltinServers || [];

const before = cfg.settings.mcp.servers.map((s) => s.name);

const entry = {
  id: crypto.randomUUID(),
  name: SERVER_NAME,
  enabled: true,
  protocolMode: 'auto',
  transport: {
    type: 'stdio',
    command: CLAUDE_EXE,
    args: ['mcp', 'serve'],
  },
};

const idx = cfg.settings.mcp.servers.findIndex((s) => s.name === SERVER_NAME);
if (idx >= 0) {
  entry.id = cfg.settings.mcp.servers[idx].id || entry.id; // keep the existing id
  cfg.settings.mcp.servers[idx] = entry;
  console.log('updated existing entry');
} else {
  cfg.settings.mcp.servers.push(entry);
  console.log('added new entry');
}

fs.writeFileSync(CONFIG, JSON.stringify(cfg, null, 2), 'utf8');

const check = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
console.log('');
console.log('config          : ' + CONFIG);
console.log('mcp.servers before : [' + before.join(', ') + ']');
console.log('mcp.servers after  : [' + check.settings.mcp.servers.map((s) => s.name).join(', ') + ']');
console.log('');
const s = check.settings.mcp.servers.find((x) => x.name === SERVER_NAME);
console.log('name        : ' + s.name);
console.log('id          : ' + s.id);
console.log('enabled     : ' + s.enabled);
console.log('transport   : ' + s.transport.type);
console.log('command     : ' + s.transport.command);
console.log('args        : ' + JSON.stringify(s.transport.args));
console.log('');
console.log('other settings preserved: configVersion=' + check.configVersion +
            '  providers=[' + Object.keys(check.settings.providers).join(', ') + ']' +
            '  settingsKeys=' + Object.keys(check.settings).length);
console.log('OK');
