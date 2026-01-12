# core/engine/calibration.py
import math
import time
import pyautogui
import keyboard
import winsound # 引入声音库
from PIL import ImageGrab

def calibrate(global_coords, log, overlay_callback=None):
    """
    执行校准流程
    :param global_coords: 全局坐标字典 (引用)
    :param log: 日志回调函数
    :param overlay_callback: 悬浮窗回调函数 (用于显示提示)
    """
    steps = [
        ("Step 1/6: 指向 [1] 左上 → 按 P", "p"),
        ("Step 2/6: 指向 [5] 右下 → 按 P", "p"),
        ("Step 3/6: 指向 [6] 左上 → 按 P", "p"),
        ("Step 4/6: 指向 [0] 右下 → 按 P", "p"),
        ("Step 5/6: 指向 [F1] 左上 → 按 P", "p"),
        ("Step 6/6: 指向 [F3] 右下 → 按 P", "p"),
    ]

    points = []
    
    # 提示开始
    log(">>> 进入校准模式 (请跟随悬浮窗提示)")
    if overlay_callback:
        overlay_callback("开始校准: 按 P 确认", "yellow")
    
    try:
        for text, key in steps:
            # 1. 更新日志
            log(text)
            
            # 2. 更新悬浮窗 (视觉反馈)
            if overlay_callback:
                overlay_callback(text, "#FFD60A") # 黄色提示
            
            # 3. 等待按键
            keyboard.wait(key)
            
            # 4. 播放提示音 (听觉反馈)
            winsound.Beep(800, 100) # 800Hz, 100ms
            
            # 5. 记录坐标
            points.append(pyautogui.position())
            
            # 防抖动
            time.sleep(0.3)

        # 开始计算
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
        
        log(">>> 校准计算完成")
        
    except Exception as e:
        log(f"校准逻辑错误: {e}")