# core/engine.py
import threading
import time
import math
from typing import Callable, Dict, List, Optional, Any
import pydirectinput
import keyboard
import pyautogui
from PIL import ImageGrab
from .models import SkillAction
from .config import load_config, save_config

class Engine:
    def __init__(
        self,
        config_path: str = "config.json",
        on_log: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[bool], None]] = None,
        on_overlay: Optional[Callable[[str, str], None]] = None,
        on_snapshot: Optional[Callable[[List[Dict]], None]] = None, # 新增快照回调
    ):
        self.config_path = config_path
        self.on_log = on_log or (lambda msg: None)
        self.on_status = on_status or (lambda running: None)
        self.on_overlay = on_overlay or (lambda t, c: None)
        self.on_snapshot = on_snapshot or (lambda d: None)

        self.running = False
        self.current_profile = "Guardian - Dragonhunter"
        self.global_coords: Dict[str, Any] = {}
        self.profiles_data: Dict[str, List[SkillAction]] = {self.current_profile: []}
        self._load()

    def _load(self):
        try:
            gc, pd = load_config(self.config_path)
            self.global_coords = gc
            if pd:
                self.profiles_data.update(pd)
                self.current_profile = next(iter(self.profiles_data.keys()))
            self.on_log("核心引擎已就绪 (v2.0)")
        except Exception as e:
            self.on_log(f"Load Error: {e}")

    def save(self):
        try:
            save_config(self.config_path, self.global_coords, self.profiles_data)
            self.on_log("配置已保存")
        except Exception as e:
            self.on_log(f"保存失败: {e}")

    # --- 数据操作 ---
    def set_profile(self, profile: str):
        if profile == self.current_profile: return
        self.current_profile = profile
        if profile not in self.profiles_data: self.profiles_data[profile] = []
        self.on_log(f"切换模版 -> {profile}")
        self.save()

    def get_profiles(self) -> List[str]: return list(self.profiles_data.keys())
    def get_current_skills(self) -> List[SkillAction]: return self.profiles_data.get(self.current_profile, [])

    def add_skill(self, name: str, key: str, delay: int):
        key = key.upper()
        cx, cy, cr, p11x, p11y, p11r = 0, 0, None, 0, 0, None
        
        # 自动匹配坐标
        if key in self.global_coords:
            gc = self.global_coords[key]
            cx, cy, p11x, p11y = gc['cx'], gc['cy'], gc['p11x'], gc['p11y']
            try:
                grab = ImageGrab.grab()
                cr = grab.getpixel((cx, cy))
                p11r = grab.getpixel((p11x, p11y))
                self.on_log(f"[{key}] 自动取色成功")
            except: pass

        skill = SkillAction(name, key, delay, cx, cy, cr, p11x, p11y, p11r)
        self.profiles_data.setdefault(self.current_profile, []).append(skill)
        self.save()

    def delete_skill_by_index(self, idx: int):
        skills = self.profiles_data.get(self.current_profile, [])
        if 0 <= idx < len(skills):
            skills.pop(idx)
            self.save()

    # --- 校准逻辑 ---
    def start_calibration(self):
        threading.Thread(target=self._calibration_wizard, daemon=True).start()

    def _calibration_wizard(self):
        import winsound
        steps = [("Step 1/6: Point [1] Top-Left -> Press P", "p"), ("Step 2/6: Point [5] Bottom-Right -> Press P", "p"),
                 ("Step 3/6: Point [6] Top-Left -> Press P", "p"), ("Step 4/6: Point [0] Bottom-Right -> Press P", "p"),
                 ("Step 5/6: Point [F1] Top-Left -> Press P", "p"), ("Step 6/6: Point [F3] Bottom-Right -> Press P", "p")]
        points = []
        try:
            self.on_log(">>> 开始校准")
            for text, trigger in steps:
                self.on_overlay(text, "yellow")
                keyboard.wait(trigger)
                winsound.Beep(800, 100)
                points.append(pyautogui.position())
                time.sleep(0.5)
            self._calc_region(points[0], points[1], ["1","2","3","4","5"])
            self._calc_region(points[2], points[3], ["6","7","8","9","0"])
            self._calc_region(points[4], points[5], ["F1","F2","F3"])
            self.on_overlay("校准完成", "#00ff00")
            self.save()
        except Exception as e: self.on_log(f"校准失败: {e}")

    def _calc_region(self, p1, p2, keys):
        width = (p2.x - p1.x) / len(keys)
        radius = (width / 2) * 0.85
        cy = int((p1.y + p2.y) / 2)
        for i, k in enumerate(keys):
            cx = int(p1.x + i * width + width/2)
            off_x, off_y = int(radius * math.sin(math.radians(30))), int(radius * math.cos(math.radians(30)))
            self.global_coords[k] = {'cx': cx, 'cy': cy, 'p11x': cx-off_x, 'p11y': cy-off_y}

    # --- 战斗循环 (v2.0) ---
    def start(self):
        if self.running: return
        self.running = True
        self.on_status(True)
        threading.Thread(target=self._combat_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.on_status(False)
        self.on_overlay("READY", "#00ff00")

    def toggle(self):
        self.stop() if self.running else self.start()

    def _combat_loop(self):
        while self.running:
            skills = self.get_current_skills()
            if not skills:
                time.sleep(0.5); continue
            
            # 1. 发送快照 (可视化状态)
            snapshot = []
            for s in skills:
                snapshot.append({"name": s.name, "key": s.key, "status": "CD" if False else "READY"}) 
                # 注：这里简化了CD计算，完整版可参考之前的 logic
            self.on_snapshot(snapshot)

            # 2. 执行逻辑
            for s in skills:
                if not self.running: break
                
                # 双点检测
                can_cast = True
                if s.cr and s.p11r:
                    try:
                        grab = ImageGrab.grab()
                        c, p = grab.getpixel((s.cx, s.cy)), grab.getpixel((s.p11x, s.p11y))
                        if not ((abs(s.cr[0]-c[0])<30) and (abs(s.p11r[0]-p[0])<30)):
                            can_cast = False
                    except: pass
                
                if can_cast:
                    self.on_overlay(f"CAST: {s.name}", "#00ffff")
                    pydirectinput.press(s.key.lower())
                    time.sleep(max(s.delay, 50) / 1000.0)
            
            time.sleep(0.05)