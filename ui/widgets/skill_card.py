# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore
from ui.constants import *

class SkillCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(object)

    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.setObjectName("skillCard")
        self.setStyleSheet("""
        QFrame#skillCard {
            background-color: #232327;
            border-radius: 8px;
            padding: 8px;
        }
        QLabel { color: #EDEDED; }
        QPushButton { min-width:60px; }
        """)
        self.setFixedWidth(180)
        self._init_ui()

    def _init_ui(self):
        main = QtWidgets.QHBoxLayout(self)
        main.setContentsMargins(8, 6, 8, 6)
        main.setSpacing(8)

        col = QtWidgets.QVBoxLayout()
        name = self.skill.get("name") if isinstance(self.skill, dict) else getattr(self.skill, "name", "")
        key = self.skill.get("key") if isinstance(self.skill, dict) else getattr(self.skill, "key", "")

        self.lbl_name = QtWidgets.QLabel(str(name))
        self.lbl_name.setStyleSheet("font-size:16px; font-weight:600;")
        self.lbl_key = QtWidgets.QLabel(str(key))
        self.lbl_key.setStyleSheet("font-size:12px; color:#A8B0B6;")

        col.addWidget(self.lbl_name)
        col.addWidget(self.lbl_key)
        col.addStretch()

        self.btn_edit = QtWidgets.QPushButton("Edit")
        self.btn_edit.setFixedHeight(28)

        main.addLayout(col, 1)
        main.addWidget(self.btn_edit, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def mousePressEvent(self, e):
        self.clicked.emit(self.skill)

    def update_state(self, text, color):
        self.lbl_state.setText(text)
        self.lbl_state.setStyleSheet(f"color:{color}; font-size:12px;")

    def bind_to(self, callback):
        # 当点击 Edit 时回调外部传入的绑定函数，传入该 skill 作为参数
        if callback:
            self.btn_edit.clicked.connect(lambda: callback(self.skill))
