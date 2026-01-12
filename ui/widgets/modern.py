# ui/widgets/modern.py
from PySide6 import QtWidgets, QtCore, QtGui

class ModernButton(QtWidgets.QPushButton):
    """
    iOS 风格按钮：
    - 鼠标悬停时轻微放大
    - 点击时反馈
    - 丝滑背景色过渡
    """
    def __init__(self, text, color="#3A3A3C", hover_color="#4A4A4C", icon=None):
        super().__init__(text)
        if icon: self.setIcon(icon)
        
        self.default_color = QtGui.QColor(color)
        self.hover_color = QtGui.QColor(hover_color)
        self.current_color = self.default_color

        self.setFixedHeight(40)
        self.setCursor(QtCore.Qt.PointingHandCursor)
        
        # 阴影效果
        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QtGui.QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

        # 动画引擎
        self._anim = QtCore.QPropertyAnimation(self, b"color_prop")
        self._anim.setDuration(150)
        
    def _update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color.name()};
                color: white;
                border-radius: 10px;
                border: none;
                font-family: "Microsoft YaHei", "Segoe UI";
                font-weight: 600;
                font-size: 13px;
            }}
        """)
        
    def showEvent(self, event):
        self._update_style()
        super().showEvent(event)

    # 属性动画需要的 Property
    def get_color(self): return self.current_color
    def set_color(self, c):
        self.current_color = c
        self._update_style()
    color_prop = QtCore.Property(QtGui.QColor, get_color, set_color)

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setEndValue(self.hover_color)
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setEndValue(self.default_color)
        self._anim.start()
        super().leaveEvent(event)


class CoordMonitor(QtWidgets.QScrollArea):
    """
    左侧参数监视器：
    显示 Key | (x, y) | Color Block
    """
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { width: 4px; background: transparent; }
            QScrollBar::handle:vertical { background: #555; border-radius: 2px; }
        """)
        
        self.container = QtWidgets.QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QtWidgets.QVBoxLayout(self.container)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(4)
        self.layout.addStretch() # 弹簧垫底
        
        self.setWidget(self.container)
        self.rows = {}

    def update_data(self, global_coords):
        # 清空旧数据（保留最后的弹簧）
        while self.layout.count() > 1:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            
        self.rows.clear()
        
        if not global_coords:
            lbl = QtWidgets.QLabel("暂无校准数据")
            lbl.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
            lbl.setAlignment(QtCore.Qt.AlignCenter)
            self.layout.insertWidget(0, lbl)
            return

        # 排序：1-9, 0, F1-F3
        keys = sorted(global_coords.keys(), key=lambda k: (len(k), k))
        
        for k in keys:
            data = global_coords[k]
            row = QtWidgets.QFrame()
            row.setStyleSheet("background-color: #252525; border-radius: 6px;")
            row.setFixedHeight(32)
            
            rl = QtWidgets.QHBoxLayout(row)
            rl.setContentsMargins(10, 0, 10, 0)
            
            # Key
            lbl_key = QtWidgets.QLabel(f"[{k}]")
            lbl_key.setFixedWidth(40)
            lbl_key.setStyleSheet("color: #0A84FF; font-weight: bold; font-family: Consolas;")
            
            # Coords
            cx, cy = data.get('cx', 0), data.get('cy', 0)
            lbl_pos = QtWidgets.QLabel(f"POS: {cx}, {cy}")
            lbl_pos.setStyleSheet("color: #AAAAAA; font-size: 11px;")
            
            rl.addWidget(lbl_key)
            rl.addWidget(lbl_pos)
            rl.addStretch()
            
            self.layout.insertWidget(self.layout.count()-1, row)