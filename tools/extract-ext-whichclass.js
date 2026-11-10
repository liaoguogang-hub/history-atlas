// Which class owns the session-list building, and therefore which includeProgrammatic value applies?
const fs = require('fs');
const path = require('path');

const extDir = path.join(process.env.USERPROFILE, '.vscode', 'extensions');
const ext = path.join(extDir, fs.readdirSync(extDir).find((d) => d.startsWith('anthropic.claude-code')));
const src = fs.readFileSync(path.join(ext, 'extension.js'), 'utf8');

const marks = [
  'includeProgrammaticSessions=!0',
  'includeProgrammaticSessions=!1',
  'sessionListOptions(){',
  'sessionListLoadTimeoutMs=15000',
  'class f$ extends MX',
  'async buildSessionList(){',
  'async readSessionList(){',
];

const found = marks.map((m) => ({ m, at: src.indexOf(m) }));
found.sort((a, b) => (a.at < 0 ? 1e12 : a.at) - (b.at < 0 ? 1e12 : b.at));
console.log('offset order in extension.js:');
for (const f of found) console.log('  ' + String(f.at).padStart(9) + '  ' + f.m);

// For each class-declaration marker, show the nearest class keyword before it.
console.log('\nnearest enclosing "class" before each includeProgrammaticSessions assignment:');
for (const m of ['includeProgrammaticSessions=!0', 'includeProgrammaticSessions=!1']) {
  const at = src.indexOf(m);
  if (at < 0) { console.log('  ' + m + ' -> not found'); continue; }
  const before = src.slice(Math.max(0, at - 60000), at);
  const idx = before.lastIndexOf('class ');
  console.log('  ' + m + ' @' + at);
  console.log('    nearest class: "' + before.slice(idx, idx + 120).replace(/\s+/g, ' ').split('{')[0] + '"');
}

// Which class contains sessionListOptions?
const sl = src.indexOf('sessionListOptions(){');
const beforeSl = src.slice(Math.max(0, sl - 60000), sl);
const idxSl = beforeSl.lastIndexOf('class ');
console.log('\nsessionListOptions @' + sl);
console.log('  nearest class: "' + beforeSl.slice(idxSl, idxSl + 160).replace(/\s+/g, ' ').split('{')[0] + '"');
