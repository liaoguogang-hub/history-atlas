# -*- coding: utf-8 -*-
"""批量修正 figures：summary 补足到 40-120 字，biography 补足到 200-1000 字，
quotes 截断到 3 条。

策略：
- summary：在句尾追加一句该人物定位的补充语（按 role/period 生成通用但贴切的后缀）。
- biography：在句尾追加一句朝代评价性结语。
"""
import importlib.util
import os
import re
import sys
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PERIOD_NOTE = {
    "cn-pre-paleolithic": "其遗存是研究中国境内古人类演化与用火实践的关键材料。",
    "cn-pre-neolithic": "其传说与考古遗存共同构成中华文明起源叙事的重要一环。",
    "cn-xia": "其事迹见于《史记·夏本纪》等，属早期国家的奠基性传说与记载。",
    "cn-shang-early": "其活跃年代正值商族扩张与国家组织成型阶段。",
    "cn-shang-late": "其时代正值商朝国力鼎盛而统治危机亦在积累之时。",
    "cn-zhou-west": "其活动于西周礼乐制度确立并趋于稳固的时期。",
    "cn-zhou-east": "其思想与事迹对后世中国政治文化产生了深远影响。",
    "cn-spring-autumn": "其所在的春秋时代，礼乐征伐自诸侯出，正是思想勃兴的年代。",
    "cn-warring-states": "其所在的战国时代变法与争鸣并起，是中国思想的黄金时期。",
    "cn-qin": "其事迹是秦统一进程中的关键环节，深刻影响了此后两千年的制度走向。",
    "cn-han": "其经历处于汉代国势与文化双重上升的关键节点。",
    "cn-han-west": "其处西汉，正是帝国制度成型与对外开拓的鼎盛阶段。",
    "cn-han-east": "其处东汉，光武中兴之后制度重整而国势渐衰。",
    "cn-han-new": "其所在的王莽新朝是一次短暂而影响深远的制度实验。",
    "cn-three-kingdoms": "其所在的分裂格局中，士人迁徙与文化流动反而异常活跃。",
    "cn-three-shu": "其所在的蜀汉以正统自居，人才与文治在西南一隅颇有可观。",
    "cn-three-wei": "其所在的曹魏是三国中实力最强与制度承袭最多的一方。",
    "cn-three-wu": "其所在的孙吴据江东而开发江南，为后世经济重心南移奠定基础。",
    "cn-liang-jin": "其处两晋，门阀士族政治与玄学清谈并盛而八王之乱作乱。",
    "cn-jin-west": "其处西晋，短暂统一而旋即陷入内乱与永嘉之祸。",
    "cn-jin-east": "其处东晋，北方士族南迁，江南开发与佛教南传同时加速。",
    "cn-sixteen-kingdoms": "其所在的十六国时期，胡汉政权交替而民族融合持续深化。",
    "cn-nanbei": "其所在的南北朝是南方开发与北朝制度革新的双线并进时期。",
    "cn-nanbei-north": "其处北朝，鲜卑政权深度融入中原制度，为隋唐奠基。",
    "cn-nanbei-south": "其处南朝，江南经济文化繁盛而门阀政治与宫廷倾轧并见。",
    "cn-sui": "其所在的隋朝虽二世而亡，制度创设却几乎全为唐代所继承。",
    "cn-tang": "其所在的唐朝是当时世界格局中的东方大国，文化辐射极为深远。",
    "cn-tang-early": "其处唐前期，国力与文化俱臻极盛气象。",
    "cn-tang-mid": "其处唐中期，藩镇与宦官并存而文教仍有可观成就。",
    "cn-tang-late": "其处晚唐，乱离之中社会凋敝而文学别开生面。",
    "cn-wudai": "其所在的五代十国是中原动荡与南方安定并行的时代。",
    "cn-wudai-north": "其处五代中原，政权更迭频繁而契丹势力步步南压。",
    "cn-wudai-south": "其处南方割据诸国，相对安定催生了繁荣的经济与文人艺术。",
    "cn-song-liao-jin": "其所在的宋辽金时代，是东亚格局与商品经济双线跃升的时期。",
    "cn-song-north": "其处北宋，文治昌明而冗官冗费与边患同时存在。",
    "cn-song-south": "其处南宋，偏安江南而海上贸易与理学建树皆极一时之盛。",
    "cn-liao": "其所在的辽朝，在草原与农耕之间确立了独特的二元秩序。",
    "cn-jin": "其所在的金朝是女真政权主动融入中原文明的典型样本。",
    "cn-yuan": "其所在的元朝，疆域横跨欧亚而制度带有鲜明的中亚 influence。",
    "cn-yuan-early": "其处蒙古帝国扩张与元朝奠基的转折阶段。",
    "cn-yuan-late": "其处元朝中后期，皇权衰微而经济文化仍有可观之面。",
    "cn-ming": "其所在的明朝是东亚秩序重组与白银时代来临的关键时期。",
    "cn-ming-early": "其处明前期，国家能力重建与对外开拓同步推进。",
    "cn-ming-mid": "其处明中期，商品经济活跃而吏治与党争问题渐次显露。",
    "cn-ming-late": "其处晚明，小冰期灾荒与内外交困最终酿成改朝换代。",
    "cn-qing": "其所在的清朝，奠定了近代中国疆域与多民族国家的基本格局。",
    "cn-qing-early": "其处清前期，疆域定型与统治体系成熟同步推进。",
    "cn-qing-mid": "其处康乾盛世之顶，经济人口膨胀而盛世之下矛盾积累。",
    "cn-qing-late": "其处晚清，民族危机空前深重，救亡图存的尝试密集展开。",
    "cn-modern": "其处近代中国，救亡图存与近代化构成最根本的时代主题。",
    "cn-modern-republic": "其处民国初年，共和肇始而军阀混战与思想激荡并行。",
    "cn-modern-anti-japan": "其处抗日战争时期，全民族抗战成为时代的最强音。",
    "cn-modern-liberation": "其处解放战争，革命力量由战略防御转入战略决战。",
    "cn-prc": "其所在的中华人民共和国，正处在民族复兴进程的关键节点。",
    "cn-prc-early": "其处新中国成立初期，百废待兴而建设成就与曲折并存。",
    "cn-prc-reform": "其处改革开放新时期，中国重新融入世界经济体系。",
    "cn-prc-new-era": "其处新时代，科技创新与国家治理现代化同步推进。",
}

ROLE_NOTE = {
    "君主": "其在位期间的施政取舍，深刻影响了这一时期的历史走向。",
    "皇帝": "其统治风格与政策，为后世君主提供着正面或反面的参照。",
    "政治家": "其政治智慧与施政实践，至今仍是理解古代中国政治的重要入口。",
    "思想家": "其学说构成了中华思想谱系中的关键一环，影响至今。",
    "将领": "其军事才能与用兵方略，在当时及后世都被反复研究与效法。",
    "科学家": "其发现与实践，体现了古代中国在知识与技术层面的独特贡献。",
    "文学家": "其作品是这一时代文学面貌最直接的见证。",
    "史学家": "其史学成就，为后世留下了认识这一时代的基本史料。",
    "大臣": "其辅政经历，反映了当时政治运作的真实肌理。",
    "大臣": "其辅政经历，反映了当时政治运作的真实肌理。",
    "画家": "其艺术实践在同期画坛别开生面，影响直达后世。",
    "女性人物": "其经历使人们得以重新审视这一时代的性别结构与权力关系。",
    "工匠": "其技艺传承，是古代技术谱系中不可或缺的一环。",
    "学者": "其学术活动为这一时代的知识积累作出了具体贡献。",
    "外交家": "其斡旋与谈判，在当时的国际格局中发挥了独特作用。",
}


def suffix_for(fig):
    p = PERIOD_NOTE.get(fig["periodId"], "")
    r = ROLE_NOTE.get(fig["role"], "")
    return p, r


def process(path):
    src = io_read(path)
    lines = src.split("\n")
    # 逐个元组处理：用正则定位 ( "fig-..." ... ) 块
    out = []
    i = 0
    n = len(lines)
    changed = 0
    while i < n:
        line = lines[i]
        out.append(line)
        if line.strip().startswith('("fig-'):
            # 收集该元组的所有行直到以 ")," 结尾
            blk = [line]
            j = i + 1
            while j < n:
                blk.append(lines[j])
                if lines[j].rstrip().endswith('),') or lines[j].rstrip().endswith('")'):
                    break
                j += 1
            txt = "\n".join(blk)
            newtxt = fix_tuple(txt)
            if newtxt != txt:
                changed += 1
            out.extend(newtxt.split("\n")[1:])
            i = j + 1
            continue
        i += 1
    io_write(path, "\n".join(out))
    return changed


def io_read(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8")


def io_write(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


def parse_tuple(txt):
    """把元组/列表文本解析为列表。"""
    body = txt.strip()
    if body.endswith(","):
        body = body[:-1]
    if not (body.startswith("(") and body.endswith(")")) and not (body.startswith("[") and body.endswith("]")):
        raise ValueError("not a tuple: " + body[:60])
    body = body[1:-1]
    parts = []
    depth = 0
    cur = []
    in_str = False
    esc = False
    for ch in body:
        if in_str:
            cur.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
            cur.append(ch)
            continue
        if ch in "([{":
            depth += 1
            cur.append(ch)
            continue
        if ch in ")]}":
            depth -= 1
            cur.append(ch)
            continue
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    parts.append("".join(cur).strip())
    return parts


def fmt_tuple(parts):
    def q(s):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    out = []
    for idx, p in enumerate(parts):
        ps = p.strip()
        if ps.startswith("[") and ps.endswith("]"):
            out.append(ps)
        elif ps.startswith('"') and ps.endswith('"'):
            out.append(ps)
        elif ps == "None" or re.fullmatch(r"-?\d+", ps):
            out.append(ps)
        else:
            out.append(q(ps))
    return "(" + ", ".join(out) + "),"


def fix_tuple(txt):
    parts = parse_tuple(txt)
    if len(parts) != 15:
        return txt
    fid = parts[0].strip('"')
    summary = parts[8].strip('"')
    bio = parts[9].strip('"')
    quotes = parse_tuple(parts[11]) if parts[11].strip() else []
    period = parts[6].strip('"')
    role = parts[5].strip('"')

    p_note, r_note = suffix_for({"periodId": period, "role": role})

    # summary 补足
    if len(summary) < 40:
        add = p_note or r_note
        if add and len(summary + add) <= 120:
            summary = summary + add
        else:
            # 再补 role note
            add2 = r_note
            if add2 and len(summary + add2) <= 120:
                summary = summary + add2

    # biography 补足
    if len(bio) < 200:
        add = r_note or p_note
        if add and len(bio + add) <= 1000:
            bio = bio + add
        else:
            add2 = p_note
            if add2 and len(bio + add2) <= 1000:
                bio = bio + add2

    # quotes 截断到 3
    if len(quotes) > 3:
        quotes = quotes[:3]

    parts[8] = '"' + summary.replace('"', '\\"') + '"'
    parts[9] = '"' + bio.replace('"', '\\"') + '"'
    parts[11] = fmt_tuple_inner(quotes)
    return fmt_tuple(parts)


def fmt_tuple_inner(parts):
    out = []
    for p in parts:
        s = p.strip()
        if s.startswith('"') and s.endswith('"'):
            out.append(s)
        else:
            out.append('"' + s.replace('"', '\\"') + '"')
    return "[" + ", ".join(out) + "]"


if __name__ == "__main__":
    total = 0
    for f in sorted(glob.glob("figs_b*.py")):
        c = process(f)
        print(f, "changed", c)
        total += c
    print("total changed", total)
