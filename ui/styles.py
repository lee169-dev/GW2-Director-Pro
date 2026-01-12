STYLE = """
QWidget {
    background-color: #121212;
    color: #EDEDED;
    font-family: "Microsoft YaHei";
    font-size: 13px;
}
QLabel { color: #EDEDED; }
QFrame { background-color: #1C1C1E; border-radius: 12px; }
QPushButton { background-color: #2C2C2E; color: #EDEDED; border: none; border-radius: 10px; padding: 6px 14px; }
QPushButton#primary { background-color: #0078D7; border-radius: 8px; padding: 6px 12px; color: #FFF; min-height: 32px; }
QPushButton#primary:hover { background-color: #0A84FF; }
QPushButton#danger { background-color: #FF453A; }
QPushButton:disabled { background-color: #3A3A3C; color: #8E8E93; }
QLineEdit, QPlainTextEdit { background-color: #1E1E1E; color: #EDEDED; border-radius: 8px; padding: 6px; }
QLineEdit::placeholder { color: #8E8E93; }

/* 顶部右侧面板样式 */
QFrame#topRight {
    max-width: 360px;
    background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #1F2226, stop:1 #151618);
    border: 1px solid rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 8px;
}
QLabel.title { font-size: 14px; font-weight: 700; color: #FFFFFF; }
QLabel.meta { font-size: 12px; color: #9AA0A6; }
QFrame#topRight QLabel#skillName { font-size: 20px; font-weight: 800; color: #FFFFFF; }
"""
