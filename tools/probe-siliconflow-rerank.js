// probe-siliconflow-rerank.js
// Determines WHY Chatbox reports `20012 Model does not exist` for
// BAAI/bge-reranker-v2-m3 while local WeKnora uses the same model successfully.
//
// Tests, with the key already stored in Chatbox's config:
//   A. POST /v1/rerank                 Cohere-shaped body  -> the endpoint WeKnora-style clients use
//   B. POST /v2/rerank                 Cohere v2 path      -> what a newer Cohere SDK would call
//   C. POST /v1/chat/completions       with the same model -> expected to be the failing path
//   D. GET  /v1/models                                     -> what the provider "Check" may call
const fs = require('fs');
const path = require('path');

const CONFIG = path.join(process.env.APPDATA, 'xyz.chatboxapp.app', 'config.json');
const cfg = JSON.parse(fs.readFileSync(CONFIG, 'utf8'));
const key = cfg.settings.providers?.siliconflow?.apiKey;
if (!key) { console.error('no siliconflow apiKey in Chatbox config'); process.exit(1); }

const BASE = 'https://api.siliconflow.cn/v1';
const MODEL = process.argv[2] || 'BAAI/bge-reranker-v2-m3';

async function probe(label, url, init) {
  const t0 = Date.now();
  try {
    const r = await fetch(url, init);
    const ms = Date.now() - t0;
    const text = await r.text();
    let body = text;
    try { body = JSON.stringify(JSON.parse(text)); } catch { /* keep raw */ }
    console.log(`${label}\n  ${init && init.method ? init.method : 'GET'} ${url}`);
    console.log(`  -> HTTP ${r.status}  ${ms}ms`);
    console.log(`  body: ${body.slice(0, 400)}`);
    console.log('');
    return { status: r.status, body };
  } catch (e) {
    console.log(`${label}\n  ${url}\n  -> FETCH FAILED: ${e.message}\n`);
    return { status: 0, body: e.message };
  }
}

(async () => {
  console.log('model : ' + MODEL);
  console.log('key   : ' + key.slice(0, 6) + '...' + key.slice(-4) + ' (len ' + key.length + ')');
  console.log('base  : ' + BASE);
  console.log('');

  const auth = { Authorization: 'Bearer ' + key, 'Content-Type': 'application/json' };

  await probe('A. Cohere-shaped rerank at /v1/rerank', BASE + '/rerank', {
    method: 'POST',
    headers: auth,
    body: JSON.stringify({
      model: MODEL,
      query: '什么是知识库',
      documents: ['知识库是文档的集合', '今天天气不错', '检索增强生成'],
      top_n: 2,
    }),
  });

  await probe('B. Cohere v2 path /v2/rerank', 'https://api.siliconflow.cn/v2/rerank', {
    method: 'POST',
    headers: auth,
    body: JSON.stringify({ model: MODEL, query: '什么是知识库', documents: ['知识库是文档的集合', '今天天气不错'], top_n: 2 }),
  });

  await probe('C. chat/completions with the SAME model (the suspect)', BASE + '/chat/completions', {
    method: 'POST',
    headers: auth,
    body: JSON.stringify({ model: MODEL, messages: [{ role: 'user', content: 'hi' }], max_tokens: 5 }),
  });

  await probe('D. GET /v1/models', BASE + '/models', { method: 'GET', headers: { Authorization: 'Bearer ' + key } });
})().catch((e) => { console.error('FAILED: ' + e.message); process.exit(1); });
