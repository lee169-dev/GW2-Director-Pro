# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from ui.constants import *
from ui.panels.skill_list import SkillListPanel
from ui.widgets.skill_editor import SkillEditor
from ui.overlay import Overlay
from core.engine.engine import Engine

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 720)

        # 左右分栏
        splitter = QtWidgets.QSplitter()

        self.skill_list = SkillListPanel()
        self.editor = SkillEditor()

        splitter.addWidget(self.skill_list)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)

        self.setCentralWidget(splitter)

        # Overlay
        self.overlay = Overlay()
        self.overlay.move(40, 40)
        self.overlay.show()

        # Engine
        self.engine = Engine(
            on_log=self.log,
            on_status=self.on_status,
            on_overlay=self.on_overlay
        )

        self._build_ui()

    def _build_ui(self):
        self.status_lbl = QtWidgets.QLabel(STATUS_READY)
        self.status_lbl.setStyleSheet(f"color:{COLOR_TEXT_SUB};")

        # 启动按钮
        self.btn_start = QtWidgets.QPushButton(BTN_START)
        self.btn_start.setObjectName("primary")
        self.btn_start.clicked.connect(self.start)

        # 停止按钮
        self.btn_stop = QtWidgets.QPushButton(BTN_STOP)
        self.btn_stop.setObjectName("danger")
        self.btn_stop.clicked.connect(self.stop)

        # 布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        self.setLayout(layout)

    def start(self):
        self.status_lbl.setText(STATUS_RUNNING)
        self.overlay.set_text(STATUS_RUNNING)

    def stop(self):
        self.status_lbl.setText(STATUS_READY)
        self.overlay.set_text(STATUS_READY)

    def set_skills(self, skills):
        self.skill_list.set_skills(skills, self.on_skill_selected)
        self.engine.set_skills(skills)

    def on_skill_selected(self, skill):
        self.editor.bind(skill)

    def on_status(self, running: bool):
        text = STATUS_RUNNING if running else STATUS_READY
        self.overlay.set_text(text)

    def on_overlay(self, text: str, color: str):
        self.overlay.set_text(text)

    def log(self, text: str):
        print(text)
