# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.1.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace("dataset.events.size >= 430", "dataset.events.size >= 440")
s = s.replace("dataset.figures.size >= 327", "dataset.figures.size >= 351")

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v2.1.0：古代文明 + 中世纪 + 冷战人物补强，keyFigures 全面回填
        listOf(
            "哈拉帕", "米诺斯", "迈锡尼", "亚述", "查士丁尼", "地理大发现",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: " + name)
        }
        listOf(
            "阿伽门农", "海伦", "珀涅罗珀", "亚述巴尼拔", "米诺斯",
            "查士丁尼", "狄奥多拉", "贝利撒留", "曼努埃尔", "迪亚士", "麦哲伦",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: " + name)
        }

        // keyFigures 必须覆盖绝大多数时期（容器的史前时期可为空）
        val substantivePeriods = dataset.periods.filter { p ->
            !p.id.startsWith("w-cc-") &&
                p.id !in setOf(
                    "w-prehistory", "w-paleolithic", "w-neolithic", "w-aryan",
                    "w-zhou", "w-medieval-china", "w-america-precol",
                    "w-east-asia", "w-tang-song", "w-latin-america",
                )
        }
        val emptyKey = substantivePeriods.filter { it.keyFigures.isEmpty() }
        assertTrue(
            emptyKey.isEmpty(),
            "以下时期缺代表人物: " + emptyKey.joinToString { it.id },
        )

        // 两次世界大战时期的代表人物不得是战后人物（v2.1.0 已修正归属）
        val wwPeriod = dataset.periods.find { it.id == "w-world-wars" }
        assertTrue(wwPeriod != null, "缺少 w-world-wars 时期")
        val wwNames = wwPeriod!!.keyFigures.mapNotNull { fid ->
            dataset.figures.find { it.id == fid }?.name
        }
        listOf("屠呦呦", "加加林", "奥尔德林", "曼德拉").forEach { bad ->
            assertTrue(
                wwNames.none { it.contains(bad) },
                "两次世界大战时期不应含战后人物: " + bad,
            )
        }

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
