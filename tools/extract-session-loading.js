// What does the extension's "Loading sessions..." actually wait for, and what can hang it?
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));
const src = fs.readFileSync(path.join(ext, 'extension.js'), 'utf8');
const web = fs.readFileSync(path.join(ext, 'webview', 'index.js'), 'utf8');

function show(hay, needle, before, after, max) {
  const hits = [];
  let i = -1;
  while ((i = hay.indexOf(needle, i + 1)) >= 0 && hits.length < (max || 2)) hits.push(i);
  console.log('\n' + '='.repeat(88));
  console.log('== ' + needle + '  (' + hits.length + ' shown) ==');
  console.log('='.repeat(88));
  if (!hits.length) { console.log('  (none)'); return; }
  for (const h of hits) console.log(hay.slice(Math.max(0, h - before), Math.min(hay.length, h + after)).replace(/\s+/g, ' '));
}

console.log('#### extension.js');
show(src, 'sessionListLoadTimeoutMs', 400, 1500, 3);
show(src, 'async readSessionList', 200, 1200, 2);
show(src, 'doListSessions', 300, 1200, 2);
show(src, 'sessionsListEnabled', 400, 400, 1);

console.log('\n\n#### webview/index.js');
show(web, 'Loading sessions', 700, 500, 2);
show(web, 'sessionListError', 400, 700, 3);
show(web, 'list_sessions_request', 400, 700, 2);
