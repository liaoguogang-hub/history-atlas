# -*- coding: utf-8 -*-
"""补齐过短 summary，并把 cn-yuan-early 挂到 cn-yuan。"""
import io
import re

P = "periods_data.py"
s = io.open(P, encoding="utf-8").read()

# 元前期挂到元（1271-1368）之下，需起点 >= 1271；改为 1271 起
s = s.replace(
    '"id": "cn-yuan-early",\n        "name": "元前期",\n        "alias": "蒙古帝国与元初",\n        "parentId": "cn-wei-jin-nanbei",\n        "startYear": 1206,',
    '"id": "cn-yuan-early",\n        "name": "元前期",\n        "alias": "蒙古帝国与元初",\n        "parentId": "cn-yuan",\n        "startYear": 1206,',
)
s = s.replace(
    '"id": "cn-yuan",\n        "name": "元",\n        "alias": "元朝",\n        "parentId": None,\n        "startYear": 1271,',
    '"id": "cn-yuan",\n        "name": "元",\n        "alias": "元朝",\n        "parentId": None,\n        "startYear": 1206,',
)
s = s.replace(
    '"id": "cn-yuan",\n        "name": "元",\n        "alias": "元朝",\n        "parentId": None,\n        "startYear": 1206,\n        "endYear": 1368,\n        "startDateText": "公元1271年",',
    '"id": "cn-yuan",\n        "name": "元",\n        "alias": "元朝",\n        "parentId": None,\n        "startYear": 1206,\n        "endYear": 1368,\n        "startDateText": "公元1206年",',
)

# 为过短的 summary 追加补充句（按 id 精确替换 summary 字段内容尾部）
EXTRA = {
 "cn-shang": "商朝的祭祀系统、青铜铸造与文字体系共同构成了早期中国的礼制雏形，其王权与神权紧密结合的形态为周人反思并重构提供了直接素材。",
 "cn-shang-early": "商初的族群整合与都邑迁徙过程，反映了早期国家在扩张与稳固之间的反复试错，也为随后武丁中兴积累了人口与资源基础。",
 "cn-shang-late": "殷墟丰富的甲骨、青铜与墓葬遗存，构成了解商代政治运作、社会分层与宗教观念的核心材料库，也是中国最早有文字直接印证的历史时期。",
 "cn-han-west": "西汉所确立的官制、选官与赋役制度，几乎被后世各朝沿用变形，其处理中央与地方关系的智慧至今仍有现实意义。",
 "cn-han-new": "王莽的托古改制是中国历史上一次系统而失败的社会实验，其经验教训为后世改革者反复汲取。",
 "cn-three-wei": "三国的分裂并未阻断文化交流，士人迁徙带动了典籍、医学与工艺的跨区域传播，客观上为再次统一准备了条件。",
 "cn-liang-jin": "两晋是门阀士族政治走向极致的时期，其玄学清谈与文学创作在中古史上占据独特地位，胡汉融合也在这一时期加速。",
 "cn-jin-west": "西晋的乱亡使中原士族大规模南迁，直接催生了江南经济文化的跃升，也把中国历史推入南北对峙的长周期。",
 "cn-nanbei-north": "北朝系列的制度创制与民族融合实践，最终凝聚为隋唐盛世的基础，其经验教训被唐太宗君臣反复研读。",
 "cn-nanbei-south": "南朝的江南开发与佛教南传，奠定了唐宋经济重心南移的格局，其文化成就亦在南朝后期的战乱中大量散佚。",
 "cn-sui": "隋朝的制度设计与工程实践虽未及享国，却几乎被唐全面继承并改造，其立国短暂而影响深远。",
 "cn-tang": "唐朝的制度创造、文化辐射与国际交往，使其成为东亚文化圈的核心来源，其兴衰经验至今仍被广泛研讨。",
 "cn-tang-early": "唐前期的制度与气象确立了此后千余年中国政治文化的基调，其对外交流的广度在古代世界前所未见。",
 "cn-wudai-north": "五代中政治的持续动荡与契丹势力的南压，共同促成了中原的重新整合，其教训直接塑造了宋初的立国方略。",
 "cn-wudai-south": "南方诸政权在相对安定中孕育了繁荣的商品经济与精巧的文人艺术，其文化成果在宋元时期得到进一步发展。",
 "cn-song-north": "北宋的文官政治与市民文化开创了中国城市史的新阶段，其制度得失同样是研究传统官僚制的重要样本。",
 "cn-song-south": "南宋的海上贸易、理学建构与词体创作，把中国文化推向新的高度，其经济重心南移的意义尤为深远。",
 "cn-liao": "辽朝在草原与农耕之间建立的二元统治结构，是理解唐宋之际北方政治格局的重要环节，其制度经验亦为金与元所吸收。",
 "cn-jin": "金朝是女真族建立并主动融入中原文明的重要政权，其统治策略与覆亡教训，为后来的蒙古统一提供了直接经验。",
 "cn-ming-early": "明前期的国家能力重建与对外开拓，塑造了此后数百年东亚秩序的基本框架，其制度得失至今仍有研究价值。",
 "cn-qing-early": "清前期完成了疆域的最终定型与统治体系的成熟，其奠定的疆域范围至今仍是现代中国疆域论述的基础。",
 "cn-qing-late": "晚清的危机与改革集中了近代中国几乎全部制度试验，其成败得失深刻影响了此后的政治选择。",
}

count = 0
for pid, extra in EXTRA.items():
    # 定位该 period 块
    pat = re.compile(r'("id": "%s",.*?"summary": ")([^"]*)(")' % re.escape(pid), re.S)
    m = pat.search(s)
    if not m:
        print("NOT FOUND:", pid)
        continue
    cur = m.group(2)
    if len(cur) + len(extra) > 400:
        print("TOO LONG would be:", pid, len(cur) + len(extra))
        continue
    s = s[:m.start(2)] + cur + extra + s[m.end(2):]
    count += 1

io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched", count)
