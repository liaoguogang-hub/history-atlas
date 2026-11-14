# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.6.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

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
        // v2.6.0：卒年回填 + 当代人物归期 + 重复合并
        // 帝号人物必须只有一个条目（不得同时存在本名与帝号两条）
        listOf("康熙", "乾隆", "梁武帝", "柳宗元").forEach { name ->
            val matches = dataset.figures.filter { it.name.contains(name) }
            assertTrue(
                matches.size <= 1,
                "重复人物未合并: " + name + " -> " + matches.map { it.id },
            )
        }

        // 已合并的冗余 id 不得残留
        listOf(
            "fig-xiao-yan", "fig-kangxi", "fig-qianlong", "fig-liu-zongyuan",
        ).forEach { gone ->
            assertTrue(
                dataset.figures.none { it.id == gone },
                "冗余人物未删除: " + gone,
            )
        }

        // 当代领导人必须归入正确时期
        fun periodOfName(name: String): String? =
            dataset.figures.find { it.name.contains(name) }?.periodId
        listOf(
            "习近平" to "cn-prc-new-era",
            "李克强" to "cn-prc-new-era",
            "胡锦涛" to "cn-prc-reform",
            "温家宝" to "cn-prc-reform",
        ).forEach { (name, expected) ->
            assertTrue(
                periodOfName(name) == expected,
                "当代人物 $name 归属错误: " + periodOfName(name),
            )
        }

        // 有明确 lifeText 的历史人物必须有卒年（不能再被误清空）
        listOf("康熙帝" to 1722, "乾隆帝" to 1799, "张献忠" to 1647)
            .forEach { (name, year) ->
                val f = dataset.figures.find { it.name.contains(name) }
                assertTrue(f != null, "缺少人物: " + name)
                assertTrue(
                    f!!.deathYear == year,
                    "$name 卒年错误: " + f.deathYear + "（应为 $year）",
                )
            }

        // 新中国历史人物（如张良、霍去病）的公元前卒年必须为负数
        val zhangLiang = dataset.figures.find { it.name.contains("张良") }
        if (zhangLiang != null) {
            assertTrue(
                zhangLiang.deathYear != null && zhangLiang.deathYear!! < 0,
                "张良卒年应为公元前（负数）: " + zhangLiang.deathYear,
            )
        }

'''

s = s[:j] + BLOCK + s[j:]
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
