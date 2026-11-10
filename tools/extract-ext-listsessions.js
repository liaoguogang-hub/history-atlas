// Show every listSessions occurrence in the extension host, wide enough to find the method body.
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));
const src = fs.readFileSync(path.join(ext, 'extension.js'), 'utf8');

const hits = [];
let i = -1;
while ((i = src.indexOf('listSessions', i + 1)) >= 0) hits.push(i);
console.log('total listSessions occurrences: ' + hits.length);

hits.forEach((h, n) => {
  console.log('\n' + '='.repeat(90));
  console.log('--- occurrence ' + (n + 1) + ' at offset ' + h + ' ---');
  console.log(src.slice(Math.max(0, h - 350), Math.min(src.length, h + 1400)).replace(/\s+/g, ' '));
});

// Also: how does the host enumerate the projects dir for the list?
console.log('\n\n' + '#'.repeat(90));
console.log('### looking for the projects-dir reader used by the sidebar list');
console.log('#'.repeat(90));
for (const needle of ['readdirSync(rx()', 'nU1()', 'listProjectSessions', 'sessionsInProject', 'buildSessionList']) {
  const at = src.indexOf(needle);
  console.log('\n== ' + needle + ' == ' + (at < 0 ? '(none)' : ''));
  if (at >= 0) console.log(src.slice(Math.max(0, at - 500), Math.min(src.length, at + 1500)).replace(/\s+/g, ' '));
}
