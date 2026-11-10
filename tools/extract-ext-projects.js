// Find every mention of 'projects' / session enumeration in the extension's own bundle,
// to see whether it filters out `claude -p` sessions.
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));

for (const rel of ['extension.js', 'webview/index.js']) {
  const src = fs.readFileSync(path.join(ext, rel), 'utf8');
  console.log('\n' + '#'.repeat(90));
  console.log('### ' + rel + '   (' + src.length + ' chars)');
  console.log('#'.repeat(90));

  for (const needle of ['projects', 'readdir', 'Session history', 'session_list', 'listSessions(']) {
    let i = -1, n = 0;
    console.log('\n== ' + needle + ' ==');
    while ((i = src.indexOf(needle, i + 1)) >= 0 && n < 4) {
      n++;
      let chunk = src.slice(Math.max(0, i - 220), Math.min(src.length, i + 380));
      chunk = chunk.replace(/\s+/g, ' ');
      console.log('  [' + n + '] …' + chunk + '…');
      console.log('');
    }
    if (!n) console.log('  (none)');
  }
}
