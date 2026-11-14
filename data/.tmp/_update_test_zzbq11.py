# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 的断言：规模下限 + 禁止英文空壳事件名。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace("dataset.events.size >= 426", "dataset.events.size >= 415")
s = s.replace("dataset.events.size >= 439", "dataset.events.size >= 438")

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // 事件名不得是英文空壳（backfill 兜底生成的 jin taikang 之类）
        val shellLike = dataset.events.filter { e ->
            Regex("[a-zA-Z]{3,}").containsMatchIn(e.name)
        }
        assertTrue(
            shellLike.isEmpty(),
            "存在英文空壳事件名: " + shellLike.joinToString { it.id + "=" + it.name },
        )

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
