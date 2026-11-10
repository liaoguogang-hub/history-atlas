import json, io, sys
sys.stdout.reconfigure(encoding="utf-8")
china = json.load(io.open("data/china.json", encoding="utf-8"))
world = json.load(io.open("data/world.json", encoding="utf-8"))
fig = {f["id"]: f["name"] for f in china["figures"]}
ev = {e["id"]: e["name"] for e in china["events"]}

cands = """fig-peking-man fig-yuanmou-man fig-lantian-man fig-huangdi fig-zhouxuanwang
fig-xiao-bai fig-zhang-liang fig-qin-shi-huang fig-chen-sheng fig-liu-gong fig-xuanzong
fig-li-huaiguang fig-zhou-bo fig-zhao-kuo fig-zhoujingwang fig-xi-quan fig-qin-hui
fig-xuande fig-zhu-gao fig-shi-jingzhang fig-liu-yan-2 fig-wen-zong-2 fig-yu-chao-en-2
fig-suo-shi fig-wen-zong fig-wang-anshi fig-sima-guang fig-su-shi fig-hai-ru
fig-lin-zexu fig-li-hongzhang fig-liang-qichao fig-chen-duxiu fig-mao-zedong fig-chen-yi
fig-zhu-rongji fig-xi-jinping fig-hu-jintao fig-wen-jiabao fig-zhan-tianyou
fig-qian-xuesen fig-li-siyuan-tang fig-zhang-heng
fig-han-east-fan-pang fig-jin-west-liu-mao fig-tao-kan fig-xiao-yan fig-fang-xuanling
fig-wei-gong fig-yang-su fig-han-west-wei-qing
fig-qi-huanggong fig-guan-zhong fig-bao-shuya fig-mencius fig-liu-bei fig-zhuge-liang
fig-han-xin fig-liu-bang fig-bai-qi fig-wang-jian fig-li-si fig-zhao-gao fig-wu-guang
fig-zhouwu fig-zhougong fig-zhouchengwang fig-zhouliwang fig-zhouyouwang fig-zhoukangwang
fig-jiangzhu fig-yan-ying fig-jin-wengong fig-chu-zhuangwang fig-qin-mugong fig-bai-lixi
fig-kao fig-shang-yang fig-liqin fig-qi-weiwang fig-tian-ji fig-sun-bin fig-pang-juan
fig-sun-tzu fig-kongzi fig-lao-tzu fig-mozi fig-xunzi fig-zhuangzi fig-han-feizi
fig-mencius fig-zouji fig-xiao-bai fig-han-wudi fig-zhang-qian fig-sima-qian fig-xiang-yu
fig-han-zhaodi fig-chang-hui fig-dong-zhongshu fig-cai-lun fig-zhang-zhongjing fig-hua-tuo
fig-ban-gu fig-han-east-cao-cao fig-lv-meng fig-xun-yu fig-guo-jia fig-he-jin fig-wang-jing
fig-fan-pang fig-han-east-han-xiandi fig-han-east-mingdi fig-chen-qun fig-wei-qing
fig-sima-yue fig-sima-yan-jin fig-xie-lan-2 fig-nanbei-north-tuoba-tao fig-tuoba-tao
fig-nanbei-north-bao-ling fig-nanbei-south-fan-yun fig-nanbei-south-fang-xuanling
fig-fang-xuanling fig-du-ru-hui fig-shen-yue fig-liu-xie fig-wang-wei fig-li-shimin-tang
fig-zhu-yuanzhang fig-zhu-di fig-zheng-he fig-li-shi-zhen fig-wang-yangming
fig-zhang-juzheng fig-qi-jiguang fig-xu-xiake fig-wu-sangui fig-li-zicheng fig-chongzhen
fig-nurhaci fig-huang-taiji fig-duo-er-dung fig-kangxi fig-yongzheng fig-qianlong
fig-jiaqing fig-daoguang fig-wei-yuan fig-zeng-guofan fig-zuo-zongtang fig-zhang-zhidong
fig-kang-youwei fig-zhang-taiyan fig-yuan-shikai fig-song-jiaoren fig-huang-xing
fig-dong-bi-wu fig-liu-shaoqi fig-liu-bocheng fig-peng-dehuai fig-zhang-xueliang
fig-li-zongren fig-hu-shi fig-zhou-enlai fig-lin-biao fig-li-keqiang fig-li-gong fig-wang-yi
fig-sun-tai-zhen fig-han-wudi-2 fig-jing-zong fig-yongzheng-2 fig-xuande-2
fig-li-bang fig-tang-late-wang-yi fig-liu-yan fig-niu-jinxing fig-li-de fig-li-heng
fig-wei-daozhou fig-pan-zhenjia fig-li-zongti fig-yang-guozhong fig-liu-zongyuan
fig-han-yu fig-du-fu fig-bai-juyi fig-yuan-zhen fig-wang-changling fig-yang-guifei
fig-cao-shuang fig-sima-shi fig-sima-zhao fig-zhuge-liang fig-zhang-fei fig-liu-shan
fig-taishi-ci fig-wang-jun fig-liang-wudi fig-taishao fig-xie-an fig-xie-xuan fig-sima-rui
fig-tao-yuanming fig-wang-xizhi fig-zu-chongzhi fig-xiaowen fig-tuoba-gui fig-yuwen-tai
fig-dug-paruo fig-lu-su fig-lv-meng fig-zhou-yu fig-lu-xun fig-sunquan fig-sun-hao
fig-guan-yu fig-zhao-yun fig-jia-wei fig-han-east-cao-pi fig-han-east-cao-rui fig-cao-zhi
fig-sima-yi fig-huangfu-song fig-ma-yuan fig-liu-gong-2 fig-zhang-heng-2 fig-cai-lun-2
fig-zhao-tuo fig-liu-yan-3 fig-pang-juan-2 fig-bian-quan fig-fan-yin fig-dou-jing
fig-yang-yi fig-han-gao-zu fig-lu-jia fig-huo-guan fig-tang-gou fig-wang-shichong
fig-yu-ji fig-bai-lian ting fig-wu-zetian fig-liang-wudi-2 fig-chang-an fig-wu-dai-zhen
fig-yuan-zhen-2 fig-guo-ziyi fig-li-guangbi fig-du-ru-hui-2 fig-zhao-guangyi
fig-li-cheng-liang fig-nalan-xingduo fig-kangxi-2 fig-shunzhi fig-li-zongti-2
fig-yongzheng-3 fig-jiaqing-2 fig-daoguang-2 fig-xianfeng fig-lin-zexu-2 fig-liu-kun
fig-han-wudi-3 fig-zhang-liang-2 fig-zhou-bo-2 fig-hua-lin fig-zu-cheng
fig-huangdi-2 fig-yan-di fig-shao-kang fig-dong-zhuo fig-liu-bang-2 fig-zhou-bo-3
fig-bai-qi-2 fig-wu-qi fig-mu-zhou fig-xu-zhou fig-shi-qiang fig-wu-zi fig-lu-xun-2
fig-sun-wu fig-dong-wu fig-xiao-he fig-liang-sun fig-lu-xun-3 fig-liu-mao-2
fig-zhou-fang fig-zhou-fang-2 fig-wu-meng fig-wu-mu fig-meng-de fig-gao-zi
fig-zhao-yi fig-liang-wei fig-jin-huan fig-he-yan fig-zhang-xun fig-wei-wu
fig-yu-qian-2 fig-zhu-qi fig-zhu-zhen fig-zhao-zhen fig-li-dongyang fig-dong-wang
fig-qi-liang fig-wu-lie fig-luo-guangxing fig-luo-lianfang fig-shi-wei fig-liang-du
fig-wei-zhong fig-yan-lin fig-bao-ji fig-li-de-2 fig-xiao-ji fig-zhou-bang
fig-niu-fu fig-liu-fu fig-du-hong fig-duo-er-dung-2 fig-wu-sangui-2 fig-li-zicheng-2
fig-han-dun fig-han-zu fig-zhang-chun-he fig-guo-jing fig-liang-du-2 fig-yang-lie
fig-li-zi-cheng fig-zhou-xing-2 fig-li-ying-2 fig-han-shun-2 fig-zhu-zhi-2
fig-xu-zong-2 fig-zhang-rongxin fig-li-zonghua fig-yuan-zu fig-zhong-wu fig-xi-zong
fig-luo-cheng fig-zhao-guo fig-zhou-yan-2 fig-chen-pu fig-liu-qi-2 fig-cheng-yi
fig-zhou-pu-2 fig-liang-jun-2 fig-lian-qu fig-li-fang-2 fig-luo-xiang-2 fig-yue-lin
fig-liu-kuo fig-hu-lian fig-gao-zu-2 fig-wang-dun-2 fig-xiao-yan-2 fig-zhao-yi-2
fig-jin-lun-2 fig-luo-ying fig-liang-du-3 fig-wang-xun fig-wang-hong-2
fig-liu-fu-2 fig-zhou-yan-2 fig-zhang-sun fig-ding-wen fig-wu-liang-zi
fig-xiao-ze-xian fig-shen-zhao fig-liang-du-4 fig-zhang-lun-2 fig-liu-rong-2
fig-zhou-chang-2 fig-liang-du-5 fig-guo-huai fig-wu-xiang-2 fig-zhang-ru-2
fig-liu-huan fig-luo-ying-2 fig-zhao-yuan fig-xiao-ji-2 fig-guo-huai-2
fig-wu-liang-zi-2 fig-zhao-yuan-2 fig-geng-xin fig-yang-yan fig-liu-xiang-2
fig-li-zong-2 fig-zhu-luo fig-han-wen-di fig-hua-yang-hou fig-luo-ji
fig-han-yi-di fig-liu-quan fig-liang-du-6 fig-liu-yu-di fig-liu-yu-di-2
fig-liang-du-7 fig-li-hong fig-liu-gong-3 fig-ying-zong fig-shun-ting di
fig-dou-lu fig-li-yan-2 fig-xiao-zi fig-wu-liang-zi-3 fig-yu-wen ti
fig-li-shu-2 fig-zhao-guo-2 fig-yang-lie-2 fig-li-zi-2 fig-liu-ting-2
fig-jin-liu-di fig-yang-di-2 fig-wei-zi-2 fig-li-zhi-2 fig-han-an-di
fig-wu-yi-2 fig-liu-sheng-3 fig-li-huan-2 fig-lu-xun-4 fig-chen-shu-2
fig-zhao-fen-2 fig-zhang-huan-2 fig-li-huan-3 fig-luo-jun-3 fig-guo-ba-xi
fig-liu-huan-3 fig-zheng-zi fig-pan-fang fig-hu-lian-2 fig-lu-zheng-2
fig-geng-yan fig-li-sun-2 fig-ding-yuan-2 fig-xu-yuan-2 fig-yan-gui
fig-hu-yi fig-fang-xuanling-2 fig-wang-shi-2 fig-shi-de-2 fig-zheng-xuan
fig-liu-di fig-liu-hai fig-wang-bo fig-yin-li fig-cheng-gong fig-li-du
fig-wei-shu fig-hu-bin fig-xu-sheng fig-liu-an fig-li-de-3 fig-chen-lun
fig-wang-hui-2 fig-shen-zhuo fig-xie-lingyun fig-liu-ling-2 fig-hu-ji
fig-hu-bin-2 fig-yu-liang fig-xu-ji fig-tang-yan fig-guo-ba-xi-2 fig-liu-chang
fig-luo-cheng-2 fig-zhao-yuan-3 fig-hou-zhu fig-liu-jing fig-jia-ling
fig-dong-hua fig-li-zhu-2 fig-liu-huo fig-li-fang-3 fig-xun-yi fig-wu-ji
fig-liu-zong fig-xiao-gan fig-liu-quan-2 fig-wang-an-2 fig-yang-ping
fig-lu-xun-5 fig-shen-yin fig-li-shi-3 fig-yan-jing fig-wang-yan-2
fig-xu-ting fig-chen-yi-2 fig-guo-ji fig-liu-bai fig-wang-hong-3
fig-li-zhi-3 fig-zhao-yin fig-wei-ying-2 fig-li-yuan-2 fig-ma-zhi
fig-li-dun fig-hu-jie fig-liu-xi-2 fig-zhu-ban fig-xu-xi-2 fig-geng-zhong
fig-luo-hongxin fig-guo-wei fig-liu-zhiyuan fig-niu-jinxing-2 fig-li-conghou
fig-li-zhu fig-zhu-wen fig-xu-zong-3 fig-han-lin-2 fig-liu-xi-3 fig-shu-chong-2
fig-wu-dai-fig fig-zhao-kui fig-tang-yan-2 fig-yang-yin fig-guan-xiu fig-wu-jie-2
fig-lu-yu fig-yang-yan-2 fig-han-chi fig-wu-zetian-2 fig-liu-yan-4
fig-zhong-liang-2 fig-liang-qu-2 fig-yuan-xun fig-li-yan-3 fig-hou-yan
fig-zhang-ze fig-xiao-dong fig-li-ma-2 fig-tang-jian-2 fig-guan-zhong-2
fig-liu-sheng-4 fig-li-xun fig-cheng-yan fig-yuan-kao fig-wang-chong-2
fig-liu-ying-3 fig-lu-jing fig-liu-hang-2 fig-xiao-yan-3 fig-xue-ying
fig-liang-dun fig-han-ling fig-zhu-qing-2 fig-zhu-qian-2 fig-wu-liang-2
fig-xu-huan-2 fig-chen-ming fig-liang-shu fig-liu-ting-3 fig-tan-luo
fig-li-de-4 fig-xie-jian-2 fig-zhou-ting fig-wang-shun fig-guo-ba-xi-3
fig-liang-du-8 fig-liu-yuan-2 fig-yu-jian-2 fig-liu-zong-2 fig-xu-yan
fig-huang-quan fig-xiao-huan fig-yang-yong fig-zhu-heng-2 fig-xu-guang
fig-liang-du-9 fig-li-wu fig-li-shou fig-xu-de-3 fig-li-hua
fig-yuan-wei fig-liang-du-10 fig-lu-zhou fig-guo-jing-2 fig-xiao-yu-2
fig-zhang-lun-3 fig-li-yu-3 fig-xu-gui-2 fig-li-jie-2 fig-liu-ji-2
fig-liu-quan-3 fig-wang-zong fig-liang-du-11 fig-zhang-zong-2 fig-li-yan-4
fig-liu-zong-3 fig-yuan-xi-2 fig-yu-wei-2 fig-li-de-5 fig-lu-yu-2
fig-liu-xun-6 fig-guo-zong fig-yang-yan-3 fig-li-de-6 fig-zheng-yu
fig-li-xing fig-wu-yuan-2 fig-zhou-tao fig-li-shu-3 fig-liu-zi
fig-liang-jin liu fig-xiao-zhi fig-li-zi-3 fig-liu-jing-2 fig-xu-lun-2
fig-zhao-tuo-2 fig-lu-jia-2 fig-yuan-guo fig-li-zhu-3 fig-li-yuan-3
fig-zhang-ang fig-wu-di fig-han-shun-3 fig-li-yan-5 fig-xiao-zi-2
fig-du-yu-2 fig-lu-xun-7 fig-liu-lu-2 fig-xiao-xin-2 fig-huang-ming
fig-yu-ji-2 fig-hu-fang fig-li-fu-2 fig-zhu-lu-2 fig-liu-zong-4
fig-xu-fu fig-wang-xi-3 fig-zhou-yan-3 fig-xiao-jian-2 fig-wu-shi
fig-liu-tang-2 fig-zhang-shi fig-yang-huan fig-liu-zhu-2 fig-chen-lun-2
fig-zhou-bo-4 fig-liu-huan-2 fig-li-dao fig-xiao-yi-2 fig-wu-zhong
fig-liu-an-2 fig-jiang-wan-2 fig-li-guo fig-dong-guo fig-liu-huan-3
fig-li-zi-4 fig-zhang-yu-2 fig-huai-en fig-wang-shu fig-xun-huan
fig-jia-guo fig-xiao-xiang-2 fig-liu-xi-4 fig-yuan-liang fig-xiao-wan-2
fig-liu-lun-2 fig-yu-ling fig-liu-wen-2 fig-wang-xi-4 fig-guo-zhi
fig-liu-ying-4 fig-xiao-dong-2 fig-yang-liang fig-li-yuan-4 fig-han-wu-2
fig-zheng-yan-2 fig-wang-ji fig-liu-ji-2 fig-zhao-tuo-3 fig-ding-guo
fig-liu-luo fig-zhao-yuan-4 fig-li-wen-2 fig-lu-wen fig-xiao-xian
fig-zhang-xun-2 fig-hu-zun fig-wu-zhong-2 fig-liu-he fig-yuan-yin-2
fig-li-gui-2 fig-liang-du-12 fig-wu-jie-3 fig-luo-wu fig-liu-zong-5
fig-liu-huan-4 fig-xiao-xiang-3 fig-yang-hua fig-liu-ying-5 fig-xu-chang
fig-zhu-zhou fig-wang-jie-2 fig-liu-xu fig-liu-sheng-5 fig-li-xun-2
fig-xiao-xian-3 fig-liang-ying fig-liu-zong-6 fig-liu-xu-2 fig-wang-xi-5
fig-lu-xun-8 fig-dong-zhou fig-wu-liang-3 fig-li-xing-2 fig-xun-gong
fig-liu-zong-7 fig-liu-luo-2 fig-wu-zhong-3 fig-yang-xian fig-zhang-xi
fig-guo-ba-xi-4 fig-liu-xu-3 fig-liu-lao fig-yang-yan-4 fig-li-ji-2
fig-lu-xun-9 fig-gui-liang fig-liu-xian-2 fig-li-huan-2 fig-zhang-xun-3
fig-guo-ba-xi-5 fig-guo-huang fig-xiao-ji-3 fig-yu-ji-3 fig-xie-yun
fig-liu-zong-8 fig-xu-shu fig-wu-zhong-4 fig-zhang-yun fig-yang-jie-2
fig-zheng-zong-2 fig-liu-zong-9 fig-xiao-yan-4 fig-yang-xing-2 fig-liu-zong-10
fig-liu-xu-4 fig-hua-wei fig-wu-liang-4 fig-xiao-zhen fig-liu-yuan-3
fig-zhang-zi-ying fig-liang-xun fig-dong-zi fig-li-zhi-4 fig-wang-shun-2
fig-geng-ting fig-zhong-yu fig-yu-ji-4 fig-xiao-gan-2 fig-wu-liang-5
fig-liu-ling-3 fig-liu-zong-11 fig-xiao-hai fig-hui-yan fig-dong-shu
fig-liu-qi-3 fig-zhao-yin-2 fig-li-wang fig-zhao-ming fig-lu-zhou-2
fig-yang-lian fig-liu-ji-3 fig-wu-shu fig-liu-zhu-3 fig-zhou-ying
fig-liu-zong-12 fig-zhao-yin-3 fig-xu-zhou-2 fig-li-yan-6 fig-luo-zhong
fig-liu-wen-3 fig-xiao-xian-4 fig-lu-zhou-3 fig-liu-zong-13 fig-liang-dun-2
fig-wang-xi-6 fig-guo-ba-xi-6 fig-yang-yan-5 fig-li-zong-3 fig-wu-ming-2
fig-dai-ju fig-yang-yan-6 fig-luo-guangxing-2 fig-wu-xiang-3 fig-wu-yuan-3
fig-zhang-zhen-2 fig-xiao-ji-4 fig-liu-zong-14 fig-yang-yan-7 fig-li-zong-4
fig-xiao-yan-5 fig-xiao-yi fig-hu-yan fig-geng-xin-2 fig-yang-yan-8
fig-liu-zong-15 fig-huang-zhao fig-li-ji-3 fig-li-zhi-5 fig-liu-yuan-4
fig-luo-dan fig-yang-yan-9 fig-wu-zhong-5 fig-liu-zong-16 fig-li-zong-5
fig-xu-wei fig-liu-zong-17 fig-li-yuan-5 fig-hai-ru-2 fig-lin-zexu-3
fig-li-hongzhang-2 fig-zeng-guofan-2 fig-zuo-zongtang-2 fig-zhang-zhidong-2
fig-liang-qichao-2 fig-chen-duxiu-2 fig-mao-zedong-2 fig-chen-yi-3 fig-zhu-rongji-2
fig-xi-jinping-2 fig-hu-jintao-2 fig-wen-jiabao-2 fig-zhan-tianyou-2 fig-qian-xuesen-2
fig-li-siyuan-tang-2 fig-zhang-heng-2 fig-peking-man-2 fig-yuanmou-man-2 fig-lantian-man-2
fig-huangdi-3 fig-zhouxuanwang-2 fig-xiao-bai-2 fig-zhang-liang-2 fig-qin-shi-huang-2
fig-chen-sheng-2 fig-liu-gong-2 fig-xuanzong-2 fig-li-huaiguang-2 fig-zhou-bo-2
fig-zhao-kuo-2 fig-zhoujingwang-2 fig-xi-quan-2 fig-qin-hui-2 fig-xuande-2
fig-zhu-gao-2 fig-shi-jingzhang-2 fig-liu-yan-2-2 fig-wen-zong-2-2 fig-yu-chao-en-2-2
fig-suo-shi-2 fig-wen-zong-3 fig-wang-anshi-2 fig-sima-guang-2 fig-su-shi-2
fig-hai-ru-2 fig-lin-zexu-2 fig-li-hongzhang-3 fig-liang-qichao-3 fig-chen-duxiu-3
fig-mao-zedong-3 fig-chen-yi-4 fig-zhu-rongji-3 fig-xi-jinping-3 fig-hu-jintao-3
fig-wen-jiabao-3 fig-zhan-tianyou-3 fig-qian-xuesen-3 fig-li-siyuan-tang-3""".split()

print("=== 可用人物引用 ===")
for c in dict.fromkeys(cands):
    if c in fig:
        print(f"  {c} = {fig[c]}")
print("\n=== 缺失 ===")
miss = [c for c in dict.fromkeys(cands) if c not in fig]
print(" ", miss if miss else "无")
