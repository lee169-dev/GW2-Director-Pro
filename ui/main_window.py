# -*- coding: utf-8 -*-
import threading
import time
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import (
    QTextEdit, QMenu, QLineEdit, QPushButton, QFrame,
    QHBoxLayout, QVBoxLayout, QMessageBox, QLabel, QSplitter
)
from PySide6.QtGui import QAction, QFont, QColor
from core.engine.engine import Engine
from ui.overlay import Overlay
from ui.panels.skill_list import SkillListPanel
from ui.widgets.skill_editor import SkillEditor
from core.config import save_config, load_config
from core.models.skill import SkillAction

# 统一从 ui.constants 导入 UI 文案与配色（简洁可维护）
from ui.constants import (
    APP_TITLE, LABEL_ADD_SKILL, PLACEHOLDER_NAME, PLACEHOLDER_KEY, PLACEHOLDER_DELAY,
    BTN_ADD, BTN_EDIT, BTN_SAVE, BTN_CANCEL, BTN_START, BTN_STOP,
    STATUS_READY, STATUS_RUNNING, COLOR_PRIMARY, COLOR_FAIL, COLOR_TEXT_SUB
)

# 尝试导入 ModernButton 与相关常量，若缺失则提供回退实现以避免 NameError
try:
    from ui.widgets.modern import ModernButton
except Exception:
    try:
        from PySide6.QtWidgets import QPushButton
    except Exception:
        # 如果连 PySide6 也不可用，则定义一个最小占位类（极端情况）
        class ModernButton:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("ModernButton/unavailable")
    else:
        class ModernButton(QPushButton):
            def __init__(self, text, color=None, hover_color=None, parent=None):
                super().__init__(text, parent)
                self.setObjectName("ModernButton")
                # 简单样式以保持外观可用
                if color:
                    self.setStyleSheet(f"background-color: {color}; color: #FFFFFF; border-radius: 8px; padding: 6px 14px;")
                else:
                    self.setStyleSheet("background-color: #2C2C2E; color: #EDEDED; border-radius: 8px; padding: 6px 14px;")

class UiBridge(QtCore.QObject):
    """UI 线程桥接器"""
    log = QtCore.Signal(str)
    status = QtCore.Signal(bool)
    overlay = QtCore.Signal(str, str)
    snapshot = QtCore.Signal(list)
    coords_update = QtCore.Signal(dict)  # 恢复坐标更新信号

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # 使用已确保存在的 APP_TITLE 设置窗口标题
        self.setWindowTitle(f"{APP_TITLE} - Pro Edition")
        self.resize(1180, 800)
        
        # === 1. 信号桥接 ===
        self.bridge = UiBridge()
        self.bridge.log.connect(self._append_log)
        self.bridge.status.connect(self._set_status)
        self.bridge.overlay.connect(self._set_overlay)
        self.bridge.snapshot.connect(self._on_snapshot)
        self.bridge.coords_update.connect(self._update_coords_monitor)  # 连接监视器
        
        # === 2. 引擎初始化 ===
        self.engine = Engine(
            config_path="config.json",
            on_log=self.bridge.log.emit,
            on_status=self.bridge.status.emit,
            on_overlay=self.bridge.overlay.emit,
            on_snapshot=self.bridge.snapshot.emit,
            on_coords_update=self.bridge.coords_update.emit  # 注入数据回调
        )

        # === 3. 初始化组件 ===
        self.overlay = Overlay()
        self.overlay.show()
        
        self._init_ui()
        
        # 启动键盘监听
        self._key_thread = threading.Thread(target=self._key_listener, daemon=True)
        self._key_thread.start()

    def _init_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QHBoxLayout(central)
        root.setSpacing(16)
        root.setContentsMargins(16, 16, 16, 16)

        # ==========================
        # 左侧面板：控制与监视
        # ==========================
        left = QtWidgets.QFrame()
        left.setFixedWidth(340)
        left.setStyleSheet("background-color: #1C1C1E; border-radius: 16px;")
        
        # 阴影效果
        shadow = QtWidgets.QGraphicsDropShadowEffect(left)
        shadow.setBlurRadius(20); shadow.setColor(QtGui.QColor(0,0,0,100)); left.setGraphicsEffect(shadow)
        
        left_l = QtWidgets.QVBoxLayout(left)
        left_l.setContentsMargins(20, 25, 20, 25)
        root.addWidget(left)

        # 1. 标题区
        lbl_conf = QtWidgets.QLabel("系统配置")
        lbl_conf.setStyleSheet(f"color: {COLOR_TEXT_SUB}; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        left_l.addWidget(lbl_conf)

        # 2. 职业选择
        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.addItems(self.engine.get_profiles() or ["默认"])
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        self.profile_combo.setFixedHeight(35)
        left_l.addWidget(self.profile_combo)
        left_l.addSpacing(10)

        # 3. 核心按钮组 (使用 ModernButton 实现 Apple 风格)
        # 启动按钮 (红)
        self.btn_start = ModernButton(BTN_START + " (F8)", COLOR_FAIL, "#FF6961")
        self.btn_start.clicked.connect(self.engine.toggle)
        left_l.addWidget(self.btn_start)

        # 校准按钮 (蓝)
        self.btn_calib = ModernButton(BTN_CALIBRATE, "#0A84FF", "#409CFF")
        self.btn_calib.clicked.connect(self.engine.start_calibration)
        left_l.addWidget(self.btn_calib)
        
        left_l.addSpacing(20)

        # 4. 数据监视器 (恢复此功能)
        lbl_monitor = QtWidgets.QLabel("校准数据监控")
        lbl_monitor.setStyleSheet(f"color: {COLOR_TEXT_SUB}; font-size: 12px; font-weight: bold; letter-spacing: 1px;")
        left_l.addWidget(lbl_monitor)
        
        # 确保 coord_monitor 和 log_panel 至少有一个可用的实例（容错）
        if not hasattr(self, "coord_monitor"):
            try:
                from ui.widgets.modern import CoordMonitor
                self.coord_monitor = CoordMonitor()
            except Exception:
                # 轻量 fallback（不可用时不抛异常）
                self.coord_monitor = QLabel("Coord Monitor")
                self.coord_monitor.update_data = lambda data: None

        if not hasattr(self, "log_panel"):
            try:
                from ui.widgets.log_panel import LogPanel
                self.log_panel = LogPanel()
            except Exception:
                # 轻量 fallback：使用 QTextEdit 并提供 log() 方法
                self.log_panel = QTextEdit()
                self.log_panel.setReadOnly(True)
                self.log_panel.log = lambda msg: self.log_panel.append(str(msg))

        left_l.addWidget(self.coord_monitor, 1)

        # ==========================
        # 右侧面板：技能列表与日志
        # ==========================
        right = QtWidgets.QFrame()
        right.setStyleSheet("background-color: #121212; border-radius: 16px;")
        right_l = QtWidgets.QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        right_l.setSpacing(0)
        root.addWidget(right, 1)

        # 1. 顶部状态栏
        top_bar = QtWidgets.QFrame()
        top_bar.setFixedHeight(70)
        top_bar.setStyleSheet("background-color: #1A1A1A; border-top-left-radius: 16px; border-top-right-radius: 16px; border-bottom: 1px solid #333;")
        tl = QtWidgets.QHBoxLayout(top_bar)
        tl.setContentsMargins(30, 0, 30, 0)
        
        self.status_lbl = QtWidgets.QLabel(STATUS_READY)
        self.status_lbl.setStyleSheet(f"font-size:24px; font-weight:800; color:{COLOR_FAIL};")
        tl.addWidget(self.status_lbl)
        tl.addStretch()
        tl.addWidget(QtWidgets.QLabel(APP_TITLE))
        
        right_l.addWidget(top_bar)

        # 2. 内容区容器
        content_area = QtWidgets.QWidget()
        cl = QtWidgets.QVBoxLayout(content_area)
        cl.setContentsMargins(20, 20, 20, 20)
        cl.setSpacing(10)

        # 分割线：上方技能列表，下方编辑器
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.setStyleSheet("QSplitter::handle { background-color: #333; height: 2px; }")
        
        # 技能列表面板
        self.skill_list_panel = SkillListPanel()
        splitter.addWidget(self.skill_list_panel)
        
        # 技能编辑器 (恢复显示)
        self.skill_editor = SkillEditor(self)
        # 默认隐藏，选中技能后显示? 或者一直显示
        splitter.addWidget(self.skill_editor)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        cl.addWidget(splitter, 1)

        # 3. 添加技能表单 (底部栏)
        form = QtWidgets.QHBoxLayout()
        self.in_name = QtWidgets.QLineEdit(); self.in_name.setPlaceholderText("技能名称")
        self.in_key = QtWidgets.QLineEdit(); self.in_key.setPlaceholderText("按键"); self.in_key.setFixedWidth(80)
        self.in_delay = QtWidgets.QLineEdit(); self.in_delay.setPlaceholderText("延迟(ms)"); self.in_delay.setFixedWidth(100)
        
        btn_add = ModernButton(BTN_ADD, COLOR_READY, "#50E378"); btn_add.setFixedWidth(80)
        btn_add.clicked.connect(self._add_skill)
        
        btn_del = ModernButton(BTN_DELETE, "#333", "#444"); btn_del.setFixedWidth(80)
        btn_del.clicked.connect(self._del_skill)
        
        form.addWidget(self.in_name); form.addWidget(self.in_key); form.addWidget(self.in_delay)
        form.addWidget(btn_add); form.addWidget(btn_del)
        
        cl.addLayout(form)
        
        # 4. 日志区域 (恢复 LogPanel)
        # self.log_panel = LogPanel()
        # self.log_panel.setFixedHeight(120)
        # cl.addWidget(self.log_panel)
        
        right_l.addWidget(content_area, 1)

        # --- 新增右下角 "新增技能" 面板（确保使用空格缩进） ---
        self.add_panel = QFrame(self)
        self.add_panel.setObjectName("addPanel")
        add_layout = QHBoxLayout(self.add_panel)
        add_layout.setContentsMargins(8, 6, 8, 6)
        add_layout.setSpacing(8)

        self.input_new_name = QLineEdit()
        self.input_new_name.setPlaceholderText(PLACEHOLDER_NAME)
        self.input_new_key = QLineEdit()
        self.input_new_key.setPlaceholderText(PLACEHOLDER_KEY)
        self.input_new_delay = QLineEdit()
        self.input_new_delay.setPlaceholderText(PLACEHOLDER_DELAY)

        self.btn_add_skill = QPushButton(BTN_ADD)
        self.btn_add_skill.setObjectName("btnAddSkill")
        self.btn_add_skill.clicked.connect(self._on_add_skill)

        add_layout.addWidget(QLabel(LABEL_ADD_SKILL))
        add_layout.addWidget(self.input_new_name)
        add_layout.addWidget(self.input_new_key)
        add_layout.addWidget(self.input_new_delay)
        add_layout.addWidget(self.btn_add_skill)

        # 放置到窗口右下：优先尝试 statusBar（若为 QMainWindow），否则加入主布局末尾靠右
        if hasattr(self, "statusBar"):
            try:
                self.statusBar().addPermanentWidget(self.add_panel)
            except Exception:
                try:
                    self.layout().addWidget(self.add_panel, alignment=Qt.AlignRight | Qt.AlignBottom)
                except Exception:
                    self.add_panel.setParent(self)
                    self.add_panel.show()
        else:
            try:
                self.layout().addWidget(self.add_panel, alignment=Qt.AlignRight | Qt.AlignBottom)
            except Exception:
                self.add_panel.setParent(self)
                self.add_panel.show()

        # 右上区域会响应右键弹出新增菜单（本类统一处理 contextMenuEvent）
        # ...existing code...

    # 右键菜单：当鼠标右键在窗口右上角区域时显示“新增技能”
    def contextMenuEvent(self, event):
        # 右上区域右键弹出菜单（新增技能）
        pos = event.pos()
        # 右上触发区域：宽度 - 380 到右边界，顶部 0..140
        if pos.x() >= max(0, self.width() - 380) and pos.y() <= 140:
            menu = QMenu(self)
            act_add = QAction(BTN_ADD, self)
            act_add.triggered.connect(self._focus_add_skill_inputs)
            menu.addAction(act_add)
            menu.exec(event.globalPos())
        else:
            super().contextMenuEvent(event)

    def _focus_add_skill_inputs(self):
        try:
            self.input_new_name.setFocus()
            self.input_new_name.selectAll()
        except Exception:
            pass

    def _on_add_skill(self):
        name = (self.input_new_name.text() or "").strip()
        key = (self.input_new_key.text() or "").strip()
        delay_text = (self.input_new_delay.text() or "").strip()

        if not name:
            QMessageBox.warning(self, "错误", "请填写技能名称。")
            return
        if not key:
            QMessageBox.warning(self, "错误", "请填写按键。")
            return
        try:
            delay = int(delay_text or 0)
        except ValueError:
            QMessageBox.warning(self, "错误", "延迟需为整数（毫秒）。")
            return

        # 确保加载了 profiles/global_coords
        if not hasattr(self, "profiles") or not hasattr(self, "global_coords"):
            gc, pr = load_config()
            self.global_coords = gc
            self.profiles = pr

        profile_name = getattr(self, "current_profile", None) or next(iter(self.profiles), None)
        if profile_name is None:
            profile_name = "Default"
            self.profiles[profile_name] = []

        new_skill_data = {
            "name": name,
            "key": key,
            "delay": delay,
            "cx": 0, "cy": 0, "p11x": 0, "p11y": 0
        }
        try:
            s = SkillAction.from_dict(new_skill_data)
        except Exception:
            s = new_skill_data

        self.profiles.setdefault(profile_name, []).append(s)

        try:
            save_config("config.json", self.global_coords, self.profiles)
        except Exception as e:
            print("保存配置失败:", e)
            QMessageBox.warning(self, "错误", "保存配置失败，请检查日志。")
            return

        self.input_new_name.clear()
        self.input_new_key.clear()
        self.input_new_delay.clear()
        QMessageBox.information(self, "已添加", f"已向配置文件 '{profile_name}' 添加技能：{name}")
        try:
            self._refresh_list()
        except Exception:
            pass

    # --- 逻辑控制 ---
    @QtCore.Slot(dict)
    def _update_coords_monitor(self, data):
        """引擎发来新的坐标数据 -> 刷新左侧列表"""
        # 容错：若 coord_monitor 或 update_data 不存在则跳过
        if hasattr(self, "coord_monitor") and hasattr(self.coord_monitor, "update_data"):
            try:
                self.coord_monitor.update_data(data)
            except Exception:
                pass
        # else: 静默跳过避免抛错

    def _on_profile_changed(self, text):
        self.engine.set_profile(text)
        self._refresh_list()

    def _add_skill(self):
        name = self.in_name.text()
        key = self.in_key.text()
        delay = self.in_delay.text()

        if not name or not key:
            QtWidgets.QMessageBox.warning(self, "警告", "技能名和按键不能为空！")
            return

        self.engine.add_skill(name, key, int(delay or 0))
        self._refresh_list()

    def _del_skill(self):
        selected_idx = self.skill_list_panel.get_selected_skill_index()
        
        if selected_idx is None:
            QtWidgets.QMessageBox.warning(self, "警告", "没有选中任何技能！")
            return
        
        self.engine.delete_skill_by_index(selected_idx)
        self._refresh_list()

    def _refresh_list(self):
        skills = self.engine.get_current_skills()
        # 绑定点击事件：点击卡片 -> 编辑器显示
        # 传入编辑回调与删除回调
        self.skill_list_panel.set_skills(skills, self._open_skill_editor, self._on_skill_deleted)

    @QtCore.Slot(list)
    def _on_snapshot(self, _):
        self.skill_list_panel.refresh()

    @QtCore.Slot(str)
    def _append_log(self, msg): 
        # 容错：若 log_panel 或 log 方法不可用则回退为打印
        if hasattr(self, "log_panel") and hasattr(self.log_panel, "log"):
            try:
                self.log_panel.log(msg)
            except Exception:
                print(str(msg))
        else:
            print(str(msg))

    @QtCore.Slot(bool)
    def _set_status(self, running):
        if running:
            self.status_lbl.setText(STATUS_RUNNING)
            self.status_lbl.setStyleSheet(f"font-size:24px; font-weight:800; color:{COLOR_READY};")
        else:
            self.status_lbl.setText(STATUS_READY)
            self.status_lbl.setStyleSheet(f"font-size:24px; font-weight:800; color:{COLOR_FAIL};")

    @QtCore.Slot(str, str)
    def _set_overlay(self, t, c): 
        # Overlay 现在的 set_text 只有一个参数，需要适配
        self.overlay.set_text(t)

    def _key_listener(self):
        import keyboard
        while True:
            if keyboard.is_pressed('F8'):
                self.engine.toggle()
                time.sleep(0.3)
            time.sleep(0.02)

    def closeEvent(self, e):
        self.engine.stop()
        self.engine.save()
        self.overlay.close()
        super().closeEvent(e)

    def _open_skill_editor(self, skill):
        # 打开编辑器并在保存后回调 _on_skill_saved
        self.skill_editor.exec_for(skill, lambda orig, new: self._on_skill_saved(orig, new))

    def _on_skill_saved(self, original_skill, new_data):
        # 确保有 profiles 与 current_profile
        if not hasattr(self, "profiles") or not hasattr(self, "global_coords"):
            gc, pr = load_config()
            self.global_coords = gc
            self.profiles = pr

        profile_name = getattr(self, "current_profile", None) or next(iter(self.profiles), None)
        if not profile_name:
            return

        skills = self.profiles.get(profile_name, [])
        updated = False
        for i, s in enumerate(skills):
            # 匹配：对象相同或按 name/key/cx 匹配
            match = False
            if s is original_skill:
                match = True
            else:
                if isinstance(s, SkillAction):
                    if isinstance(original_skill, SkillAction):
                        match = (s is original_skill)
                    else:
                        match = (s.name == original_skill.get("name") and str(s.key) == str(original_skill.get("key")))
                else:
                    # dict 情况
                    if isinstance(original_skill, dict):
                        match = (s.get("name") == original_skill.get("name") and s.get("key") == original_skill.get("key"))

            if match:
                # 更新字段
                if isinstance(s, SkillAction):
                    # 尝试直接设置属性
                    for k, v in new_data.items():
                        try:
                            setattr(s, k, v)
                        except Exception:
                            pass
                else:
                    s.update(new_data)
                updated = True
                break

        if updated:
            # 持久化并刷新 UI
            try:
                save_config("config.json", self.global_coords, self.profiles)
            except Exception as e:
                print("保存配置失败:", e)
            self._refresh_list()

    def _on_skill_deleted(self, skill):
        # 找到当前 profile 并删除匹配项（按对象或 name/key/delay）
        profile_name = getattr(self, "current_profile", None) or next(iter(getattr(self, "profiles", {})), None)
        if not profile_name:
            return
        skills = self.profiles.get(profile_name, [])
        removed = False
        for i, s in enumerate(skills):
            # 匹配逻辑：对象相同或关键字段相同
            if s is skill or (isinstance(s, dict) and isinstance(skill, dict) and s.get("name")==skill.get("name") and s.get("key")==skill.get("key") and str(s.get("delay"))==str(skill.get("delay"))):
                del skills[i]
                removed = True
                break
        # 如果被删除，持久化并刷新 UI
        if removed:
            try:
                from core.config import save_config
                save_config("config.json", self.global_coords, self.profiles)
            except Exception as e:
                print("保存配置失败:", e)
            self._refresh_list()

    def _on_skill_selected(self, skill, card_widget):
        # 管理单选：取消之前选中卡的高亮并设置当前卡高亮
        prev = getattr(self, "_selected_card_widget", None)
        if prev and hasattr(prev, "set_selected"):
            try:
                prev.set_selected(False)
            except Exception:
                pass
        self._selected_card_widget = card_widget
        self._selected_skill = skill
        if card_widget and hasattr(card_widget, "set_selected"):
            try:
                card_widget.set_selected(True)
            except Exception:
                pass

    def _on_global_delete(self):
        # 删除当前选中的技能（如果有）
        skill = getattr(self, "_selected_skill", None)
        if not skill:
            # 可选：弹出提示对话框或静默返回
            print("未选择技能，无法删除。")
            return

        # 找到当前 profile
        profile_name = getattr(self, "current_profile", None) or next(iter(getattr(self, "profiles", {})), None)
        if not profile_name:
            return

        skills = self.profiles.get(profile_name, [])
        removed = False
        for i, s in enumerate(skills):
            # 匹配：对象相同或按 name/key/delay 匹配
            if s is skill or (isinstance(s, dict) and isinstance(skill, dict) and s.get("name")==skill.get("name") and s.get("key")==skill.get("key") and str(s.get("delay"))==str(skill.get("delay"))):
                del skills[i]
                removed = True
                break

        if removed:
            try:
                from core.config import save_config
                save_config("config.json", self.global_coords, self.profiles)
            except Exception as e:
                print("保存配置失败:", e)
            # 清除选择引用并刷新
            self._selected_skill = None
            if hasattr(self, "_selected_card_widget") and self._selected_card_widget:
                try:
                    self._selected_card_widget.set_selected(False)
                except Exception:
                    pass
                self._selected_card_widget = None
            self._refresh_list()
