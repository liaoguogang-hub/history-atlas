#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""清理中文内容中的英文残留。

数据生成过程中偶尔会出现「中文词被误译成英文」的残留，例如：
    厚待之而不使君臣之礼  →  厚待而.dim不使君臣之礼
    吾制民耕 war 粟多则国富  →  吾制民耕种粟多则国富

本脚本按对照表做**上下文敏感的替换**，并对无法确定的一律删除
（删除比保留错误英文更安全：中文语境里一个突兀的英文单词一定是错的）。

用法:
    python tools\clean_english.py data\china.json --in-place
    python tools\clean_english.py data\world.json --in-place
"""
import argparse
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 少数可以安全替换的：这些英文词在中文语境里几乎只对应一个中文词，
# 且替换后不会改变句义。**不要加入有歧义的词**（如 Firewall→防火墙 会造出
# 「郑之防火墙」这种更糟的结果）。
REPLACEMENTS = [
    ("bronze", "青铜"), ("retired", "退居"), ("thousand", "千"),
    ("war", "战"), ("millet", "粟"), ("grain", "谷"),
    ("precursor", "前身"),
]

# 纯拉丁字母单词（长度 ≥2）——删除
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z\-']{1,}")

TEXT_FIELDS_EVENT = ("name", "summary", "detail", "location")
TEXT_FIELDS_PERIOD = ("name", "alias", "summary", "territory", "capital", "culture")
TEXT_FIELDS_FIGURE = ("name", "alias", "summary", "biography")
LIST_FIELDS = ("tags", "achievements", "quotes")


def scrub(text: str) -> tuple:
    """返回 (清理后的文本, 改动次数)。

    策略：只做**删除**与极少数确定的替换，绝不做可能改变句义的意译。
    删除拉丁词后要修复遗留的标点（如同句中的孤立逗号、句号）。
    """
    if not text:
        return text, 0
    orig = text
    n = 0

    # 少数安全替换
    for en, zh in REPLACEMENTS:
        if en in text:
            n += text.count(en)
            text = text.replace(en, zh)

    # 删除残留拉丁词
    text = LATIN_WORD.sub("", text)

    # 修复标点：连续标点、孤立标点、空洞标点
    text = re.sub(r"[ \t]{2,}", " ", text)
    # 标点前多余的孤立点（删词后遗留，如「被俘，.退居」）
    text = re.sub(r"([，、；：])\s*\.", r"\1", text)
    text = re.sub(r"\.\s*([，。；：、])", r"\1", text)
    # 删除中文之间的孤立斜杠 / 反斜杠（删词后遗留，如「士人/km络」）
    text = re.sub(r"[/\\]\s*", "", text)
    # 合并连续标点
    text = re.sub(r"([，。；：、！？])\s*[，。；：、]", r"\1", text)
    text = re.sub(r"，\s*。", "。", text)
    text = re.sub(r"。\s*，", "。", text)
    text = re.sub(r"，\s*；", "；", text)
    text = re.sub(r"；\s*，", "；", text)
    # 标点前后多余空格
    text = re.sub(r"\s+([，。；：、！？）」』])", r"\1", text)
    text = re.sub(r"([（「『])\s+", r"\1", text)
    # 半角逗号分号统一为中文
    text = re.sub(r"\s*,\s*", "，", text)
    text = re.sub(r"\s*;\s*", "；", text)
    # 去掉连续重复的标点
    text = re.sub(r"([，。；：、！？])\1+", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text != orig:
        n += 1
    return text, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--in-place", action="store_true")
    args = ap.parse_args()

    for path in args.files:
        data = json.load(io.open(path, encoding="utf-8"))
        total = 0

        def clean_entity(item, fields):
            nonlocal total
            for fld in fields:
                v = item.get(fld)
                if isinstance(v, str) and v:
                    new, _ = scrub(v)
                    if new != v:
                        item[fld] = new
                        total += 1
            for fld in LIST_FIELDS:
                lst = item.get(fld)
                if isinstance(lst, list):
                    for i, v in enumerate(lst):
                        if isinstance(v, str):
                            new, _ = scrub(v)
                            if new != v:
                                lst[i] = new
                                total += 1

        for e in data.get("events", []):
            clean_entity(e, TEXT_FIELDS_EVENT)
        for p in data.get("periods", []):
            clean_entity(p, TEXT_FIELDS_PERIOD)
        for f in data.get("figures", []):
            clean_entity(f, TEXT_FIELDS_FIGURE)

        out = path if args.in_place else path.replace(".json", ".clean.json")
        io.open(out, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=1)
        )
        print(f"{path} -> {out}: 清理了 {total} 个字段")


if __name__ == "__main__":
    main()
