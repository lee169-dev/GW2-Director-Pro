# -*- coding: utf-8 -*-
from PySide6 import QtWidgets

class LogPanel(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setPlaceholderText("系统日志")
        self.setStyleSheet("""
        QPlainTextEdit {
            background-color:#1E1E1E;
            color:#EDEDED;
            border-radius:10px;
        }
        """)

    def log(self, text):
        self.appendPlainText(text)
