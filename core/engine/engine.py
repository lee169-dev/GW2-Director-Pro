# core/engine/engine.py
import threading
import time
from typing import Callable, Dict, List, Optional, Any
import pydirectinput
import keyboard
from PIL import ImageGrab

from core.models.skill import SkillAction, SkillState
from core.config import load_config, save_config
from core.engine.evaluator import evaluate_skill
from core.engine.calibration import calibrate

class Engine:
    def __init__(
        self,
        config_path: str = "config.json",
        on_log: Optional[Callable[[str], None]] = None,
        on_status: Optional[Callable[[bool], None]] = None,
        on_overlay: Optional[Callable[[str, str], None]] = None,
        on_snapshot: Optional[Callable[[List[Dict]], None]] = None,
        # 【新增】坐标更新回调
        on_coords_update: Optional[Callable[[Dict], None]] = None, 
    ):
        self.config_path = config_path
        self.on_log = on_log or (lambda msg: None)
        self.on_status = on_status or (lambda running: None)
        self.on_overlay = on_overlay or (lambda t, c: None)
        self.on_snapshot = on_snapshot or (lambda d: None)
        self.on_coords_update = on_coords_update or (lambda d: None)

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
            self.on_log("核心引擎已就绪 (v3.0 Apple UI)")
            # 启动时推送一次坐标给 UI
            self.on_coords_update(self.global_coords)
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
        skill = SkillAction(name, key.upper(), delay)
        # 自动填入坐标
        if skill.key in self.global_coords:
            gc = self.global_coords[skill.key]
            skill.cx, skill.cy = gc['cx'], gc['cy']
            skill.p11x, skill.p11y = gc['p11x'], gc['p11y']
            try:
                grab = ImageGrab.grab()
                skill.cr = grab.getpixel((skill.cx, skill.cy))
                skill.p11r = grab.getpixel((skill.p11x, skill.p11y))
                self.on_log(f"[{skill.key}] 自动绑定坐标与颜色")
            except: pass
            
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
        try:
            self.on_log(">>> 开始校准程序")
            calibrate(self.global_coords, self.on_log, self.on_overlay)
            
            self.on_overlay("校准完成", "#30D158")
            self.save()
            # 【新增】校准完，推送到 UI
            self.on_coords_update(self.global_coords)
            
        except Exception as e:
            self.on_log(f"校准中断: {e}")

    # --- 战斗循环 ---
    def start(self):
        if self.running: return
        self.running = True
        self.on_status(True)
        threading.Thread(target=self._combat_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.on_status(False)
        self.on_overlay("READY", "#30D158")

    def toggle(self):
        self.stop() if self.running else self.start()

    def _combat_loop(self):
        while self.running:
            skills = self.get_current_skills()
            if not skills:
                time.sleep(0.5); continue
            
            for s in skills:
                s.runtime.state = evaluate_skill(s)
            
            self.on_snapshot([]) 

            for s in skills:
                if not self.running: break
                if s.runtime.state == SkillState.READY:
                    self.on_overlay(f"CAST: {s.name}", "#00ffff")
                    pydirectinput.press(s.key.lower())
                    time.sleep(max(s.delay, 50) / 1000.0)
            
            time.sleep(0.05)