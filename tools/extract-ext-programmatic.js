// The extension's session list passes includeProgrammatic: this.includeProgrammaticSessions.
// Find where that setting comes from and what it defaults to.
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));

for (const rel of ['extension.js', 'webview/index.js', 'package.json']) {
  const p = path.join(ext, rel);
  if (!fs.existsSync(p)) continue;
  const src = fs.readFileSync(p, 'utf8');
  console.log('\n' + '#'.repeat(92));
  console.log('### ' + rel + '  (' + src.length + ' chars)');
  console.log('#'.repeat(92));

  for (const needle of ['includeProgrammaticSessions', 'includeProgrammatic', 'programmatic']) {
    const hits = [];
    let i = -1;
    while ((i = src.indexOf(needle, i + 1)) >= 0) hits.push(i);
    console.log('\n== ' + needle + ' : ' + hits.length + ' hit(s) ==');
    hits.slice(0, 8).forEach((h, n) => {
      console.log('  [' + (n + 1) + '] …' + src.slice(Math.max(0, h - 330), Math.min(src.length, h + 430)).replace(/\s+/g, ' ') + '…');
    });
  }
}
