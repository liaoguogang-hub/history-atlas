package com.historyatlas.app.data

import java.io.File
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * 真实数据文件的解析完整性测试。
 *
 * 用与 [HistoryRepository] 完全一致的 Json 配置直接解析
 * `src/main/assets/data/china.json`，确保打包进 APK 的数据
 * 在 App 的真实解析路径下不会被静默丢弃。
 */
class RealDataIntegrityTest {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        explicitNulls = false
    }

    private fun loadChina(): HistoryDataset {
        val candidates = listOf(
            File("src/main/assets/data/china.json"),
            File("app/src/main/assets/data/china.json"),
        )
        val file = candidates.firstOrNull { it.isFile }
            ?: error("找不到 assets/data/china.json")
        val text = file.readText(Charsets.UTF_8)
        return json.decodeFromString(HistoryDataset.serializer(), text)
    }

    private fun loadWorld(): HistoryDataset {
        val candidates = listOf(
            File("src/main/assets/data/world.json"),
            File("app/src/main/assets/data/world.json"),
        )
        val file = candidates.firstOrNull { it.isFile }
            ?: error("找不到 assets/data/world.json")
        val text = file.readText(Charsets.UTF_8)
        return json.decodeFromString(HistoryDataset.serializer(), text)
    }

    @Test
    fun `打包的世界史数据可被完整解析且新补充条目未丢失`() {
        val dataset = loadWorld()

        assertTrue(dataset.periods.size >= 85, "世界史时期数异常: ${dataset.periods.size}")
        assertTrue(dataset.events.size >= 430, "世界史事件数低于预期: ${dataset.events.size}")
        assertTrue(dataset.figures.size >= 271, "世界史人物数低于预期: ${dataset.figures.size}")

        val eventNames = dataset.events.map { it.name }
        val figureNames = dataset.figures.map { it.name }
        // 近代骨架：工业革命、帝国主义、两次大战、冷战、去殖民化、科技时代
        listOf(
            "瓦特", "工业革命", "铁路时代", "柏林会议", "帝国主义扩张",
            "第一次世界大战", "第二次世界大战", "纳粹大屠杀", "冷战",
            "古巴导弹危机", "柏林墙", "去殖民化", "甘地", "曼德拉",
            "电子计算机", "阿波罗登月", "双螺旋", "人工智能",
            "君士坦丁堡的陷落", "大宪章", "文艺复兴",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: $name")
        }
        listOf("史蒂芬孙", "希特勒", "曼德拉", "杜鲁门", "威尔逊", "达·芬奇", "乔布斯").forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: $name")
        }

        // v1.5.0：填空壳时期 + 重量级人物
        listOf("亚述", "旧石器时代", "商代青铜", "香料群岛", "库克船长", "拜占庭晚期").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: $name")
        }
        listOf(
            "拿破仑", "华盛顿", "玻利瓦尔", "爱因斯坦", "贝多芬", "巴赫", "莫扎特",
            "梵高", "毕加索", "歌德", "雨果", "陀思妥耶夫斯基", "弗洛伊德",
            "马丁·路德·金", "戈尔巴乔夫",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: $name")
        }

        // v1.6.0：非西方地区（美洲/非洲/东亚）
        listOf("阿兹特克", "印加", "马里帝国", "阿克苏姆", "吴哥", "日本战国",
               "训民正音", "莫卧儿", "圣德太子").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: $name")
        }
        listOf(
            "蒙特祖玛", "科尔特斯", "阿塔瓦尔帕", "皮萨罗", "松迪亚塔",
            "丰臣秀吉", "德川家康", "世宗", "李舜臣", "圣德太子",
            "巴布尔", "沙贾汗",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: $name")
        }
    }

    @Test
    fun `打包的中国史数据可被完整解析且新补充条目未丢失`() {
        val dataset = loadChina()

        // 基础规模
        assertTrue(dataset.periods.size >= 60, "时期数异常: ${dataset.periods.size}")
        assertTrue(dataset.events.size >= 426, "事件数低于预期: ${dataset.events.size}")
        assertTrue(dataset.figures.size >= 482, "人物数低于预期: ${dataset.figures.size}")

        // 第一批（春秋战国）补充必须存在
        val eventNames = dataset.events.map { it.name }
        val figureNames = dataset.figures.map { it.name }
        listOf("三家分晋", "胡服骑射").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "缺少事件: $name")
        }
        listOf("勾践", "蔺相如", "荆轲").forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "缺少人物: $name")
        }

        // 第二批（宋元明清与近现代）补充必须存在
        listOf("陈桥兵变", "红巾军起义", "靖难之役", "明末农民大起义", "义和团", "南昌起义", "长征", "遵义会议").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "缺少事件: $name")
        }
        listOf("张献忠", "康熙帝", "乾隆帝", "建文帝", "方孝孺", "刘福通", "慈禧太后", "光绪帝", "朱德", "叶剑英", "贺龙", "叶挺", "李大钊").forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "缺少人物: $name")
        }

        // 第三批（秦汉与汉匈关系）补充必须存在
        listOf("巨鹿之战", "卫青霍去病北击匈奴", "昭君出塞", "苏武牧羊", "弭兵之会").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "缺少事件: $name")
        }
        listOf("张良", "萧何", "范增", "卫青", "霍去病", "王昭君", "向戌").forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "缺少人物: $name")
        }

        // 第四批（科技发明、文物艺术、文学名著、制度经济）补充必须存在
        listOf(
            "火药的发明", "印刷术的发明", "指南针的发明", "本草纲目", "天工开物",
            "授时历", "农政全书", "梦溪笔谈", "都江堰", "赵州桥", "兵马俑",
            "敦煌", "龙门石窟", "青花瓷", "诗经", "四大名著", "宋词", "三省六部",
            "交子", "一条鞭法", "摊丁入亩", "军机处", "遣唐使", "马可·波罗",
            "利玛窦", "尼布楚条约",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "缺少事件: $name")
        }
        listOf("李冰", "李春", "曹雪芹", "罗贯中", "施耐庵", "吴承恩", "马可·波罗", "利玛窦").forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "缺少人物: $name")
        }
    }
}
