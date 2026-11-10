"""把扩充分片里的虚构引用换成库里真实存在的 id。

撰写扩充分片时，人物与事件的关联 id 多半是凭印象写出来的，
经常指向库里并不存在的条目（例如把「魏征」写成 fig-wei-zheng，
而库里实际是 fig-wei-gong）。

处理规则：
1. 在 ``FIG_ALIAS`` / ``EV_ALIAS`` 里给出「意图写的人名 → 库中真实 id」的映射。
2. 映射命中不到的引用一律删除——关联稍后会由 build_relations.py
   依据事件参与者与正文提及重新推导，硬塞错误 id 比留空更糟。
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 人物：虚构 id → 真实 id
FIG_ALIAS = {
    "fig-wei-zheng": "fig-wei-gong",          # 魏征
    "fig-li-jing": None,                       # 李靖（库中无条目）
    "fig-hou-ying": "fig-nanbei-south-hou-jing",  # 侯景
    "fig-li-xiang": None,                       # 李贤（库中无）
    "fig-xi-liu": None,                         # 刘义庆（库中无）
    "fig-zhu-yi": None,                         # 朱异（库中无）
    "fig-liu-yuxi": "fig-liu-yu",              # 刘禹锡
    "fig-zhang-zhi": None,                      # 张志和（库中无）
    "fig-pei-du": None,                         # 裴度（库中无）
    "fig-yan-song": None,                       # 严嵩（库中无）
    "fig-ouyang-lishi": None,                   # 欧阳氏（库中无）
    "fig-hu-bin": None,                         # 胡彬（库中无）
    "fig-shen-chong": None,                     # 沈充（库中无）
    "fig-cao-rui": None,                        # 曹睿（库中无）
    "fig-hu-zhao": None,                        # 胡昭（库中无）
    "fig-cao-pi": None,                         # 曹丕（库中无）
    "fig-zhang-zun": None,                      # 张遵（库中无）
    "fig-yelv-chucai": None,                    # 耶律楚材（库中无）
    "fig-kublai": None,                         # 元世祖（库中无）
    "fig-yu-wen-tai": "fig-yuwen-tai",         # 宇文泰
    "fig-li-de-ming": None,                     # 李德明（库中无）
    "fig-li-yuanhao": None,                     # 李元昊（库中无）
    "fig-song-huizong": None,                   # 宋徽宗（库中无）
    "fig-tuoba-gui": None,                      # 拓跋珪（库中无）
    "fig-liu-ying": None,                       # 刘颖（库中无）
    "fig-sun-hao": "fig-sun-hao",                 # 孙皓
    "fig-zu-ting": None,                        # 竺道生（库中无）
    "fig-li-chang-tang": None,                  # 李昶（库中无）
    "fig-wei-xiu": None,                        # 朱见濋（库中无）
    "fig-wu-yi": None,                          # 朱祐检（库中无）
    "fig-zhu-gao": None,                        # 朱高炽（库中无）
    "fig-hai-ru": None,                         # 海瑞（库中无）
    "fig-yang-yan": None,                       # 杨炎（库中无）
    "fig-gu-rong": None,                        # 顾荣（库中无）
    "fig-luo-hongxin": None,                    # 罗弘信（库中无）
    "fig-liu-mao": None,                        # 刘茂（库中无）
    "fig-shang-rang": None,                     # 尚让（库中无）
    "fig-zhang-zhuo": None,                     # 张铎（库中无）
    "fig-fan-chong": None,                      # 范充（库中无）
    "fig-ge-shu-han": None,                     # 葛叔汉（库中无）
    "fig-xiang-lun": None,                      # 项纶（库中无）
    "fig-xie-lan": None,                        # 谢烂（库中无）
    "fig-zhao-yan": None,                       # 赵彦（库中无）
    "fig-yu-jin": None,                         # 虞溥（库中无）
    "fig-feng-jian": None,                      # 冯建（库中无）
    "fig-zhou-chang": None,                     # 周昌（库中无）
    "fig-wen-zong": None,                       # 李湛（库中无）
    "fig-fu-jian": None,                        # 苻健（库中无）
    "fig-meng-huo": None,                       # 孟获（库中无）
    "fig-zhuge-shang": None,                    # 诸葛尚（库中无）
    "fig-zao-yi": None,                         # 枣祗（库中无）
    "fig-wang-yanzheng": None,                  # 王彦之（库中无）
    "fig-shi-tiesheng": None,                   # 石天泽（库中无）
    "fig-zhu-ci": None,                         # 朱慈（库中无）
    "fig-xuande": None,                         # 朱高煦（库中无）
    "fig-wei-qing": None,                       # 卫玠（库中无）
    "fig-li-huaiguang": None,                   # 李怀光（库中无）
    "fig-chen-fan": None,                       # 范滂（库中无）
    "fig-tian-xiang": None,                     # 田祥（库中无）
    "fig-yan-fulong": None,                     # 颜福成（库中无）
    "fig-han-east-deng-rong": None,             # 邓荣（库中无）
    "fig-tao-kan": None,                        # 陶侃（库中无）
    "fig-hu-bin-2": None,
}

# 事件：虚构 id → 真实 id
EV_ALIAS = {
    "ev-tang-li-shimin": "ev-tang-xuanwumen",
    "ev-tang-wuzhong": "ev-tang-zhenguan",
    "ev-liang-jin-liu-yu": None,
    "ev-liang-jin-nanbei": None,
    "ev-tang-yongzhen-gai": None,
    "ev-tang-baijiu": None,
    "ev-ming-gengxu": None,
    "ev-three-shu-fall": "ev-weijin-shu-fall",
    "ev-three-wei-ding": None,
    "ev-jin-eight-princes": "ev-weijin-eight-princes",
    "ev-song-mongol-war": "ev-yuan-mongol-unify",
    "ev-yuan-mongol": "ev-yuan-founding",
    "ev-nanbei-northern": None,
    "ev-sixteen-kingdoms": None,
    "ev-song-xixia-war": None,
    "ev-ming-jiajing": None,
    "ev-three-wu-religion": None,
}


def main():
    for path in sys.argv[1:]:
        data = json.load(io.open(path, encoding="utf-8"))
        rem_f = rem_e = fixed = 0
        for f in data:
            new_rf = []
            for r in (f.get("relatedFigures") or []):
                if r in FIG_ALIAS:
                    tgt = FIG_ALIAS[r]
                    if tgt:
                        new_rf.append(tgt)
                        fixed += 1
                    else:
                        rem_f += 1
                else:
                    new_rf.append(r)
            f["relatedFigures"] = new_rf

            new_re = []
            for r in (f.get("relatedEvents") or []):
                if r in EV_ALIAS:
                    tgt = EV_ALIAS[r]
                    if tgt:
                        new_re.append(tgt)
                        fixed += 1
                    else:
                        rem_e += 1
                else:
                    new_re.append(r)
            f["relatedEvents"] = new_re

        io.open(path, "w", encoding="utf-8").write(
            json.dumps(data, ensure_ascii=False, indent=1))
        print(f"{path}: 修正引用 {fixed}，删除人物引用 {rem_f}，删除事件引用 {rem_e}")


if __name__ == "__main__":
    main()
