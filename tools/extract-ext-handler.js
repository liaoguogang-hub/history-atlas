// Locate the extension host's list_sessions_request handler and any filter it applies.
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));
const src = fs.readFileSync(path.join(ext, 'extension.js'), 'utf8');

const needles = [
  'list_sessions_request',
  '"list_sessions"',
  'isPrint', 'printMode', 'isHeadless', 'entryPoint',
  'includePrintSessions', 'print_sessions',
];

for (const needle of needles) {
  const hits = [];
  let i = -1;
  while ((i = src.indexOf(needle, i + 1)) >= 0 && hits.length < 2) hits.push(i);
  console.log('\n' + '='.repeat(88));
  console.log('== ' + needle + '   (' + hits.length + ' shown) ==');
  console.log('='.repeat(88));
  if (!hits.length) { console.log('  (none)'); continue; }
  for (const h of hits) {
    console.log(src.slice(Math.max(0, h - 500), Math.min(src.length, h + 1100)).replace(/\s+/g, ' '));
    console.log('  ' + '-'.repeat(80));
  }
}
