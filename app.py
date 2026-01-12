# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, QCoreApplication
from ui.main_window import MainWindow

def main():
    # 在创建 QApplication 之前设置高 DPI 选项，减少 SetProcessDpiAwarenessContext() 报错
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    app = QApplication(sys.argv)

    # 全局字体：微软雅黑
    app.setFont(QFont("Microsoft YaHei", 10))

    # Apple / Pro Tool 风格 · 静态语义色 · 无 hover
    app.setStyleSheet("""
    QWidget {
        background-color: #121212;
        color: #EDEDED;
        font-family: "Microsoft YaHei";
        font-size: 13px;
    }

    QLabel {
        color: #EDEDED;
    }

    QFrame {
        background-color: #1C1C1E;
        border-radius: 12px;
    }

    QPushButton {
        background-color: #2C2C2E;
        color: #EDEDED;
        border: none;
        border-radius: 10px;
        padding: 6px 14px;
    }

    QPushButton#primary {
        background-color: #0A84FF;   /* Apple 蓝 */
    }

    QPushButton#danger {
        background-color: #FF453A;   /* Apple 红 */
    }

    QPushButton:disabled {
        background-color: #3A3A3C;
        color: #8E8E93;
    }

    QLineEdit, QPlainTextEdit {
        background-color: #1E1E1E;
        color: #EDEDED;
        border-radius: 8px;
        padding: 6px;
    }

    QLineEdit::placeholder {
        color: #8E8E93;
    }
    """)

    win = MainWindow()
    win.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
