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
