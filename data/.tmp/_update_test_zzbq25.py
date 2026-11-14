# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.5.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

# 找到中国史测试方法的末尾插入断言
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
insert_at = j

BLOCK = '''
        // v2.5.0：三国人物归位 + 宋辽归属修复
        fun periodOf(name: String): String? =
            dataset.figures.find { it.name.contains(name) }?.periodId

        // 三国核心人物必须归入三国子时期，不得全挤在东汉
        listOf("曹操", "刘备", "孙权", "诸葛亮", "关羽", "周瑜").forEach { name ->
            val pid = periodOf(name)
            assertTrue(
                pid != null && pid.startsWith("cn-three"),
                "三国人物 $name 归属错误: " + pid,
            )
        }

        // 宋太祖、宋太宗不得挂在辽朝下
        listOf("赵匡胤", "赵炅").forEach { name ->
            val pid = periodOf(name)
            assertTrue(
                pid == "cn-song-north",
                "宋朝开国人物 $name 归属错误: " + pid,
            )
        }

        // 东汉时期人物数应因三国人物迁出而下降（原 54 人）
        val hanEastCount = dataset.figures.count { it.periodId == "cn-han-east" }
        assertTrue(
            hanEastCount < 45,
            "东汉时期人物仍然过多（三国人物未迁出）: " + hanEastCount,
        )

        // 三国时期必须有代表人物
        val threeKingdoms = dataset.periods.find { it.id == "cn-three-kingdoms" }
        assertTrue(threeKingdoms != null, "缺少 cn-three-kingdoms")
        assertTrue(
            threeKingdoms!!.keyFigures.isNotEmpty(),
            "三国时期缺代表人物",
        )

'''

s = s[:insert_at] + BLOCK + s[insert_at:]
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
