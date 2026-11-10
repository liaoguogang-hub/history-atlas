// test-minimax-toolcalling.js
// Verifies that MiniMax-M3 supports OpenAI-protocol function calling through the same
// endpoint Chatbox will use. Chatbox Work Mode depends on this.
const fs = require('fs');
const path = require('path');

const key = JSON.parse(fs.readFileSync(path.join(process.env.USERPROFILE, '.claude', 'settings.json'), 'utf8'))
  ?.env?.ANTHROPIC_AUTH_TOKEN;
if (!key) { console.error('no key'); process.exit(1); }

const body = {
  model: 'MiniMax-M3',
  messages: [{ role: 'user', content: 'What is the weather in Beijing? Use the tool.' }],
  tools: [{
    type: 'function',
    function: {
      name: 'get_weather',
      description: 'Get current weather for a city',
      parameters: {
        type: 'object',
        properties: { city: { type: 'string', description: 'City name' } },
        required: ['city'],
      },
    },
  }],
  tool_choice: 'auto',
  max_tokens: 300,
};

(async () => {
  const t0 = Date.now();
  const res = await fetch('https://api.minimaxi.com/v1/chat/completions', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const ms = Date.now() - t0;
  const text = await res.text();
  console.log('HTTP ' + res.status + '  ' + ms + 'ms');
  let j;
  try { j = JSON.parse(text); } catch { console.log('non-JSON: ' + text.slice(0, 500)); process.exit(1); }

  if (!res.ok) { console.log('ERROR body: ' + JSON.stringify(j).slice(0, 500)); process.exit(1); }

  const ch = j.choices?.[0];
  console.log('model         : ' + j.model);
  console.log('finish_reason : ' + ch?.finish_reason);
  console.log('usage         : ' + JSON.stringify(j.usage));

  const tc = ch?.message?.tool_calls;
  if (tc && tc.length) {
    console.log('');
    console.log('TOOL CALLS RETURNED: ' + tc.length);
    tc.forEach((c, i) => {
      console.log('  [' + i + '] id=' + c.id);
      console.log('      name=' + c.function?.name);
      console.log('      args=' + c.function?.arguments);
    });
    console.log('');
    console.log('RESULT: PASS - MiniMax-M3 supports OpenAI-protocol function calling.');
  } else {
    console.log('');
    console.log('message.content: ' + JSON.stringify(ch?.message?.content));
    console.log('');
    console.log('RESULT: no tool_calls returned.');
  }
})().catch((e) => { console.error('FETCH FAILED: ' + e.message); process.exit(1); });
