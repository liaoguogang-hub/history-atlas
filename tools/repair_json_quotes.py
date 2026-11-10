"""修复 JSON 里因正文出现半角双引号而导致的语法错误。

成因：撰写扩充分片时，正文里引用了「他说的话」但误用了半角双引号 "，
而 JSON 字符串只能用 " 包裹，于是该双引号提前终止了字符串。

处理方式：逐行扫描，对处于字符串值内部、且未转义的半角双引号
补上反斜杠转义。仅在解析失败时启用，正常文件不动。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")


def repair(path):
    raw = io.open(path, encoding="utf-8").read()
    try:
        json.loads(raw)
        return False, "本来就合法"
    except json.JSONDecodeError:
        pass

    out = []
    in_str = False
    escaped = False
    i = 0
    n = len(raw)
    while i < n:
        ch = raw[i]
        if not in_str:
            out.append(ch)
            if ch == '"':
                in_str = True
            i += 1
            continue
        # 已在字符串内
        if escaped:
            out.append(ch)
            escaped = False
            i += 1
            continue
        if ch == "\\":
            out.append(ch)
            escaped = True
            i += 1
            continue
        if ch == '"':
            # 看后面是不是合法的 JSON 结构延续：
            # 后面若紧跟 , } ] : 或空白+这些，说明是真正的结束引号
            j = i + 1
            while j < n and raw[j] in " \t\r\n":
                j += 1
            if j >= n or raw[j] in ",}]:":
                out.append(ch)
                in_str = False
            else:
                # 是正文里的裸双引号，转义
                out.append('\\"')
            i += 1
            continue
        out.append(ch)
        i += 1

    fixed = "".join(out)
    try:
        json.loads(fixed)
    except json.JSONDecodeError as e:
        io.open(path, "w", encoding="utf-8").write(fixed)
        return True, f"已转义，但仍有解析错误：{e}"

    io.open(path, "w", encoding="utf-8").write(fixed)
    return True, "已转义并可正常解析"


def main():
    for path in sys.argv[1:]:
        changed, msg = repair(path)
        print(f"{path}: {msg}")


if __name__ == "__main__":
    main()
