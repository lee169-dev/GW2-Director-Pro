# ui/overlay.py
from PySide6 import QtWidgets, QtCore
from ui.constants import TEXT_READY

class Overlay(QtWidgets.QWidget):
    """
    悬浮状态窗（显示当前运行状态）
    """

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.Tool |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.label = QtWidgets.QLabel(TEXT_READY)
        self.label.setStyleSheet(
            "font-size: 16px; font-weight: bold; color: #30D158;"
        )

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self.label)

        self.resize(220, 40)
        self.move(100, 100)

    def set_text(self, text, color):
        self.label.setText(text)
        self.label.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {color};"
        )
