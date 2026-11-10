import io,json,os,sys
sys.stdout.reconfigure(encoding="utf-8")
P=r"C:\Users\guoga\Documents\DSH\data\.tmp\exp_specs\b6.json"
d=json.load(io.open(P,encoding="utf-8"))
for x in d:
    if x["id"]=="fig-khrushchev": x["summary"]="苏联领导人，以否定斯大林时期的个人崇拜与缓和美苏关系而著称。"
    if x["id"]=="fig-charles-ellington": x["summary"]="英国陆军元帅，以滑铁卢战役击败拿破仑并两度出任英国首相。"
io.open(P,"w",encoding="utf-8",newline="\n").write(json.dumps(d,ensure_ascii=False,indent=1))
print("ok")
