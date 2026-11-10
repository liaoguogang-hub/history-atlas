import io, re, sys, subprocess

XML = r"C:\Users\guoga\Documents\DSH\_ui.xml"
ADB = r"C:\Users\guoga\AppData\Local\Android\Sdk\platform-tools\adb.exe"


def dump():
    subprocess.run([ADB, "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
                   capture_output=True)
    subprocess.run([ADB, "pull", "/sdcard/ui.xml", XML], capture_output=True)


def parse(text):
    """Return list of (text, desc, bounds)."""
    out = []
    for m in re.finditer(r'<node[^>]*>', text):
        node = m.group(0)

        def attr(name):
            mm = re.search(name + r'="([^"]*)"', node)
            return mm.group(1) if mm else ""

        t = attr("text")
        d = attr("content-desc")
        b = attr("bounds")
        if not (t or d):
            continue
        mm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
        if not mm:
            continue
        x1, y1, x2, y2 = map(int, mm.groups())
        out.append((t, d, x1, y1, x2, y2))
    return out


def tap(x, y):
    subprocess.run([ADB, "shell", "input", "tap", str(x), str(y)], capture_output=True)


def shot(path):
    subprocess.run([ADB, "shell", "screencap", "-p", "/sdcard/s.png"], capture_output=True)
    subprocess.run([ADB, "pull", "/sdcard/s.png", path], capture_output=True)


def find(label, nodes):
    for t, d, x1, y1, x2, y2 in nodes:
        if label in t or label in d:
            return (x1 + x2) // 2, (y1 + y2) // 2, t, d
    return None


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    if cmd == "list":
        dump()
        for t, d, x1, y1, x2, y2 in parse(io.open(XML, encoding="utf-8").read()):
            if t or d:
                print(f"[{(x1+x2)//2:5d},{(y1+y2)//2:5d}] text={t!r} desc={d!r}")
    elif cmd == "tap":
        dump()
        nodes = parse(io.open(XML, encoding="utf-8").read())
        r = find(sys.argv[2], nodes)
        if not r:
            print("NOT FOUND:", sys.argv[2])
            sys.exit(1)
        x, y, t, d = r
        print(f"tap {x},{y}  ({t!r} {d!r})")
        tap(x, y)
    elif cmd == "shot":
        shot(sys.argv[2])
        print("saved", sys.argv[2])
