# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.7.0（解放战争内容补强）。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

# 规模下限
s = s.replace("dataset.events.size >= 415", "dataset.events.size >= 418")
s = s.replace("dataset.figures.size >= 482", "dataset.figures.size >= 491")

anchor = "    fun `打包的中国史数据可被完整解析且新补充条目未丢失`()"
i = s.find(anchor)
assert i > 0, "锚点未找到"

body_start = s.find("{", i)
depth = 0
j = body_start
while j < len(s):
    if s[j] == "{":
        depth += 1
    elif s[j] == "}":
        depth -= 1
        if depth == 0:
            break
    j += 1

BLOCK = '''
        // v2.7.0：解放战争时期内容补强
        val liberation = dataset.periods.find { it.id == "cn-modern-liberation" }
        assertTrue(liberation != null, "缺少 cn-modern-liberation")

        // 该时期代表人物应同时包含国共双方
        val libNames = liberation!!.keyFigures.mapNotNull { fid ->
            dataset.figures.find { it.id == fid }?.name
        }
        assertTrue(
            libNames.any { it.contains("毛泽东") } && libNames.any { it.contains("蒋介石") },
            "解放战争代表人物缺国共双方: " + libNames,
        )
        assertTrue(
            libNames.size >= 6,
            "解放战争代表人物过少: " + libNames.size,
        )

        // 解放战争时期的事件不得有 figures 为空的
        val libEvents = dataset.events.filter { it.periodId == "cn-modern-liberation" }
        assertTrue(libEvents.size >= 7, "解放战争事件过少: " + libEvents.size)
        val emptyFig = libEvents.filter { it.figures.isEmpty() }
        assertTrue(
            emptyFig.isEmpty(),
            "解放战争事件缺人物关联: " + emptyFig.map { it.name },
        )

        // 该时期必须覆盖三大战役与重庆谈判
        listOf("重庆谈判", "辽沈", "淮海", "平津", "渡江").forEach { name ->
            assertTrue(
                libEvents.any { it.name.contains(name) },
                "解放战争缺少事件: " + name,
            )
        }

        // 新增的国共双方关键人物必须存在
        listOf(
            "蒋介石", "白崇禧", "杜聿明", "傅作义", "张治中",
            "粟裕", "罗荣桓", "陈毅",
        ).forEach { name ->
            assertTrue(
                dataset.figures.any { it.name.contains(name) },
                "缺少人物: " + name,
            )
        }

'''

s = s[:j] + BLOCK + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
