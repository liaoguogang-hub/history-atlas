# -*- coding: utf-8 -*-
"""检查分片内容的本地质量：拉丁残留、字数、字段、id 存在性、引号配对。"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

LATIN = re.compile(r"[A-Za-z]")
ANY_NON_CJK_PUNCT = re.compile(r"[^\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2014\u2018\u2019\u201c\u201d\u00b7\u2026\n\r\t0-9,.:;%\-()\[\]—·]+")

FIELDS = ("id", "name", "alias", "role", "birthYear", "deathYear", "gender",
          "periodId", "summary", "biography", "achievements", "quotes",
          "relatedFigures", "relatedEvents", "tags")


def check(path, known=None):
    data = json.load(io.open(path, encoding='utf-8'))
    problems = []
    for f in data:
        fid = f.get('id', '<无id>')
        for k in FIELDS:
            if k not in f:
                problems.append('%s 缺字段 %s' % (fid, k))
        # 拉丁字母（只查正文类字段：id/gender/periodId 允许拉丁）
        for k in ('alias', 'role', 'summary', 'biography'):
            v = f.get(k) or ''
            if isinstance(v, str):
                for m in LATIN.finditer(v):
                    s = max(0, m.start() - 25)
                    e = min(len(v), m.end() + 25)
                    problems.append('%s [%s] 拉丁 %r: …%s…' % (fid, k, m.group(0), v[s:e]))
        for k in ('achievements', 'quotes', 'tags'):
            for it in (f.get(k) or []):
                if isinstance(it, str):
                    for m in LATIN.finditer(it):
                        s = max(0, m.start() - 25)
                        e = min(len(it), m.end() + 25)
                        problems.append('%s [%s] 拉丁 %r: …%s…' % (fid, k, m.group(0), it[s:e]))
        bio = f.get('biography') or ''
        if len(bio) < 380:
            problems.append('%s 生平过短 %d' % (fid, len(bio)))
        if len(f.get('achievements') or []) < 6:
            problems.append('%s 成就过少 %d' % (fid, len(f.get('achievements') or [])))
        q = f.get('quotes') or []
        if not (1 <= len(q) <= 2):
            problems.append('%s 引文数 %d' % (fid, len(q)))
        s = f.get('summary') or ''
        if not (35 <= len(s) <= 55):
            problems.append('%s 摘要长度 %d' % (fid, len(s)))
        # 引号配对
        for k in ('biography', 'summary'):
            v = f.get(k) or ''
            if v.count('「') != v.count('」'):
                problems.append('%s [%s] 引号不配对 %d/%d' % (fid, k, v.count('「'), v.count('」')))
            if v.count('“') or v.count('”'):
                problems.append('%s [%s] 含弯引号' % (fid, k))
        for it in (f.get('achievements') or []) + (f.get('quotes') or []):
            if '“' in it or '”' in it:
                problems.append('%s 条目含弯引号' % fid)
            if it.count('「') != it.count('」'):
                problems.append('%s 条目引号不配对' % fid)
        if known is not None:
            for r in (f.get('relatedFigures') or []):
                if r not in known['fig']:
                    problems.append('%s relatedFigures 不存在: %s' % (fid, r))
            for r in (f.get('relatedEvents') or []):
                if r not in known['ev']:
                    problems.append('%s relatedEvents 不存在: %s' % (fid, r))
    return data, problems


def main():
    path = sys.argv[1]
    known = None
    if len(sys.argv) > 2:
        china = json.load(io.open('data/china.json', encoding='utf-8'))
        known = {'fig': set(f['id'] for f in china['figures']),
                 'ev': set(e['id'] for e in china['events'])}
    data, problems = check(path, known)
    print('=== %s ===' % path)
    print('条目 %d' % len(data))
    lens = sorted(len(f.get('biography') or '') for f in data)
    if lens:
        print('生平字数 min=%d max=%d avg=%d' % (lens[0], lens[-1], sum(lens) // len(lens)))
    ids = [f['id'] for f in data]
    dup = set(x for x in ids if ids.count(x) > 1)
    if dup:
        problems.append('批内 id 重复: %s' % sorted(dup))
    if problems:
        print('✗ %d 个问题' % len(problems))
        for p in problems:
            print('  ' + p)
        sys.exit(1)
    print('✓ 未发现问题')


if __name__ == '__main__':
    main()
