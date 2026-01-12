# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore
from ui.constants import STATUS_READY

class Overlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            QtCore.Qt.Tool |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.label = QtWidgets.QLabel(STATUS_READY, self)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(30, 30, 30, 180);
                color: #EDEDED;
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 14px;
                font-weight: 500;
            }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

    def set_text(self, text: str):
        self.label.setText(text)
        self.adjustSize()
