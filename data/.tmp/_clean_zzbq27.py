# -*- coding: utf-8 -*-
"""清理 zzbq27 生成脚本中与既有条目重复的人物定义，并修正引用。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "data/.tmp/_gen_zzbq27_liberation.py"
s = io.open(p, encoding="utf-8").read()


def drop_object(src, anchor):
    """删除以 anchor 标识的整个 {...} 对象（含尾部逗号）。"""
    i = src.find(anchor)
    if i < 0:
        return src, False
    start = src.rfind("{", 0, i)
    depth = 0
    j = start
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    end = j + 1
    while end < len(src) and src[end] in ",\n ":
        end += 1
    return src[:start] + src[end:], True


# 林彪已在库（fig-lin-biao），删除本批重复定义
s, ok1 = drop_object(s, '"id": "fig-zzbq27-linbiao"')
print("删除 林彪 重复定义:", ok1)

# 陈毅：库中 fig-chen-yi 实际是「陈云」的错标 id，不能直接引用。
# 本批保留自己新建的 fig-zzbq27-chen-yi（内容为真正的陈毅）。
# 但需确认没有 id 冲突，故不改动。

# 引用改为既有 id
s = s.replace('"fig-zzbq27-linbiao"', '"fig-lin-biao"')

# fig-chen-yi 在库里是陈云，本批事件的 figures 不应引用它
# （事件里用的是 fig-zzbq27-chen-yi，没问题）

io.open(p, "w", encoding="utf-8").write(s)
print("已修正引用指向 fig-lin-biao")
