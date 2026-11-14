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

        assertTrue(dataset.periods.size >= 95, "世界史时期数异常: ${dataset.periods.size}")
        assertTrue(dataset.events.size >= 446, "世界史事件数低于预期: ${dataset.events.size}")
        assertTrue(dataset.figures.size >= 354, "世界史人物数低于预期: ${dataset.figures.size}")

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
        listOf("亚述", "旧石器时代", "香料群岛", "库克船长", "拜占庭晚期").forEach { name ->
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

        // v1.7.0：新增南亚/东南亚编年时期 + 修畸形 id
        listOf("笈多王朝", "德里苏丹国", "莫卧儿帝国", "泰姬陵",
               "室利佛逝", "婆罗浮屠", "马六甲").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: $name")
        }
        // 事件名不得是英文空壳（backfill 兜底生成的 jin taikang 之类）
        val shellLike = dataset.events.filter { e ->
            Regex("[a-zA-Z]{3,}").containsMatchIn(e.name)
        }
        assertTrue(
            shellLike.isEmpty(),
            "存在英文空壳事件名: " + shellLike.joinToString { it.id + "=" + it.name },
        )

        // v1.9.0：西方思想史链条 + 跨 scope 冲突归零
        listOf(
            "经院哲学", "宗教改革", "启蒙运动", "德国古典哲学",
        ).forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "世界史缺少事件: " + name)
        }
        listOf(
            "奥古斯丁", "阿奎那", "但丁", "马基雅维利", "洛克",
            "亚当·斯密", "黑格尔", "尼采", "韦伯", "维特根斯坦",
        ).forEach { name ->
            assertTrue(figureNames.any { it.contains(name) }, "世界史缺少人物: " + name)
        }

        // 世界史不得再包含中国史错挂条目（这些属于中国史 scope）
        listOf("五四运动与新文化运动的影响", "长征与遵义会议", "延安整风与延安精神")
            .forEach { name ->
                assertTrue(
                    eventNames.none { it.contains(name) },
                    "世界史仍含中国史错挂条目: " + name,
                )
            }

        // v2.0.0：区域时期新建成 + 中东/南亚/非洲/美洲/东亚补强
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

        // v2.1.0：古代文明 + 中世纪 + 冷战人物补强，keyFigures 全面回填
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

        // v2.2.0：人物去重 + 父时期代表人物汇总
        // 同一历史人物不得以不同译名重复出现
        val dupNames = dataset.figures
            .groupBy { it.name.replace(Regex("[·・\\-—()（）：:]"), "") }
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

        // v2.3.0：地区错挂修复 + 拉丁美洲补强
        // 地区专题时期不得混入其他大洲的人物
        val regionForbidden = mapOf(
            "w-southeast-asia" to listOf("黑格尔", "惠灵顿", "威伯福斯", "玻利瓦尔", "圣马丁"),
            "w-modern-south-asia" to listOf("胡志明", "董必武", "陈云", "鲍林", "冯·诺依曼", "铁托"),
        )
        regionForbidden.forEach { (pid, forbidden) ->
            val period = dataset.periods.find { it.id == pid }
            if (period != null) {
                val names = period.keyFigures.mapNotNull { fid ->
                    dataset.figures.find { it.id == fid }?.name
                }
                forbidden.forEach { bad ->
                    assertTrue(
                        names.none { it.contains(bad) },
                        "地区时期 $pid 混入了不相干人物: " + bad,
                    )
                }
            }
        }

        // 拉丁美洲必须有实质内容（曾长期是 0 人物的空容器）
        val latin = dataset.periods.find { it.id == "w-latin-america" }
        assertTrue(latin != null, "缺少 w-latin-america")
        assertTrue(
            latin!!.keyFigures.size >= 5,
            "拉丁美洲代表人物过少: " + latin.keyFigures.size,
        )
        listOf("玻利瓦尔", "圣马丁", "庇隆", "瓦加斯", "卡德纳斯", "阿连德", "查韦斯")
            .forEach { name ->
                assertTrue(figureNames.any { it.contains(name) }, "拉美缺少人物: " + name)
            }
        listOf("拉丁美洲独立", "民粹主义", "民主化").forEach { name ->
            assertTrue(eventNames.any { it.contains(name) }, "拉美缺少事件: " + name)
        }

        // 东南亚应有真实的本地区人物
        val sea = dataset.periods.find { it.id == "w-southeast-asia" }
        if (sea != null) {
            val seaNames = sea.keyFigures.mapNotNull { fid ->
                dataset.figures.find { it.id == fid }?.name
            }
            assertTrue(
                seaNames.any { it.contains("那莱") || it.contains("库恩") },
                "东南亚代表人物不合理: " + seaNames,
            )
        }

        // v2.4.0：地区错挂第二批修复 + 中国近现代人物归位
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

        // 畸形 id 必须已修正
        val figureIds = dataset.figures.map { it.id }
        assertTrue(figureIds.none { it == "fig-sherlock-plo" }, "畸形 id fig-sherlock-plo 未修复")
        assertTrue(figureIds.none { it == "fig-o-kongo" }, "畸形 id fig-o-kongo 未修复")
        assertTrue(figureIds.any { it == "fig-xerxes" }, "缺少 fig-xerxes")
        assertTrue(figureIds.any { it == "fig-oda-nobunaga" }, "缺少 fig-oda-nobunaga")
    }

    @Test
    fun `打包的中国史数据可被完整解析且新补充条目未丢失`() {
        val dataset = loadChina()

        // 基础规模
        assertTrue(dataset.periods.size >= 60, "时期数异常: ${dataset.periods.size}")
        assertTrue(dataset.events.size >= 415, "事件数低于预期: ${dataset.events.size}")
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


        // v2.5.0：三国人物归位 + 宋辽归属修复

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

}
}
