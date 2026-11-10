#!/usr/bin/env node
/**
 * extract_vault_docs.mjs — 把 Obsidian vault 里的 pdf/epub 提取成同名 .md 旁挂文件
 *
 * 为什么需要这个：
 *   dsh-obsidian 插件的源码里 isMarkdownFile() 硬编码只认 .md，
 *   obsidian_read() 走 readFile(path,"utf8") —— 对 pdf 就是返回 %PDF-1.7 的字节流，
 *   对 epub 就是 ZIP 结构，模型拿不到正文。
 *   所以必须在插件之外把二进制文档转成 markdown，插件才能搜到。
 *
 * 技术选型（全部在 DSH web profile 已装的依赖里，零新增、零下载、全离线）：
 *   PDF  → markitdown-node  convertToMarkdown(Buffer)
 *          ⚠️ 必须传 Buffer，传 {filePath}/{path} 会返回空字符串
 *          ⚠️ 必须用 CJS 构建 dist/index.cjs，ESM 构建 dist/index.mjs 是坏的
 *             （里面 require("node-pptx-parser") 写在 ESM scope 里，import 直接崩）
 *   EPUB → jszip 解包 + 剥 HTML 标签
 *          markitdown 对 epub 不稳（实测 5 个里 3 个返空），JSZip 实测 5/5 成功。
 *          epub 本质是 zip，正文在 xhtml 里；DRM 只加密字体/图片，文本流是明文。
 *
 * 用法：
 *   node extract_vault_docs.mjs --limit 20            # 抽样跑 20 个
 *   node extract_vault_docs.mjs --limit 20 --dry-run  # 只报告不写文件
 *   node extract_vault_docs.mjs                        # 全量
 *   node extract_vault_docs.mjs --rescan              # 强制重转（默认跳过已存在的 md）
 *
 * 产出（与原文同目录）：
 *   raw/xxx/指南.pdf   →   raw/xxx/指南.md
 *   frontmatter 里记 source/source_type/size/chars，原文一字不动。
 */
import path from "node:path";
import fs from "node:fs";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ── 参数 ────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
const arg = (name, dflt) => {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[i + 1] : dflt;
};
const has = (name) => argv.includes(name);

const VAULT = arg("--vault", "D:\\Obsidian\\LeoLiao");
const LIMIT = parseInt(arg("--limit", "0"), 10);
const DRY_RUN = has("--dry-run");
const RESCAN = has("--rescan");
const ROOT = arg("--root", path.join(VAULT, "raw"));
const CONCURRENCY = parseInt(arg("--concurrency", "2"), 10);

// ── 定位 DSH profile 依赖 ───────────────────────────────────────────
const PROFILE = process.env.USERPROFILE + "\\.dsh\\profiles\\web\\node_modules";
const dshRequire = createRequire(path.join(PROFILE, "package.json"));

const { convertToMarkdown } = dshRequire(path.join(PROFILE, "markitdown-node", "dist", "index.cjs"));
const JSZip = dshRequire("jszip");

// ── 扫描 ────────────────────────────────────────────────────────────
function walk(dir, out = [], depth = 0) {
  if (depth > 6) return out;
  let es = [];
  try {
    es = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  for (const e of es) {
    if (e.name.startsWith(".")) continue;
    const f = path.join(dir, e.name);
    if (e.isDirectory()) walk(f, out, depth + 1);
    else out.push(f);
  }
  return out;
}

const SKIP_DIRS = new Set(["node_modules", "epub_extracted", "temp_moyan_extracted", "tmp_extract"]);
const TARGET_EXT = new Set([".pdf", ".epub"]);

function collect() {
  const all = walk(ROOT);
  const hits = all.filter((f) => {
    if (SKIP_DIRS.has(path.basename(path.dirname(f)))) return false;
    return TARGET_EXT.has(path.extname(f).toLowerCase());
  });
  // 大文件排后面，先跑小的，早点看到效果
  hits.sort((a, b) => {
    const ea = path.extname(a).toLowerCase();
    const eb = path.extname(b).toLowerCase();
    if (ea !== eb) return ea === ".pdf" ? -1 : 1;
    return fs.statSync(a).size - fs.statSync(b).size;
  });
  return hits;
}

// ── 提取 ────────────────────────────────────────────────────────────
function htmlToText(html) {
  return html
    .replace(/<head[\s\S]*?<\/head>/gi, "")
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * 修复中文 PDF 的「一字一行」。
 *
 * 背景：中文 PDF 的文本层通常是每个字一个独立定位符，没有词组切分。
 * markitdown 忠实地把每个字输出成一行，于是「谈判药品续约规则」变成
 * 谈/判/药/品/续/约/规/则 —— 这样产出的 md 全文搜索完全失效：
 * grep "谈判药品" 匹配不到任何一行。
 *
 * 实测数据（raw/医保目录/2026/谈判药品续约规则.pdf）：
 *   总行数 4271，空行仅 9 行，长度≤2 的行 4262 行 —— 即 99.8% 是被拆散的碎片。
 *
 * 判定与修复：
 *   1. 「碎片行」= 长度 ≤ 2 且主要由 CJK/中文标点构成；
 *   2. 连续碎片行合并成一行；
 *   3. 合并块遇到以下任一情况结束：空行 / 正常长行 / 块内累计字符数达到上限。
 *      上限是必要的——否则整篇 4000 行的文档会被压成一行，失去可读性；
 *      阈值取 60 字，接近一个自然句子的长度。
 *   4. 英文文本不受影响（每行长度 > 2，不构成碎片）。
 */
const CJK_SPLIT_MAX = 60;

function repairCjkLineSplit(text) {
  const lines = text.split(/\r?\n/);
  // 碎片行：长度 ≤ 2。中文 PDF 里每个字/标点/数字都是独立定位符。
  // 这里不再要求 CJK 占比——数字和中文标点同样是碎片的一部分
  // （实测「附件」「3」「，」都被单独成行）。
  const isFragment = (s) => {
    const t = s.trim();
    if (!t || t.length > 2) return false;
    // 排除真正的英文短行（如 ")" "OK"）——含拉丁字母且不是纯符号的，不算碎片
    if (/[A-Za-z]{2,}/.test(t)) return false;
    return true;
  };

  const out = [];
  let buf = [];
  let bufLen = 0;

  const flush = () => {
    if (buf.length) {
      out.push(buf.join(""));
      buf = [];
      bufLen = 0;
    }
  };

  for (const raw of lines) {
    const line = raw.trim();
    if (!line) {
      flush();
      out.push("");
      continue;
    }
    if (isFragment(line)) {
      buf.push(line);
      bufLen += line.length;
      if (bufLen >= CJK_SPLIT_MAX) flush(); // 达到上限就断开，保住可读性
    } else {
      flush();
      out.push(line);
    }
  }
  flush();

  return out.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

async function extractPdf(file) {
  const out = await convertToMarkdown(fs.readFileSync(file));
  const raw = typeof out === "string" ? out : out?.markdown || out?.textContent || "";
  // 中文 PDF 一字一行 → 修复，否则全文搜索失效（见 repairCjkLineSplit 注释）
  return repairCjkLineSplit(raw);
}

async function extractEpub(file) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const names = Object.keys(zip.files).filter((n) => !zip.files[n].dir && /\.x?html?$/i.test(n));
  const parts = [];
  for (const n of names) {
    const t = htmlToText(await zip.file(n).async("string"));
    if (t) parts.push(t);
  }
  return parts.join("\n\n");
}

// ── 输出 ────────────────────────────────────────────────────────────
function yamlQuote(s) {
  return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
}

function buildMd(srcPath, text, sizeBytes) {
  const rel = path.relative(VAULT, srcPath).replace(/\\/g, "/");
  const base = path.basename(srcPath, path.extname(srcPath));
  const ext = path.extname(srcPath).toLowerCase();
  const fm = [
    "---",
    `source: ${yamlQuote(rel)}`,
    `source_type: ${ext.slice(1)}`,
    `source_size: ${sizeBytes}`,
    `chars: ${text.length}`,
    `extracted_by: extract_vault_docs.mjs`,
    `extracted_at: ${new Date().toISOString().slice(0, 10)}`,
    "---",
    "",
    `# ${base}`,
    "",
  ].join("\n");
  // 正文里的 markdown 标题会和 frontmatter 后的 H1 打架，把正文里的 H1 降级
  const body = text.replace(/^#\s+/gm, "## ");
  return fm + body.trim() + "\n";
}

async function processOne(file) {
  const ext = path.extname(file).toLowerCase();
  const outPath = file.slice(0, -ext.length) + ".md";
  const size = fs.statSync(file).size;

  if (!RESCAN && fs.existsSync(outPath)) {
    return { status: "skip", file, outPath, size };
  }
  if (DRY_RUN) {
    return { status: "dry", file, outPath, size };
  }

  const t0 = Date.now();
  try {
    const text = ext === ".pdf" ? await extractPdf(file) : await extractEpub(file);
    const ms = Date.now() - t0;
    if (!text || text.trim().length < 50) {
      return { status: "empty", file, outPath, size, ms, chars: text?.length || 0 };
    }
    fs.writeFileSync(outPath, buildMd(file, text, size), "utf8");
    return { status: "ok", file, outPath, size, ms, chars: text.length };
  } catch (e) {
    return { status: "error", file, outPath, size, ms: Date.now() - t0, err: e.message };
  }
}

// ── 主流程 ──────────────────────────────────────────────────────────
async function main() {
  console.log(`vault = ${VAULT}`);
  console.log(`root  = ${ROOT}`);
  console.log(`dry-run=${DRY_RUN}  rescan=${RESCAN}  limit=${LIMIT || "∞"}  concurrency=${CONCURRENCY}\n`);

  const files = collect();
  console.log(`扫描到 ${files.length} 个待提取文件（pdf + epub）`);
  const list = LIMIT ? files.slice(0, LIMIT) : files;
  console.log(`本次处理 ${list.length} 个\n`);

  const stats = { ok: 0, skip: 0, empty: 0, error: 0, dry: 0 };
  let bytesWritten = 0;
  let idx = 0;

  async function worker() {
    while (idx < list.length) {
      const i = idx++;
      const f = list[i];
      const r = await processOne(f);
      stats[r.status] = (stats[r.status] || 0) + 1;
      if (r.status === "ok") bytesWritten += r.chars * 2;

      const rel = path.relative(VAULT, r.file);
      const tag = { ok: "✓", skip: "-", empty: "△", error: "✗", dry: "·" }[r.status];
      const detail =
        r.status === "ok" ? `${r.chars} 字 ${r.ms}ms`
        : r.status === "error" ? r.err.slice(0, 70)
        : r.status === "empty" ? `只提取到 ${r.chars} 字（疑似扫描件/加密）`
        : r.status === "skip" ? "已有 .md，跳过"
        : "未写入";
      console.log(`  [${String(i + 1).padStart(3)}/${list.length}] ${tag} ${rel} — ${detail}`);
    }
  }

  await Promise.all(Array.from({ length: CONCURRENCY }, worker));

  console.log(`\n完成：成功 ${stats.ok}  跳过 ${stats.skip}  空/无正文 ${stats.empty}  失败 ${stats.error}` +
    (DRY_RUN ? `  (dry-run ${stats.dry})` : ""));
  if (bytesWritten) console.log(`产出约 ${(bytesWritten / 1024 / 1024).toFixed(1)} MB 文本`);
}

main().catch((e) => {
  console.error("致命错误:", e);
  process.exit(1);
});
