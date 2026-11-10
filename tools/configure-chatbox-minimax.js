// configure-chatbox-minimax.js
// Adds a BYOK "MiniMax CN" provider to Chatbox's config.json and makes MiniMax-M3 the
// default chat model.  Run only while Chatbox is CLOSED, or the app will overwrite this.
//
// Provider definition source (Chatbox repo):
//   src/shared/providers/definitions/minimax.ts
//     MINIMAX_CN_API_HOST = 'https://api.minimaxi.com/v1'
//     ModelProviderEnum.MiniMaxCN = 'minimax-cn'
//   packages/chatbox-core/src/domain/settings/settings-schema.ts
//     ProviderSettingsSchema { apiKey, apiHost, apiPath, models, excludedModels, useProxy,
//                              oauth, activeAuthMode, ... }
//     ProviderModelInfoSchema { modelId, apiStyle, nickname, labels, capabilities,
//                               contextWindow, maxOutput }
//     SettingsSchema { providers: record<string, ProviderSettings>, defaultChatModel: {provider, model} }

const fs = require('fs');
const path = require('path');

const CONFIG = path.join(process.env.APPDATA, 'xyz.chatboxapp.app', 'config.json');
const CLAUDE_SETTINGS = path.join(process.env.USERPROFILE, '.claude', 'settings.json');
const PROVIDER_ID = 'minimax-cn';
const DEFAULT_MODEL = 'MiniMax-M3';

// ---------------------------------------------------------------- read the API key
const claude = JSON.parse(fs.readFileSync(CLAUDE_SETTINGS, 'utf8'));
const apiKey = claude?.env?.ANTHROPIC_AUTH_TOKEN;
if (!apiKey || typeof apiKey !== 'string') {
  console.error('FATAL: no ANTHROPIC_AUTH_TOKEN in ' + CLAUDE_SETTINGS);
  process.exit(1);
}

// ---------------------------------------------------------------- models
// Only models whose capabilities Chatbox itself declares are listed, so Chatbox never
// sends an image to a model that cannot take one.  (The live /v1/models endpoint also
// advertises MiniMax-M2.1, -M2.1-highspeed and -M2; add those from the GUI if wanted.)
const models = [
  { modelId: 'MiniMax-M3', capabilities: ['vision', 'reasoning', 'tool_use'], contextWindow: 1000000 },
  { modelId: 'MiniMax-M2.7', capabilities: ['reasoning', 'tool_use'], contextWindow: 204800 },
  { modelId: 'MiniMax-M2.7-highspeed', capabilities: ['reasoning', 'tool_use'], contextWindow: 204800 },
  { modelId: 'MiniMax-M2.5', capabilities: ['reasoning', 'tool_use'], contextWindow: 204800 },
  { modelId: 'MiniMax-M2.5-highspeed', capabilities: ['reasoning', 'tool_use'], contextWindow: 204800 },
];

// ---------------------------------------------------------------- patch config
const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
cfg.settings = cfg.settings || {};
cfg.settings.providers = cfg.settings.providers || {};

const before = Object.keys(cfg.settings.providers);
cfg.settings.providers[PROVIDER_ID] = {
  apiKey,
  apiHost: 'https://api.minimaxi.com/v1',
  activeAuthMode: 'apikey',
  useProxy: false,
  models,
};

const prevDefault = cfg.settings.defaultChatModel;
cfg.settings.defaultChatModel = { provider: PROVIDER_ID, model: DEFAULT_MODEL };

fs.writeFileSync(CONFIG, JSON.stringify(cfg, null, 2), 'utf8');

// ---------------------------------------------------------------- report
const check = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
const p = check.settings.providers[PROVIDER_ID];
const mask = (s) => (s ? s.slice(0, 6) + '...' + s.slice(-4) + ' (len ' + s.length + ')' : '<none>');

console.log('config        : ' + CONFIG);
console.log('providers before : [' + before.join(', ') + ']');
console.log('providers after  : [' + Object.keys(check.settings.providers).join(', ') + ']');
console.log('');
console.log('provider id   : ' + PROVIDER_ID);
console.log('  name        : MiniMax CN');
console.log('  apiHost     : ' + p.apiHost);
console.log('  apiKey      : ' + mask(p.apiKey));
console.log('  authMode    : ' + p.activeAuthMode);
console.log('  useProxy    : ' + p.useProxy);
console.log('  models      : ' + p.models.length);
p.models.forEach((m) => {
  console.log('      - ' + m.modelId.padEnd(22) + ' ctx=' + m.contextWindow + '  caps=' + m.capabilities.join('+'));
});
console.log('');
console.log('defaultChatModel : ' + JSON.stringify(prevDefault) + '  ->  ' + JSON.stringify(check.settings.defaultChatModel));
console.log('');
console.log('configVersion preserved : ' + check.configVersion + ' (was ' + cfg.configVersion + ')');
console.log('all top-level keys      : ' + Object.keys(check).join(', '));
console.log('settings keys kept      : ' + Object.keys(check.settings).length + ' keys');
console.log('OK');
