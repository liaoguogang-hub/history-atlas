import io
import os
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
    import re
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


def find(label, ns=None):
    ns = ns or nodes()
    for t, d, x, y in ns:
        if label in t or label in d:
            return x, y
    return None


def tap(x, y):
    sh(ADB, "shell", "input", "tap", str(x), str(y))
    time.sleep(1.4)


def tap_text(label):
    r = find(label)
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
    return path


def back():
    sh(ADB, "shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(1.2)


def restart():
    sh(ADB, "shell", "am", "force-stop", "com.historyatlas.app")
    sh(ADB, "shell", "am", "start", "-n", "com.historyatlas.app/.MainActivity")
    time.sleep(5.5)


def swipe(x1, y1, x2, y2, ms=400):
    sh(ADB, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(ms))
    time.sleep(1.2)


PLAN = [
    ("01_home_china", "home"),
    ("02_tree", "年表总览"),
    ("03_axis", "时间轴"),
    ("04_figures", "人物志"),
    ("05_events", "事件流"),
    ("06_compare", "中外对照"),
]


def main():
    print("capturing ->", OUT)
    restart()
    for name, label in PLAN:
        # 回到首页
        restart()
        if label == "home":
            shot(name + ".png")
            continue
        if tap_text(label):
            time.sleep(1.8)
            shot(name + ".png")
        else:
            print("  MISS", label)

    # 时期详情：从年表树进入
    restart()
    tap_text("年表总览")
    time.sleep(1.5)
    swipe(540, 1600, 540, 500)
    ns = nodes()
    picked = None
    for t, d, x, y in ns:
        if t in ("唐", "宋", "明", "清", "元"):
            picked = (t, x, y)
            break
    if picked:
        print("  entering period:", picked[0])
        tap(picked[1], picked[2])
        time.sleep(2)
        shot("07_period_detail.png")
    else:
        print("  MISS period")

    # 搜索
    restart()
    tap_text("搜索朝代")
    time.sleep(1.5)
    ns = nodes()
    for t, d, x, y in ns:
        if t == "秦":
            tap(x, y)
            break
    time.sleep(2)
    shot("08_search.png")

    print("done")


if __name__ == "__main__":
    main()
