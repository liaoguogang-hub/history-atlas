package com.scienceatlas.app.data

import kotlinx.serialization.json.Json
import java.io.File
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

/**
 * 真实数据文件的反序列化测试（纯 JVM）。
 *
 * 存在的理由：**单元测试只喂构造好的小样本，抓不到真实数据里的取值越界**。
 *
 * 曾经踩过的坑：地理数据的「地质年代」用 `-4600000000`（约 46 亿年前）表示起始年，
 * 超出 Int 下限。当时模型里 `startYear` 是 Int，`kotlinx.serialization` 直接抛
 * `JsonDecodingException`，而 App 层对解析失败是**静默兜底**的——
 * 结果就是地理学科在首页显示「0 分期 / 0 事件 / 0 人物」，
 * 且不崩溃、不报错，很难定位。
 *
 * 这个测试直接把仓库里的真实 JSON 喂给反序列化器，
 * 任何取值越界、字段改名、格式漂移都会在这里立刻暴露。
 */
class RealDataDeserializationTest {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        explicitNulls = false
    }

    private fun dataDir(): File {
        // 测试的工作目录是 app/，数据在仓库根的 data-science/
        val candidates = listOf(
            File("../../data-science"),
            File("../data-science"),
            File("data-science"),
        )
        return candidates.firstOrNull { it.isDirectory }
            ?: error("找不到 data-science 目录，已尝试：${candidates.map { it.absolutePath }}")
    }

    private fun load(name: String): ScienceDataset {
        val f = File(dataDir(), name)
        assertTrue(f.isFile, "数据文件不存在：${f.absolutePath}")
        return json.decodeFromString(ScienceDataset.serializer(), f.readText())
    }

    @Test
    fun `四个学科的真实数据都能反序列化`() {
        listOf("geo.json", "astro.json", "physics.json", "chem.json").forEach { name ->
            val ds = load(name)
            assertTrue(ds.periods.isNotEmpty(), "$name 没有分期")
            assertTrue(ds.events.isNotEmpty(), "$name 没有事件")
            assertTrue(ds.figures.isNotEmpty(), "$name 没有科学家")
        }
    }

    @Test
    fun `地质深时的年份不溢出`() {
        // 约 46 亿年前 = -4600000000，超出 Int 下限。
        // 这条数据是真实存在的，模型必须能接住。
        val geo = load("geo.json")
        val deepTime = geo.periods.filter { it.startYear < -2_147_483_648L }
        assertTrue(
            deepTime.isNotEmpty(),
            "geo.json 里应当有地质深时分期（startYear < Int 下限），用于验证 Long 年份",
        )
        // 所有年份都必须落在 Long 的安全范围内
        geo.periods.forEach { p ->
            assertTrue(p.startYear >= Long.MIN_VALUE / 2 && p.endYear <= Long.MAX_VALUE / 2)
            assertTrue(p.startYear <= p.endYear, "${p.name} 的起止年份顺序颠倒")
        }
        geo.events.forEach { e ->
            e.yearEnd?.let {
                assertTrue(e.year <= it, "${e.name} 的 yearEnd 早于 year")
            }
        }
    }

    @Test
    fun `真实数据没有悬空引用`() {
        listOf("geo.json", "astro.json", "physics.json", "chem.json").forEach { name ->
            val ds = load(name)
            val periodIds = ds.periods.map { it.id }.toSet()
            val figureIds = ds.figures.map { it.id }.toSet()
            val eventIds = ds.events.map { it.id }.toSet()

            ds.events.forEach { e ->
                assertTrue(e.periodId in periodIds, "${e.id} 的 periodId 悬空：${e.periodId}")
                e.figures.forEach { fid ->
                    assertTrue(fid in figureIds, "${e.id} 引用了不存在的人物：$fid")
                }
            }
            ds.figures.forEach { f ->
                assertTrue(f.periodId in periodIds, "${f.id} 的 periodId 悬空：${f.periodId}")
                f.relatedEvents.forEach { eid ->
                    assertTrue(eid in eventIds, "${f.id} 引用了不存在的事件：$eid")
                }
                f.relatedFigures.forEach { fid ->
                    assertTrue(fid in figureIds, "${f.id} 引用了不存在的人物：$fid")
                }
            }
            ds.periods.forEach { p ->
                assertTrue(p.parentId == null || p.parentId in periodIds, "${p.id} 的 parentId 悬空")
                p.keyFigures.forEach { fid ->
                    assertTrue(fid in figureIds, "${p.id} 引用了不存在的人物：$fid")
                }
                p.relatedEvents.forEach { eid ->
                    assertTrue(eid in eventIds, "${p.id} 引用了不存在的事件：$eid")
                }
            }
        }
    }

    @Test
    fun `真实数据的 scope 与文件名一致`() {
        assertEquals("geo", load("geo.json").scope)
        assertEquals("astro", load("astro.json").scope)
        assertEquals("physics", load("physics.json").scope)
        assertEquals("chem", load("chem.json").scope)
    }

    @Test
    fun `真实数据的 id 全局唯一`() {
        listOf("geo.json", "astro.json", "physics.json", "chem.json").forEach { name ->
            val ds = load(name)
            val all = ds.periods.map { it.id } + ds.events.map { it.id } + ds.figures.map { it.id }
            assertEquals(all.size, all.toSet().size, "$name 里存在重复 id")
        }
    }

    @Test
    fun `顶层分期都带编年主干标签`() {
        // 「编年主干」是 App 判定主干分组的显式信号，
        // 顶层分期漏标会让它被区间重叠规则误判成专题而藏起来。
        listOf("geo.json", "astro.json", "physics.json", "chem.json").forEach { name ->
            val ds = load(name)
            val tops = ds.periods.filter { it.parentId == null }
            assertTrue(tops.isNotEmpty(), "$name 没有顶层分期")
            tops.forEach { p ->
                assertTrue(
                    p.tags.any { it.contains("编年主干") },
                    "$name 的顶层分期「${p.name}」缺少「编年主干」标签",
                )
            }
        }
    }

    @Test
    fun `真实数据的事件分类都在枚举内`() {
        listOf("geo.json", "astro.json", "physics.json", "chem.json").forEach { name ->
            val ds = load(name)
            ds.events.forEach { e ->
                assertTrue(
                    e.category in VALID_CATEGORIES,
                    "$name 的事件「${e.name}」分类非法：${e.category}",
                )
                assertTrue(e.importance in 1..5, "$name 的事件「${e.name}」重要度越界")
            }
        }
    }

    private companion object {
        val VALID_CATEGORIES = setOf(
            "political", "military", "economic", "cultural", "scientific", "social",
            "religious", "art", "literature", "education", "technology", "exploration",
            "conflict", "treaty", "reform", "dynasty", "cross-civilization",
            "disaster", "health", "economy-crisis", "legend", "archaeology",
        )
    }
}
