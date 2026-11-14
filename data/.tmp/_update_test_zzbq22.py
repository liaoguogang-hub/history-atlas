# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.2.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace("dataset.figures.size >= 351", "dataset.figures.size >= 345")

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v2.2.0：人物去重 + 父时期代表人物汇总
        // 同一历史人物不得以不同译名重复出现
        val dupNames = dataset.figures
            .groupBy { it.name.replace(Regex("[·・\\\\-—()（）：:]"), "") }
            .filterValues { it.size > 1 }
        assertTrue(
            dupNames.isEmpty(),
            "存在同名的重复人物: " + dupNames.keys.take(5),
        )

        // 已合并的冗余 id 不得残留
        listOf(
            "fig-leibniz", "fig-jawaharlal-nehru", "fig-ibn-majid",
            "fig-w-john-wycliffe", "fig-w-augustus-alt",
            "fig-zzbq9-montezuma", "fig-montezuma",
        ).forEach { gone ->
            assertTrue(
                dataset.figures.none { it.id == gone },
                "冗余人物未删除: " + gone,
            )
        }

        // 讹误名「薄利丘」（Wycliffe 的错误音译）必须已清除
        assertTrue(
            dataset.figures.none { it.name.contains("薄利丘") },
            "仍存在讹误人名: 约翰·薄利丘",
        )

        // 父级容器时期的代表人物应从子时期汇总，不得为空
        listOf("w-america-precol", "w-east-asia").forEach { pid ->
            val period = dataset.periods.find { it.id == pid }
            assertTrue(period != null, "缺少时期: " + pid)
            assertTrue(
                period!!.keyFigures.isNotEmpty(),
                "父时期缺代表人物: " + pid,
            )
        }

        // 冷战时期代表人物应为冷战决策者
        val coldWar = dataset.periods.find { it.id == "w-cold-war" }
        assertTrue(coldWar != null, "缺少 w-cold-war")
        val coldNames = coldWar!!.keyFigures.mapNotNull { fid ->
            dataset.figures.find { it.id == fid }?.name
        }
        assertTrue(
            coldNames.any { it.contains("杜鲁门") || it.contains("赫鲁晓夫") || it.contains("尼克松") },
            "冷战代表人物不合理: " + coldNames,
        )

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
