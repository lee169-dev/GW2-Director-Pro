# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from ui.constants import COLOR_TEXT_SUB

class CalibrationCard(QtWidgets.QFrame):
    def __init__(self, key, cx, cy, color):
        super().__init__()
        self.setStyleSheet("QFrame { background-color:#1C1C1E; }")

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        title = QtWidgets.QLabel(f"[{key}] 技能槽")
        title.setStyleSheet("font-weight:600;")

        coord = QtWidgets.QLabel(f"中心坐标：({cx}, {cy})")
        coord.setStyleSheet(f"color:{COLOR_TEXT_SUB};")

        color_lbl = QtWidgets.QLabel(f"冷却颜色：{color}")
        color_lbl.setStyleSheet(f"color:{COLOR_TEXT_SUB};")

        layout.addWidget(title)
        layout.addWidget(coord)
        layout.addWidget(color_lbl)
