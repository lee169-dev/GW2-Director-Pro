# -*- coding: utf-8 -*-
import threading
import time
from PySide6 import QtCore, QtWidgets, QtGui

from core.engine.engine import Engine
from ui.overlay import Overlay
from ui.panels.skill_list import SkillListPanel
from ui.widgets.skill_editor import SkillEditor
# 引入丢失的现代组件和日志面板
from ui.widgets.modern import ModernButton, CoordMonitor
from ui.widgets.log_panel import LogPanel
from ui.constants import *  # 引入汉化常量

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
        
        self.coord_monitor = CoordMonitor()  # 使用 modern.py 里的组件
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
        self.skill_editor = SkillEditor()
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
        self.log_panel = LogPanel()
        self.log_panel.setFixedHeight(120)
        cl.addWidget(self.log_panel)
        
        right_l.addWidget(content_area, 1)

        # 初始化刷新
        self._refresh_list()

    # --- 逻辑控制 ---
    @QtCore.Slot(dict)
    def _update_coords_monitor(self, data):
        """引擎发来新的坐标数据 -> 刷新左侧列表"""
        self.coord_monitor.update_data(data)

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
        self.skill_list_panel.set_skills(skills, self.skill_editor.bind)

    @QtCore.Slot(list)
    def _on_snapshot(self, _):
        self.skill_list_panel.refresh()

    @QtCore.Slot(str)
    def _append_log(self, msg): 
        self.log_panel.log(msg)

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
