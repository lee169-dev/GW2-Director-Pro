# -*- coding: utf-8 -*-
from PySide6 import QtWidgets, QtCore
from ui.constants import *
from ui.constants import BTN_EDIT

class SkillCard(QtWidgets.QFrame):
    clicked = QtCore.Signal(object)

    def __init__(self, skill, parent=None):
        super().__init__(parent)
        self.skill = skill
        self.setObjectName("skillCard")
        # 更精致的渐变与边框，稍微收窄宽度
        self.setStyleSheet("""
        QFrame#skillCard {
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #232327, stop:1 #1B1C1E);
            border-radius: 10px;
            padding: 8px;
            border: 1px solid rgba(255,255,255,0.04);
        }
        QLabel#skillName { color: #FFFFFF; font-size: 15px; font-weight:700; }
        QLabel#skillKey  { color: #9AA0A6; font-size: 11px; }
        QPushButton { min-width:60px; min-height:28px; }
        """)
        self.setFixedWidth(170)  # 更紧凑
        self._init_ui()

    def _init_ui(self):
        # 改为：第一行技能名（大），第二行按键 + 编辑/删除按钮（较小）
        v_main = QtWidgets.QVBoxLayout(self)
        v_main.setContentsMargins(8, 6, 8, 6)
        v_main.setSpacing(6)

        # 第一行：技能名（放大）
        name = self.skill.get("name") if isinstance(self.skill, dict) else getattr(self.skill, "name", "")
        self.lbl_name = QtWidgets.QLabel(str(name))
        self.lbl_name.setObjectName("skillName")
        self.lbl_name.setStyleSheet("font-size:16px; font-weight:700; color:#FFFFFF;")
        v_main.addWidget(self.lbl_name)

        # 第二行：按键 + 按钮
        row = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(8)

        key = self.skill.get("key") if isinstance(self.skill, dict) else getattr(self.skill, "key", "")
        self.lbl_key = QtWidgets.QLabel(f"按键：{str(key)}")
        self.lbl_key.setObjectName("skillKey")
        self.lbl_key.setStyleSheet("font-size:12px; color:#A8B0B6;")
        # 允许换行并可扩展，避免显示不全
        self.lbl_key.setWordWrap(True)
        self.lbl_key.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        self.lbl_key.setMinimumWidth(40)

        # 编辑按钮
        self.btn_edit = QPushButton(BTN_EDIT)  # 使用常量
        self.btn_edit.setObjectName("btnEdit")
        self.btn_edit.setFixedHeight(26)
        self.btn_edit.setStyleSheet("QPushButton#btnEdit { background-color: #5A5A5C; color: #FFFFFF; border-radius: 6px; padding:4px 8px; }")

        # 删除按钮（通常在技能列表中出现）
        self.btn_delete = QtWidgets.QPushButton("删除")
        self.btn_delete.setObjectName("btnDelete")
        self.btn_delete.setFixedHeight(26)
        self.btn_delete.setStyleSheet("QPushButton#btnDelete { background-color: #FF453A; color: #FFFFFF; border-radius: 6px; padding:4px 8px; }")

        # 如果该卡片是被放到右上区域(topRight)，则隐藏删除按钮
        parent = self.parent()
        # 检查祖先链，若存在 objectName == "topRight" 则隐藏删除
        ancestor = parent
        while ancestor is not None:
            try:
                if getattr(ancestor, "objectName", lambda: "")() == "topRight":
                    self.btn_delete.hide()
                    break
            except Exception:
                pass
            ancestor = getattr(ancestor, "parent", lambda: None)()

        h.addWidget(self.lbl_key, 1)
        h.addWidget(self.btn_edit, 0, QtCore.Qt.AlignRight)
        h.addWidget(self.btn_delete, 0, QtCore.Qt.AlignRight)
        v_main.addWidget(row)

        # 选中支持
        self._selected = False
        self._select_cb = None

    def bind_to(self, edit_callback=None, delete_callback=None, select_callback=None):
        # 绑定编辑、删除、选择回调
        if edit_callback:
            self.btn_edit.clicked.connect(lambda: edit_callback(self.skill))
        if delete_callback:
            self.btn_delete.clicked.connect(lambda: delete_callback(self.skill))
        self._select_cb = select_callback

    def mousePressEvent(self, event):
        # 点击卡片时触发选中回调（若提供）
        if self._select_cb:
            try:
                self._select_cb(self.skill, self)
            except Exception:
                pass
        # 改变视觉选中状态
        # 由外部通过 set_selected 控制多个卡的互斥选中
        super().mousePressEvent(event)

    def set_selected(self, yes: bool):
        self._selected = bool(yes)
        if self._selected:
            # 高亮边框
            self.setStyleSheet(self.styleSheet() + "QFrame#skillCard { border: 1px solid #0A84FF; }")
        else:
            # 取消高亮（移除 border；简单方式：重置样式）
            self.setStyleSheet(self.styleSheet().replace("QFrame#skillCard { border: 1px solid #0A84FF; }", ""))
