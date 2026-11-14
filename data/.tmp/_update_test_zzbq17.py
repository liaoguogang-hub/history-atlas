# -*- coding: utf-8 -*-
"""更新 RealDataIntegrityTest 至 v2.0.0。"""
import io
import sys

sys.stdout.reconfigure(encoding="utf-8")

p = "history-atlas/app/src/test/java/com/historyatlas/app/data/RealDataIntegrityTest.kt"
s = io.open(p, encoding="utf-8").read()

s = s.replace('dataset.periods.size >= 85', 'dataset.periods.size >= 95')
s = s.replace('dataset.periods.size >= 92', 'dataset.periods.size >= 95')
s = s.replace('dataset.events.size >= 434', 'dataset.events.size >= 441')
s = s.replace('dataset.figures.size >= 283', 'dataset.figures.size >= 327')

MARKER = "        // 畸形 id 必须已修正"
assert MARKER in s, "锚点未找到"

BLOCK = '''        // v2.0.0：区域时期新建成 + 中东/南亚/非洲/美洲/东亚补强
        listOf(
            "阿拔斯革命", "智慧宫", "十字军东征", "奥斯曼帝国", "莫卧儿帝国",
            "笈多王朝", "德里苏丹国", "马拉塔", "印度独立",
            "黄金贸易", "桑海", "阿克苏姆", "拉利贝拉", "埃塞俄比亚",
            "玛雅古典期", "阿兹特克帝国", "印加帝国", "拉丁美洲独立",
            "大化改新", "战国时代的统一", "训民正音", "吴哥", "库克船长", "暹罗",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: " + name)
        }
        listOf(
            "哈伦·拉希德", "马蒙", "肯迪", "阿尔法拉比", "拉齐",
            "沙摩陀罗笈多", "迦梨陀娑", "希瓦吉", "奥朗则布", "泰戈尔",
            "阿姆倍伽尔", "真纳",
            "桑尼·阿里", "阿斯基亚", "埃扎纳", "拉利贝拉", "孟尼利克", "海尔·塞拉西",
            "帕卡尔", "蒙特祖玛一世", "瓦伊纳·卡帕克", "拉斯·卡萨斯", "杜桑", "圣马丁",
            "中臣镰足", "阇耶跋摩七世", "苏利耶跋摩二世", "库克", "朱拉隆功",
            "福泽谕吉", "明治天皇", "许筠", "苏加诺",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: " + name)
        }

        // 新建的 4 个区域时期必须存在
        val periodIds = dataset.periods.map { it.id }
        listOf(
            "w-modern-south-asia", "w-latin-america",
            "w-modern-africa", "w-modern-southeast-asia",
        ).forEach { pid ->
            assertTrue(periodIds.contains(pid), "缺少时期: " + pid)
        }

        // 跨文明时期不得再是零人物（v2.0.0 已补 keyFigures）
        dataset.periods
            .filter { it.id.startsWith("w-cc-") }
            .forEach { p ->
                assertTrue(
                    p.keyFigures.isNotEmpty(),
                    "跨文明子时期缺 keyFigures: " + p.id,
                )
            }

'''

s = s.replace(MARKER, BLOCK + MARKER, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("测试已更新")
