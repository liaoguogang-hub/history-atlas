# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.3.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace("dataset.events.size >= 440", "dataset.events.size >= 446")
s = s.replace("dataset.figures.size >= 345", "dataset.figures.size >= 354")

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v2.3.0：地区错挂修复 + 拉丁美洲补强
        // 地区专题时期不得混入其他大洲的人物
        val regionForbidden = mapOf(
            "w-southeast-asia" to listOf("黑格尔", "惠灵顿", "威伯福斯", "玻利瓦尔", "圣马丁"),
            "w-modern-south-asia" to listOf("胡志明", "董必武", "陈云", "鲍林", "冯·诺依曼", "铁托"),
        )
        regionForbidden.forEach { (pid, forbidden) ->
            val period = dataset.periods.find { it.id == pid }
            if (period != null) {
                val names = period.keyFigures.mapNotNull { fid ->
                    dataset.figures.find { it.id == fid }?.name
                }
                forbidden.forEach { bad ->
                    assertTrue(
                        names.none { it.contains(bad) },
                        "地区时期 $pid 混入了不相干人物: " + bad,
                    )
                }
            }
        }

        // 拉丁美洲必须有实质内容（曾长期是 0 人物的空容器）
        val latin = dataset.periods.find { it.id == "w-latin-america" }
        assertTrue(latin != null, "缺少 w-latin-america")
        assertTrue(
            latin!!.keyFigures.size >= 5,
            "拉丁美洲代表人物过少: " + latin.keyFigures.size,
        )
        listOf("玻利瓦尔", "圣马丁", "庇隆", "瓦加斯", "卡德纳斯", "阿连德", "查韦斯")
            .forEach { name ->
                assertTrue(figureNames.any { it.contains(name) }, "拉美缺少人物: " + name)
            }
        listOf("拉丁美洲独立", "民粹主义", "民主化").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "拉美缺少事件: " + name)
        }

        // 东南亚应有真实的本地区人物
        val sea = dataset.periods.find { it.id == "w-southeast-asia" }
        if (sea != null) {
            val seaNames = sea.keyFigures.mapNotNull { fid ->
                dataset.figures.find { it.id == fid }?.name
            }
            assertTrue(
                seaNames.any { it.contains("那莱") || it.contains("库恩") },
                "东南亚代表人物不合理: " + seaNames,
            )
        }

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
