// Extract the extension's session-listing logic from its minified bundle.
const fs = require('fs');
const path = require('path');

const ext = path.join(process.env.USERPROFILE, '.vscode', 'extensions',
  fs.readdirSync(path.join(process.env.USERPROFILE, '.vscode', 'extensions'))
    .find((d) => d.startsWith('anthropic.claude-code')));
const file = path.join(ext, 'extension.js');
const src = fs.readFileSync(file, 'utf8');
console.log('  extension.js length: ' + src.length);

function around(needle, before, after, max) {
  const out = [];
  let i = -1;
  while ((i = src.indexOf(needle, i + 1)) >= 0 && out.length < (max || 3)) {
    out.push(src.slice(Math.max(0, i - before), Math.min(src.length, i + after)));
  }
  return out;
}

const shows = [
  ['listSessions', 200, 700, 3],
  ['.claude/projects', 300, 600, 1],
  ['isSidechain', 120, 320, 2],
];

for (const [needle, before, after, max] of shows) {
  console.log('\n' + '='.repeat(90));
  console.log('=== ' + needle + ' ===');
  console.log('='.repeat(90));
  const chunks = around(needle, before, after, max);
  if (!chunks.length) console.log('  (no hits)');
  chunks.forEach((c, n) => {
    console.log('\n--- hit ' + (n + 1) + ' ---');
    console.log(c.replace(/\\n/g, '\n  ').replace(/\s{3,}/g, ' '));
  });
}
