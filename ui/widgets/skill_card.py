# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore
from ui.constants import *

class SkillCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(object)

    def __init__(self, skill):
        super().__init__()
        self.skill = skill
        self.setFixedHeight(64)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        self.lbl_name = QtWidgets.QLabel(skill.name)
        self.lbl_name.setStyleSheet("font-size:14px; font-weight:600;")

        self.lbl_state = QtWidgets.QLabel(STATUS_READY)
        self.lbl_state.setStyleSheet(f"color:{COLOR_TEXT_SUB}; font-size:12px;")

        layout.addWidget(self.lbl_name)
        layout.addWidget(self.lbl_state)

    def mousePressEvent(self, e):
        self.clicked.emit(self.skill)

    def update_state(self, text, color):
        self.lbl_state.setText(text)
        self.lbl_state.setStyleSheet(f"color:{color}; font-size:12px;")
