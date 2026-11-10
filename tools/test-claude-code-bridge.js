// test-claude-code-bridge.js
// Drives the bridge over real MCP stdio JSON-RPC.
//   node test-claude-code-bridge.js            protocol + one real task (sync or poll)
//   node test-claude-code-bridge.js slow       also long task + session continuity
//
// CCB_WAIT_MS controls which path the first call takes:
//   45000 (default) -> task finishes inside the call   (synchronous path)
//   3000            -> task overruns -> JOB_ID + poll  (polling path)

const { spawn } = require('node:child_process');
const path = require('node:path');

const SERVER = path.join(process.env.USERPROFILE, '.mcp-servers', 'claude-code-bridge', 'server.js');
const RUN_SLOW = process.argv.includes('slow');
const WAIT = process.env.CCB_WAIT_MS || '45000';

const child = spawn(process.execPath, [SERVER], {
  stdio: ['pipe', 'pipe', 'pipe'],
  env: { ...process.env, CCB_WAIT_MS: WAIT, CCB_MAX_WAIT_MS: process.env.CCB_MAX_WAIT_MS || '50000' },
});
console.log('CCB_WAIT_MS = ' + WAIT + (RUN_SLOW ? '   (slow tests enabled)' : ''));

let buf = '';
const pending = new Map();
let nextId = 1;
let stderrAll = '';

child.stderr.on('data', (d) => { stderrAll += d.toString(); });
child.stdout.on('data', (d) => {
  buf += d.toString('utf8');
  let i;
  while ((i = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, i).trim();
    buf = buf.slice(i + 1);
    if (!line) continue;
    let msg;
    try { msg = JSON.parse(line); } catch {
      console.log('  !! NON-JSON on stdout (protocol violation): ' + line.slice(0, 160));
      continue;
    }
    if (msg.id != null && pending.has(msg.id)) {
      const p = pending.get(msg.id);
      pending.delete(msg.id);
      clearTimeout(p.timer);
      msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
    }
  }
});

function rpc(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('RPC timeout: ' + method)), 300_000);
    pending.set(id, { resolve, reject, timer });
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  });
}
const text = (r) => (!r || !r.content) ? '(no content)' : r.content.map((c) => c.text || '').join('\n');
const statusOf = (t) => (t.match(/STATUS: (\w+)/) || [])[1];
const jobIdOf = (t) => (t.match(/\{"job_id":"([0-9a-f]+)"/) || [])[1];
const sessionOf = (t) => (t.match(/SESSION_ID: ([0-9a-f-]+)/) || [])[1];

let pass = 0, fail = 0;
const check = (label, ok, extra) => {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + label + (extra ? '  [' + extra + ']' : ''));
  ok ? pass++ : fail++;
};

/** Call claude_code, then follow the documented polling protocol until it settles. */
async function runToCompletion(args, label, { expectRunningFirst = null, quiet = false } = {}) {
  let t = text(await rpc('tools/call', { name: 'claude_code', arguments: args }));
  const first = statusOf(t);
  if (expectRunningFirst === true) check(label + ': first call returned running', first === 'running', first);
  if (expectRunningFirst === false) check(label + ': first call completed inline', first === 'completed', first);
  if (!quiet) console.log(t.split('\n').slice(0, 6).map((l) => '      ' + l).join('\n'));

  let polls = 0;
  while (first !== 'completed' && statusOf(t) === 'running' && polls < 30) {
    const id = jobIdOf(t) || (t.match(/JOB_ID: ?([0-9a-f]+)/) || [])[1];
    if (!id) break;
    polls++;
    t = text(await rpc('tools/call', { name: 'claude_code_check', arguments: { job_id: id, wait_seconds: 8 } }));
    if (!quiet) console.log('      poll ' + polls + ' -> STATUS=' + statusOf(t));
  }
  return { text: t, first, polls };
}

(async () => {
  console.log('\n=== 1. initialize ===');
  const init = await rpc('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'bridge-test', version: '1.0' } });
  check('serverInfo present', !!init.serverInfo, JSON.stringify(init.serverInfo));
  check('declares tools capability', !!init.capabilities.tools);
  child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method: 'notifications/initialized' }) + '\n');

  console.log('\n=== 2. tools/list ===');
  const tl = await rpc('tools/list', {});
  const names = (tl.tools || []).map((t) => t.name);
  check('4 tools exposed', names.length === 4, names.join(', '));
  check('claude_code_log is exposed', names.includes('claude_code_log'));
  check('every tool has an object inputSchema', (tl.tools || []).every((t) => t.inputSchema && t.inputSchema.type === 'object'));
  check('claude_code requires prompt', JSON.stringify((tl.tools.find((t) => t.name === 'claude_code') || {}).inputSchema.required) === '["prompt"]');

  console.log('\n=== 3. ping ===');
  await rpc('ping', {});
  check('ping answered', true);

  console.log('\n=== 4. robustness ===');
  const bad = await rpc('tools/call', { name: 'nope', arguments: {} });
  check('unknown tool sets isError', bad.isError === true, text(bad).slice(0, 40));
  const badArgs = await rpc('tools/call', { name: 'claude_code', arguments: {} });
  check('missing prompt sets isError', badArgs.isError === true, text(badArgs).slice(0, 40));
  const alive = await rpc('tools/list', {});
  check('server alive after bad calls', (alive.tools || []).length === 4);

  console.log('\n=== 5. real task: token echo ===');
  const r1 = await runToCompletion(
    { prompt: 'Reply with exactly this token and nothing else: BRIDGE_OK' },
    'task1',
    { expectRunningFirst: Number(WAIT) >= 20000 ? false : null }
  );
  check('task1 reached completed', /STATUS: completed/.test(r1.text));
  check('task1 result has BRIDGE_OK', /BRIDGE_OK/.test(r1.text));
  const sessionId = sessionOf(r1.text);
  check('task1 returned SESSION_ID', !!sessionId, sessionId ? sessionId.slice(0, 12) + '...' : '');
  check('task1 reported cost/turns', /COST: \$/.test(r1.text) && /TURNS:/.test(r1.text));

  console.log('\n=== 5b. claude_code_log (live narration, from stream-json) ===');
  const jobsRes = text(await rpc('tools/call', { name: 'claude_code_jobs', arguments: { limit: 5 } }));
  let recentJobId = null;
  try { recentJobId = JSON.parse(jobsRes)[0].job_id; } catch { /* leave null */ }
  check('claude_code_jobs yields a job id to test with', !!recentJobId, recentJobId || '');
  if (recentJobId) {
    const logRes = text(await rpc('tools/call', { name: 'claude_code_log', arguments: { job_id: recentJobId } }));
    const head = logRes.split('\n')[0];
    check('claude_code_log returns a JOB header', /^JOB [0-9a-f]+ {2}status=/.test(head), head.slice(0, 70));
    check('claude_code_log reports recorded steps', /steps=[1-9]/.test(head), head.slice(0, 70));
    check('claude_code_log captured session_started', /\[start\] session /.test(logRes));
    check('claude_code_log line format is [+N.Ns] [kind]', /^\+\d+\.\d+s {2}\[/m.test(logRes));
    const truncated = await rpc('tools/call', { name: 'claude_code_log', arguments: { job_id: recentJobId, since: 99999 } });
    check('claude_code_log since-past-end does not error', truncated.isError !== true);
    const badLog = await rpc('tools/call', { name: 'claude_code_log', arguments: { job_id: 'nosuchjob' } });
    check('claude_code_log unknown job sets isError', badLog.isError === true);
  }

  if (RUN_SLOW) {
    console.log('\n=== 6. long task (must survive past the 60 s MCP request timeout via polling) ===');
    const r2 = await runToCompletion(
      {
        prompt: 'Run this exact command with the Bash tool and wait for it to finish: ' +
                'powershell -NoProfile -Command "Start-Sleep -Seconds 75". ' +
                'After it finishes, reply with exactly this token and nothing else: SLOW_DONE',
        timeout_seconds: 600,
      },
      'task2',
      { expectRunningFirst: true }
    );
    check('task2 reached completed', /STATUS: completed/.test(r2.text));
    check('task2 took longer than one poll window', r2.polls >= 1, r2.polls + ' poll(s)');
    console.log('      final result line: ' + (r2.text.split('RESULT:')[1] || '').trim().split('\n')[0].slice(0, 120));

    console.log('\n=== 7. session continuity (--resume) ===');
    let r3 = await runToCompletion(
      { prompt: 'In my previous message I asked you to reply with a specific token. Reply with just that token.', session_id: sessionId },
      'task3'
    );
    check('resumed session reached completed', /STATUS: completed/.test(r3.text));
    check('resumed session remembered BRIDGE_OK', /BRIDGE_OK/.test(r3.text));
    check('resumed session returned the same session id', sessionOf(r3.text) === sessionId, sessionOf(r3.text) ? 'same' : 'differs');

    console.log('\n=== 8. cwd is honoured ===');
    const tmp = path.join(process.env.USERPROFILE, 'Documents', 'DSH');
    const r4 = await runToCompletion({ prompt: 'Reply with your current working directory and nothing else.', cwd: tmp }, 'task4', { quiet: true });
    check('task4 reports the requested cwd', r4.text.includes('DSH'));
  } else {
    console.log('\n(skipping long-task / resume / cwd tests; pass "slow" to run them)');
  }

  console.log('\n=== misc ===');
  const jl = await rpc('tools/call', { name: 'claude_code_jobs', arguments: { limit: 5 } });
  let jobList = [];
  try { jobList = JSON.parse(text(jl)); } catch { /* ignore */ }
  check('claude_code_jobs lists jobs', Array.isArray(jobList) && jobList.length >= 1, jobList.length + ' job(s)');
  check('job summaries carry job_id + status', jobList.every((j) => j.job_id && j.status));
  check('stderr used for diagnostics, not stdout', stderrAll.length > 0);

  console.log('\n========================================');
  console.log('PASS ' + pass + '   FAIL ' + fail);
  child.kill();
  process.exit(fail ? 1 : 0);
})().catch((e) => { console.log('\nFATAL: ' + e.message); child.kill(); process.exit(2); });
