# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QCoreApplication
from ui.main_window import MainWindow
from ui.styles import STYLE

def main():
    # 使用环境变量启用高 DPI 支持（兼容多数平台）
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)

    # 全局字体：微软雅黑
    app.setFont(QFont("Microsoft YaHei", 10))

    # 使用集中样式
    app.setStyleSheet(STYLE)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
