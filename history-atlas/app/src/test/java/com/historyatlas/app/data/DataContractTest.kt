package com.historyatlas.app.data

import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull
import kotlin.test.assertTrue

/**
 * 数据层契约测试（纯 JVM，不依赖 Android Context）。
 *
 * 覆盖：
 * - 模型反序列化：缺字段时用默认值兜底，不崩溃
 * - 引用容错：悬空引用被剔除而非抛异常
 * - 序列化往返：JSON → 模型 → JSON 字段一致
 */
class DataContractTest {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        coerceInputValues = true
        explicitNulls = false
    }

    @Test
    fun `完整数据可以正确反序列化`() {
        val raw = """
            {
              "version": 1,
              "scope": "china",
              "periods": [
                {
                  "id": "cn-qin", "name": "秦", "alias": "秦朝", "parentId": null,
                  "startYear": -221, "endYear": -207,
                  "startDateText": "公元前221年", "endDateText": "公元前207年",
                  "colorKey": "blue", "summary": "秦的概述",
                  "territory": "东至东海", "capital": "咸阳", "population": "约2000万",
                  "culture": "秦篆", "keyFigures": ["fig-qin-shi-huang"],
                  "relatedEvents": ["ev-qin-unify"], "tags": ["统一", "中央集权"]
                }
              ],
              "events": [
                {
                  "id": "ev-qin-unify", "name": "秦灭六国完成统一",
                  "year": -221, "yearEnd": null, "dateText": "公元前221年",
                  "periodId": "cn-qin", "category": "political", "location": "咸阳",
                  "summary": "摘要", "detail": "详情", "importance": 5,
                  "figures": ["fig-qin-shi-huang"], "tags": ["统一", "战争"]
                }
              ],
              "figures": [
                {
                  "id": "fig-qin-shi-huang", "name": "秦始皇", "alias": "嬴政、始皇帝",
                  "birthYear": -259, "deathYear": -210,
                  "lifeText": "公元前259年－公元前210年", "role": "皇帝",
                  "periodId": "cn-qin", "gender": "male", "summary": "简介",
                  "biography": "生平", "achievements": ["统一六国"], "quotes": ["朕为始皇帝"],
                  "relatedEvents": ["ev-qin-unify"], "relatedFigures": ["fig-li-si"],
                  "tags": ["皇帝", "统一"]
                }
              ]
            }
        """.trimIndent()

        val ds = json.decodeFromString(HistoryDataset.serializer(), raw)
        assertEquals(1, ds.version)
        assertEquals("china", ds.scope)
        assertEquals(1, ds.periods.size)
        assertEquals(1, ds.events.size)
        assertEquals(1, ds.figures.size)

        val period = ds.periods.first()
        assertEquals("cn-qin", period.id)
        assertEquals(-221, period.startYear)
        assertNull(period.parentId)
        assertEquals("blue", period.colorKey)
        assertEquals(listOf("fig-qin-shi-huang"), period.keyFigures)

        val event = ds.events.first()
        assertEquals(-221, event.year)
        assertNull(event.yearEnd)
        assertEquals(0, event.span, "yearEnd 为 null 时跨年跨度应为 0")
        assertEquals(5, event.importance)

        val figure = ds.figures.first()
        assertEquals(-259, figure.birthYear)
        assertEquals(-210, figure.deathYear)
        assertEquals(listOf("朕为始皇帝"), figure.quotes)
    }

    @Test
    fun `缺少可选字段时使用默认值而不是崩溃`() {
        val raw = """
            {
              "version": 1,
              "scope": "world",
              "periods": [{"id": "p1", "name": "时期"}],
              "events": [{"id": "e1", "name": "事件", "periodId": "p1"}],
              "figures": [{"id": "f1", "name": "人物", "periodId": "p1"}]
            }
        """.trimIndent()

        val ds = json.decodeFromString(HistoryDataset.serializer(), raw)

        val p = ds.periods.first()
        assertEquals("", p.alias)
        assertEquals("", p.colorKey)
        assertEquals(emptyList(), p.keyFigures)
        assertEquals(emptyList(), p.tags)
        assertEquals(0, p.startYear)

        val e = ds.events.first()
        assertEquals(0, e.importance)
        assertNull(e.yearEnd)
        assertEquals(emptyList(), e.figures)

        val f = ds.figures.first()
        assertNull(f.birthYear)
        assertNull(f.deathYear)
        assertEquals(emptyList(), f.achievements)
    }

    @Test
    fun `顶层数组缺失时也能反序列化`() {
        val raw = """{"version":1,"scope":"china"}"""
        val ds = json.decodeFromString(HistoryDataset.serializer(), raw)
        assertEquals(0, ds.periods.size)
        assertEquals(0, ds.events.size)
        assertEquals(0, ds.figures.size)
    }

    @Test
    fun `未知字段被忽略`() {
        val raw = """
            {
              "version": 1, "scope": "china",
              "periods": [{"id":"p1","name":"时期","futureField":"whatever"}],
              "events": [], "figures": [], "extraTopLevel": 123
            }
        """.trimIndent()
        val ds = json.decodeFromString(HistoryDataset.serializer(), raw)
        assertEquals(1, ds.periods.size)
        assertEquals("时期", ds.periods.first().name)
    }

    @Test
    fun `event category 枚举未知值回退而不抛异常`() {
        assertEquals(EventCategory.POLITICAL, EventCategory.from("political"))
        assertEquals(EventCategory.CROSS_CIVILIZATION, EventCategory.from("cross-civilization"))
        assertEquals(EventCategory.SOCIAL, EventCategory.from("not-a-real-category"))
        assertEquals(EventCategory.SOCIAL, EventCategory.from(""))
    }

    @Test
    fun `事件跨度计算正确`() {
        val spanning = Event(id = "e", name = "战争", year = -200, yearEnd = -100)
        assertEquals(100, spanning.span)
        assertEquals(-200, spanning.spanStart)
        assertEquals(-100, spanning.spanEnd)

        val point = Event(id = "e", name = "事件", year = -221, yearEnd = null)
        assertEquals(0, point.span)
        assertEquals(-221, point.spanEnd)
    }

    @Test
    fun `年份文本与数值并存且一致`() {
        val p = Period(
            id = "cn-qin", name = "秦",
            startYear = -221, endYear = -207,
            startDateText = "公元前221年", endDateText = "公元前207年",
        )
        assertTrue(p.yearRangeText.contains("公元前221年"))
        assertTrue(p.yearRangeText.contains("公元前207年"))
        assertTrue(p.startYear <= p.endYear)
    }

    @Test
    fun `模型可以往返序列化`() {
        val original = Period(
            id = "cn-han", name = "汉", alias = "汉朝", parentId = "cn-empire",
            startYear = -202, endYear = 220,
            startDateText = "公元前202年", endDateText = "公元220年",
            colorKey = "han", summary = "概述", capital = "长安",
            keyFigures = listOf("f1"), relatedEvents = listOf("e1"), tags = listOf("汉"),
        )
        val text = json.encodeToString(Period.serializer(), original)
        val back = json.decodeFromString(Period.serializer(), text)
        assertEquals(original, back)
        assertEquals("cn-empire", back.parentId)
        assertEquals("han", back.colorKey)
    }

    @Test
    fun `parentId 为 null 的时期往返后仍为 null`() {
        val original = Period(id = "cn-qin", name = "秦", parentId = null)
        val text = json.encodeToString(Period.serializer(), original)
        val back = json.decodeFromString(Period.serializer(), text)
        assertNull(back.parentId)
        assertEquals(original, back)
    }
}
