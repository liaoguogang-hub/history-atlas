import io
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

ADB = r"C:\Users\guoga\AppData\Local\Android\Sdk\platform-tools\adb.exe"
OUT = r"C:\Users\guoga\Documents\DSH\_verify_shots"
XML = r"C:\Users\guoga\Documents\DSH\_ui.xml"


def sh(*args):
    return subprocess.run(args, capture_output=True, text=True)


def dump():
    sh(ADB, "shell", "uiautomator", "dump", "/sdcard/ui.xml")
    sh(ADB, "pull", "/sdcard/ui.xml", XML)


def nodes():
    dump()
    try:
        text = io.open(XML, encoding="utf-8").read()
    except Exception:
        return []
    out = []
    for m in re.finditer(r"<node[^>]*>", text):
        node = m.group(0)

        def attr(name):
            mm = re.search(name + r'="([^"]*)"', node)
            return mm.group(1) if mm else ""

        t, d, b = attr("text"), attr("content-desc"), attr("bounds")
        if not (t or d):
            continue
        mm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
        if not mm:
            continue
        x1, y1, x2, y2 = map(int, mm.groups())
        out.append((t, d, (x1 + x2) // 2, (y1 + y2) // 2))
    return out


def find(label, exact=False):
    for t, d, x, y in nodes():
        if (t == label) if exact else (label in t or label in d):
            return x, y
    return None


def tap(x, y):
    sh(ADB, "shell", "input", "tap", str(x), str(y))
    time.sleep(1.5)


def tap_text(label, exact=False):
    r = find(label, exact)
    if r:
        tap(*r)
        return True
    return False


def shot(name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    sh(ADB, "shell", "screencap", "-p", "/sdcard/s.png")
    sh(ADB, "pull", "/sdcard/s.png", path)
    print("  saved", os.path.basename(path))


def restart():
    sh(ADB, "shell", "am", "force-stop", "com.historyatlas.app")
    sh(ADB, "shell", "am", "start", "-ncom.historyatlas.app/.MainActivity"
       if False else "-n", "com.historyatlas.app/.MainActivity")
    time.sleep(6)


def swipe(x1, y1, x2, y2, ms=400):
    sh(ADB, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))
    time.sleep(1.2)


def back():
    sh(ADB, "shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(1.2)


def main():
    print("capturing detail pages ->", OUT)

    # ---- 事件流 → 事件详情 ----
    restart()
    tap_text("事件流")
    time.sleep(2)
    shot("10_event_list.png")
    # 点第一个事件（列表里第一条）
    ns = nodes()
    # 找事件标题：列表中第一个非日期、非按钮的文本
    tapped = False
    for t, d, x, y in ns:
        if t and len(t) > 3 and not t.startswith("公元") and not t.startswith("公元前") \
           and t not in ("事件流", "按时间与分类浏览全部历史事件") and y > 400:
            print("  tapping event:", t)
            tap(x, y)
            tapped = True
            break
    if tapped:
        time.sleep(2)
        shot("11_event_detail.png")
        swipe(540, 1800, 540, 900)
        time.sleep(1)
        shot("12_event_detail_scrolled.png")
    else:
        print("  MISS event row")

    # ---- 人物志 → 人物详情 ----
    restart()
    tap_text("人物志")
    time.sleep(2)
    shot("13_figure_list.png")
    ns = nodes()
    tapped = False
    for t, d, x, y in ns:
        if t and len(t) >= 2 and y > 400 and t not in (
                "人物志", "帝王将相、思想家、科学家与探索者",
                "全部", "思想家", "科学家", "帝王", "将领", "诗人", "学者"):
            print("  tapping figure:", t)
            tap(x, y)
            tapped = True
            break
    if tapped:
        time.sleep(2)
        shot("14_figure_detail.png")

    # ---- 搜索 → 搜索结果 ----
    restart()
    tap_text("搜索朝代")
    time.sleep(1.5)
    sh(ADB, "shell", "input", "text", "唐")
    time.sleep(2.5)
    shot("15_search_tang.png")

    # ---- 年表总览 → 时期详情 ----
    restart()
    tap_text("年表总览")
    time.sleep(2)
    shot("16_tree.png")
    swipe(540, 1700, 540, 700)
    time.sleep(1)
    ns = nodes()
    for t, d, x, y in ns:
        if t in ("唐", "宋", "明", "清", "元", "汉") and y > 300:
            print("  tapping period:", t)
            tap(x, y)
            time.sleep(2)
            shot("17_period_detail.png")
            break
    else:
        print("  MISS period row")

    # ---- 世界史 ----
    restart()
    if tap_text("世界史", exact=True):
        time.sleep(2)
        shot("18_home_world.png")
        tap_text("人物志")
        time.sleep(2)
        shot("19_world_figures.png")
        tap_text("年表总览")
        time.sleep(2)
        shot("20_world_tree.png")

    print("done")


if __name__ == "__main__":
    main()
