# app.py
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    # ? 全局字体设置：微软雅黑
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
