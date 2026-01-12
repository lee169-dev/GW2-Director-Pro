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
