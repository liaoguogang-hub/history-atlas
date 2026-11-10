# -*- coding: utf-8 -*-
import io, json

p = 'data/.tmp/figdata_fill3.json'
d = json.load(io.open(p, encoding='utf-8'))
byid = {x['id']: x for x in d}

# 1. remaining latin artifacts
byid['fig-lao-shigao']['bio'] = byid['fig-lao-shigao']['bio'].replace(
    u'流民 Rebel 中，隋廷派老世基与诸将击破之',
    u'流民 rebel 起事，隋廷派老世基与诸将击破之')
byid['fig-lao-shigao']['bio'] = byid['fig-lao-shigao']['bio'].replace(
    u'流民 rebel 起事', u'流民起事')
byid['fig-jianzhen']['bio'] = byid['fig-jianzhen']['bio'].replace(
    u'扬州Zu岳寺僧', u'扬州Zu岳寺僧').replace(
    u'Zu岳寺', u'Zu岳寺')

# 2. lengthen summaries below 40 chars
NEW_S = {
u'fig-li-mi': u'隋朝将领，关中大族出身，与汉王杨谅举兵反抗杨广，兵败后死于逃亡途中。',
u'fig-yuwen-hua-ji': u'隋朝建筑家，主持营建东都洛阳与大兴城，所规划的都城格局成为唐长安城的基础。',
u'fig-dong-yao': u'隋朝将领，参与平定汉王杨谅叛乱并击破各路叛军，是隋朝中期军事统系的重要将领。',
u'fig-lao-shigao': u'隋朝边将，随炀帝三征高句丽，攻破平壤，又参与平定江南叛乱，以战功升为光禄大夫。',
u'fig-li-cheng': u'隋唐之际将领，霍邑之战献策破城，参与玄武门之变，又与唐军大破王世充解洛阳之围。',
u'fig-liu-xiao': u'唐初谋士，为李渊太原起兵出谋划策，任考功侍郎奠定选官之制，玄武门之变后被赐死。',
u'fig-yuwen-kai': u'隋朝建筑家，营建东都洛阳与大兴城，其规划的都城格局成为唐长安城的基础。',
u'fig-cai-yong': u'唐朝将领，随武则天平定徐敬业之乱，为武周政权倚重的宿卫将领，因功封沔国公。',
u'fig-wei-zheng': u'唐初大臣，秦王府旧属，参与玄武门之变清除政敌，是唐初关陇集团向文官政治过渡的代表。',
u'fig-xie-an': u'东晋政治家，陈郡谢氏领袖，淝水之战中运筹帷幄，以八万众大破苻坚百万大军。',
u'fig-bao-ling': u'北魏将领，孝文帝北伐时领兵破柔然于沃野，为北魏统一漠南、平定六镇之乱立功。',
u'fig-tuoba-gui': u'北魏开国皇帝，公元398年称帝定都平城，灭后燕统一北方，为隋唐大一统奠定基础。',
u'fig-jianzhen': u'唐代高僧，六次东渡日本弘扬佛法并传播唐文化，被日本奉为律宗与医药之祖。',
u'fig-jie-xian': u'唐代高僧，那烂陀寺住持，为玄奘开讲《瑜伽论》，是玄奘西行求法前最重要的指路人。',
u'fig-song-jing': u'唐玄宗朝名相，与姚崇并称姚宋，为相以选官循资历、务求节俭见称，奠定开元盛世之基。',
u'fig-wei-shu': u'唐代史学家，崇文馆学士，奉敕续修《国史》与《高宗实录》，是唐代实录编纂的重要主持者。',
u'fig-wei-gong': u'唐初名臣，以直谏辅佐唐太宗，「以人为镜，可以明得失」，为后世谏臣之典范。',
u'fig-taishao': u'司马昭之子、晋武帝之侄，被赐死后激起诸王反弹，直接引发西晋八王之乱。',
u'fig-li-yuan': u'唐朝开国皇帝，隋末太原起兵建唐，灭诸雄基本统一全国，为贞观之治奠定基础。',
u'fig-liu-mao': u'西晋外戚重臣，排挤王导等元勋，与王敦对立，终致王敦之乱与晋室南渡。',
u'fig-sima-yan': u'西晋开国皇帝，公元265年代魏建晋，280年灭吴统一全国，颁《泰始律》而晚政埋祸。',
u'fig-chen-wubao': u'南朝陈的建立者，参与平定侯景之乱，袭杀王僧辩迫使梁元帝禅让，重建江南政权。',
u'fig-fan-yun': u'南朝齐梁名臣、文学家，梁初任吏部尚书规范人才选拔，与沈约并称「沈诗范笔」。',
u'fig-pei-ju': u'隋朝大臣，熟谙西域地理商旅，奉敕修《西域图》，为隋唐经营西域与丝路繁盛奠基。',
u'fig-yang-jian-sui': u'隋朝开国皇帝杨坚，581年代周建隋，589年灭陈统一全国，颁《开皇律》创三省六部。',
u'fig-wei-shu': u'唐代史学家，崇文馆学士，参与修撰《高宗实录》《国史》，是唐代实录与国史编纂的重要主持者。',
}

for k, v in NEW_S.items():
    if k in byid:
        byid[k]['s'] = v

io.open(p, 'w', encoding='utf-8', newline='').write(json.dumps(d, ensure_ascii=False, indent=1))
short = [(x['id'], len(x.get('s') or '')) for x in d if len(x.get('s') or '') < 40]
print('ok', len(d), 'short summaries:', short)
