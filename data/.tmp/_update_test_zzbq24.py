# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.4.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v2.4.0：地区错挂第二批修复 + 中国近现代人物归位
        // 地区时期不得出现完全跨文化的人物
        val regionMustNot = mapOf(
            "w-old-world" to listOf("姜子牙"),
            "w-korea" to listOf("冒顿"),
            "w-near-east-persian" to listOf("索福克勒斯", "伯里克利", "希罗多德"),
            "w-modern-south-asia" to listOf("维多利亚"),
        )
        regionMustNot.forEach { (pid, forbidden) ->
            val period = dataset.periods.find { it.id == pid }
            if (period != null) {
                val names = period.keyFigures.mapNotNull { fid ->
                    dataset.figures.find { it.id == fid }?.name
                }
                forbidden.forEach { bad ->
                    assertTrue(
                        names.none { it.contains(bad) },
                        "地区时期 $pid 仍含错挂人物: " + bad,
                    )
                }
            }
        }

        // 中国近现代人物必须按政治生涯归位，不能全挤在「清后期」
        fun periodOf(name: String): String? =
            dataset.figures.find { it.name.contains(name) }?.periodId
        assertTrue(periodOf("毛泽东") == "cn-prc-early", "毛泽东归属错误: " + periodOf("毛泽东"))
        assertTrue(periodOf("周恩来") == "cn-prc-early", "周恩来归属错误: " + periodOf("周恩来"))
        assertTrue(periodOf("邓小平") == "cn-prc-reform", "邓小平归属错误: " + periodOf("邓小平"))
        assertTrue(periodOf("宋教仁") == "cn-modern-republic", "宋教仁归属错误: " + periodOf("宋教仁"))

        // 清后期时期的人物不得是共和国时期人物
        val qingLate = dataset.periods.find { it.id == "cn-qing-late" }
        assertTrue(qingLate != null, "缺少 cn-qing-late")
        val qingNames = qingLate!!.keyFigures.mapNotNull { fid ->
            dataset.figures.find { it.id == fid }?.name
        }
        listOf("毛泽东", "周恩来", "邓小平", "刘少奇", "彭德怀").forEach { bad ->
            assertTrue(
                qingNames.none { it.contains(bad) },
                "清后期时期不应含共和国人物: " + bad,
            )
        }

        // 中华人民共和国时期代表人物应含开国领袖
        val prcEarly = dataset.periods.find { it.id == "cn-prc-early" }
        assertTrue(prcEarly != null, "缺少 cn-prc-early")
        val prcNames = prcEarly!!.keyFigures.mapNotNull { fid ->
            dataset.figures.find { it.id == fid }?.name
        }
        assertTrue(
            prcNames.any { it.contains("毛泽东") || it.contains("周恩来") },
            "共和国建设时期代表人物不合理: " + prcNames,
        )

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
