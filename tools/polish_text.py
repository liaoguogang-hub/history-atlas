import io
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 清理占位数据留下的粗糙痕迹：
#   - role 为英文标识（historical_figure 等）→ 中文
#   - 时期名后重复的「时期」（如「旧石器时代时期」）
#   - summary / biography 中出现的「的相关的相关」类重复

ROLE_CN = {
    "historical_figure": "历史人物",
    "ruler": "君主",
    "general": "将领",
    "politician": "政治家",
    "scholar": "学者",
    "scientist": "科学家",
    "poet": "诗人",
    "artist": "画家",
    "calligrapher": "书法家",
    "painter": "画家",
    "engineer": "工程师",
    "explorer": "航海家",
    "revolutionary": "革命家",
    "reformer": "改革家",
    "diplomat": "外交家",
    "chief": "首领",
    "philosopher": "哲学家",
    "author": "作家",
    "king": "国王",
    "queen": "女王",
    "emperor": "皇帝",
    "empress": "皇后",
}


def fix_dup_period(text):
    """把「XX时期时期」还原为「XX时期」，「XX的相关的相关」修正。"""
    if not text:
        return text
    out = re.sub(r"(时代|王朝|朝代|时期)时期", r"\1", text)
    out = re.sub(r"的\s*相关的\s*相关", "的相关", out)
    out = re.sub(r"时期的\s*时期的", "时期的", out)
    return out


def main():
    path = sys.argv[1]
    data = json.load(io.open(path, encoding="utf-8"))
    n_role = 0
    n_text = 0

    for f in data.get("figures") or []:
        r = f.get("role")
        if isinstance(r, str) and r in ROLE_CN:
            f["role"] = ROLE_CN[r]
            n_role += 1
        for k in ("summary", "biography", "lifeText"):
            v = f.get(k)
            if isinstance(v, str) and v:
                nv = fix_dup_period(v)
                if nv != v:
                    f[k] = nv
                    n_text += 1

    for e in data.get("events") or []:
        for k in ("summary", "detail", "name"):
            v = e.get(k)
            if isinstance(v, str) and v:
                nv = fix_dup_period(v)
                if nv != v:
                    e[k] = nv
                    n_text += 1

    for p in data.get("periods") or []:
        for k in ("summary", "name"):
            v = p.get(k)
            if isinstance(v, str) and v:
                nv = fix_dup_period(v)
                if nv != v:
                    p[k] = nv
                    n_text += 1

    io.open(path, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{path}: role localized {n_role}, text deduped {n_text}")


if __name__ == "__main__":
    main()
