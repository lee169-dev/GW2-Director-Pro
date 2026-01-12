# ui/main_window.py
import threading
import time
from PySide6 import QtCore, QtWidgets
from core.engine.engine import Engine
from .overlay import Overlay
# 引入高级面板
from ui.panels.skill_list import SkillListPanel

class UiBridge(QtCore.QObject):
    log = QtCore.Signal(str)
    status = QtCore.Signal(bool)
    overlay = QtCore.Signal(str, str)
    snapshot = QtCore.Signal(list)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GW2 Director Pro (PySide6 Ultimate)")
        self.resize(1100, 800)
        
        self.bridge = UiBridge()
        self.bridge.log.connect(self._append_log)
        self.bridge.status.connect(self._set_status)
        self.bridge.overlay.connect(self._set_overlay)
        self.bridge.snapshot.connect(self._on_snapshot) # 连接快照
        
        self.engine = Engine(
            on_log=self.bridge.log.emit,
            on_status=self.bridge.status.emit,
            on_overlay=self.bridge.overlay.emit,
            on_snapshot=self.bridge.snapshot.emit
        )

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

        # 左侧面板
        left = QtWidgets.QFrame()
        left.setFixedWidth(300)
        left.setStyleSheet("QFrame{background:#1C1C1E; border-radius:12px;}")
        left_l = QtWidgets.QVBoxLayout(left)
        root.addWidget(left)

        self.profile_combo = QtWidgets.QComboBox()
        self.profile_combo.addItems(self.engine.get_profiles() or ["Default"])
        self.profile_combo.currentTextChanged.connect(self._on_profile_changed)
        
        left_l.addWidget(QtWidgets.QLabel("PROFILE"))
        left_l.addWidget(self.profile_combo)
        
        btn_calib = QtWidgets.QPushButton("开始 6 点校准")
        btn_calib.clicked.connect(self.engine.start_calibration)
        left_l.addWidget(btn_calib)
        
        left_l.addStretch()

        # 右侧面板
        right = QtWidgets.QFrame()
        right.setStyleSheet("QFrame{background:#111; border-radius:12px;}")
        right_l = QtWidgets.QVBoxLayout(right)
        root.addWidget(right, 1)

        self.status_lbl = QtWidgets.QLabel("STOPPED")
        self.status_lbl.setStyleSheet("font-size:24px; font-weight:bold; color:#FF453A;")
        self.status_lbl.setAlignment(QtCore.Qt.AlignCenter)
        right_l.addWidget(self.status_lbl)

        # === 使用高级列表面板 ===
        self.skill_list_panel = SkillListPanel()
        right_l.addWidget(self.skill_list_panel, 1)

        # 添加技能表单
        form = QtWidgets.QHBoxLayout()
        self.in_name = QtWidgets.QLineEdit(); self.in_name.setPlaceholderText("Name")
        self.in_key = QtWidgets.QLineEdit(); self.in_key.setPlaceholderText("Key"); self.in_key.setFixedWidth(60)
        self.in_delay = QtWidgets.QLineEdit(); self.in_delay.setPlaceholderText("Delay"); self.in_delay.setFixedWidth(80)
        btn_add = QtWidgets.QPushButton("Add"); btn_add.clicked.connect(self._add_skill)
        btn_del = QtWidgets.QPushButton("Del"); btn_del.clicked.connect(self._del_skill)
        
        form.addWidget(self.in_name); form.addWidget(self.in_key); form.addWidget(self.in_delay)
        form.addWidget(btn_add); form.addWidget(btn_del)
        right_l.addLayout(form)

        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setFixedHeight(120)
        self.log_view.setReadOnly(True)
        right_l.addWidget(self.log_view)
        
        self._refresh_list()

    def _on_profile_changed(self, text):
        self.engine.set_profile(text)
        self._refresh_list()

    def _add_skill(self):
        if self.in_name.text() and self.in_key.text():
            self.engine.add_skill(self.in_name.text(), self.in_key.text(), int(self.in_delay.text() or 0))
            self._refresh_list()

    def _del_skill(self):
        # 这里暂时简单处理，实际应该获取 skill_list_panel 的选中项
        # 简化版：删除最后一个，或者你需要给 Panel 加个 get_selected_index
        self.engine.delete_skill_by_index(0) 
        self._refresh_list()

    def _refresh_list(self):
        skills = self.engine.get_current_skills()
        self.skill_list_panel.set_skills(skills, lambda s: print(f"Select {s.name}"))

    @QtCore.Slot(list)
    def _on_snapshot(self, _):
        # 收到快照信号，刷新列表显示（颜色/状态）
        self.skill_list_panel.refresh()

    @QtCore.Slot(str)
    def _append_log(self, msg): self.log_view.appendPlainText(msg)

    @QtCore.Slot(bool)
    def _set_status(self, running):
        self.status_lbl.setText("RUNNING" if running else "STOPPED")
        self.status_lbl.setStyleSheet(f"font-size:24px; font-weight:bold; color:{'#30D158' if running else '#FF453A'};")

    @QtCore.Slot(str, str)
    def _set_overlay(self, t, c): self.overlay.set_text(t, c)

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