# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 断言至 v1.9.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace("dataset.events.size >= 438", "dataset.events.size >= 434")
s = s.replace("dataset.figures.size >= 272", "dataset.figures.size >= 283")

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v1.9.0：西方思想史链条 + 跨 scope 冲突归零
        listOf(
            "经院哲学", "宗教改革", "启蒙运动", "德国古典哲学",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: " + name)
        }
        listOf(
            "奥古斯丁", "阿奎那", "但丁", "马基雅维利", "洛克",
            "亚当·斯密", "黑格尔", "尼采", "韦伯", "维特根斯坦",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: " + name)
        }

        // 世界史不得再包含中国史错挂条目（这些属于中国史 scope）
        listOf("五四运动与新文化运动的影响", "长征与遵义会议", "延安整风与延安精神")
            .forEach { name ->
                assertTrue(
                    eventNames.none { it.contains(name) },
                    "世界史仍含中国史错挂条目: " + name,
                )
            }

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
