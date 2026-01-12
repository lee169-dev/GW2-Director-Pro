import math
import time
import pyautogui
import keyboard
from PIL import ImageGrab

def calibrate(global_coords, log):
    steps = [
        ("指向 [1] 左上 → P", "p"),
        ("指向 [5] 右下 → P", "p"),
        ("指向 [6] 左上 → P", "p"),
        ("指向 [0] 右下 → P", "p"),
        ("指向 [F1] 左上 → P", "p"),
        ("指向 [F3] 右下 → P", "p"),
    ]

    points = []
    for text, key in steps:
        log(text)
        keyboard.wait(key)
        points.append(pyautogui.position())
        time.sleep(0.3)

    def calc(p1, p2, keys):
        w = (p2.x - p1.x) / len(keys)
        r = (w / 2) * 0.85
        cy = int((p1.y + p2.y) / 2)

        for i, k in enumerate(keys):
            cx = int(p1.x + w * i + w / 2)
            offx = int(r * math.sin(math.radians(30)))
            offy = int(r * math.cos(math.radians(30)))
            p11x, p11y = cx - offx, cy - offy
            global_coords[k] = {"cx": cx, "cy": cy, "p11x": p11x, "p11y": p11y}

    calc(points[0], points[1], ["1","2","3","4","5"])
    calc(points[2], points[3], ["6","7","8","9","0"])
    calc(points[4], points[5], ["F1","F2","F3"])
