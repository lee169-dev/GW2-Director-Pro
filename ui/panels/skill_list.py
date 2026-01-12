# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QSizePolicy
from PySide6.QtCore import Qt
from ui.widgets.skill_card import SkillCard

class SkillListPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(12)
        self.grid.setContentsMargins(12, 12, 12, 12)
        self.setLayout(self.grid)
        self.items = []
        self.setStyleSheet("background-color: #151515; border-radius:8px;")

    def set_skills(self, skills, bind_callback, delete_callback=None, select_callback=None):
        # 清空旧项
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        self.items = []

        # 去重（按 name/key/delay）避免重复展示
        seen = set()
        filtered = []
        for s in skills:
            name = s.get("name") if isinstance(s, dict) else getattr(s, "name", "")
            key = s.get("key") if isinstance(s, dict) else getattr(s, "key", "")
            delay = s.get("delay") if isinstance(s, dict) else getattr(s, "delay", "")
            k = (str(name), str(key), str(delay))
            if k in seen:
                continue
            seen.add(k)
            filtered.append(s)

        for i, skill in enumerate(filtered):
            card = SkillCard(skill)
            # 传入 select_callback，以便卡片点击时通知 MainWindow
            card.bind_to(bind_callback, delete_callback, select_callback)
            delay_ms = skill.get("delay") if isinstance(skill, dict) else getattr(skill, "delay", 0)
            self.items.append((card, int(delay_ms or 0)))

        self._reflow()

        # 清除任何之前的视觉选中（由 MainWindow 控制）
        # 这里不持有 selected 状态，MainWindow 通过回调管理

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._reflow()

    def _reflow(self):
        if not self.items:
            return
        available = max(1, self.width() - 24)
        card_w = 170         # 减小卡片宽度以便多列换行更好看
        arrow_w = 56
        unit_w = card_w + arrow_w
        cols = max(1, available // unit_w)

        # 清空再布局
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)

        row = 0
        col_slot = 0
        for idx, (card, delay_ms) in enumerate(self.items):
            col = col_slot * 2
            self.grid.addWidget(card, row, col)
            if idx < len(self.items) - 1:
                w = QWidget()
                from PySide6.QtWidgets import QVBoxLayout
                l = QVBoxLayout(w)
                l.setContentsMargins(0, 0, 0, 0)
                l.setSpacing(2)
                lbl_delay = QLabel(f"{delay_ms} 毫秒")  # ms -> 毫秒
                lbl_delay.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
                lbl_delay.setStyleSheet("color:#9AA0A6; font-size:11px;")
                lbl_arrow = QLabel("➜")
                lbl_arrow.setAlignment(Qt.AlignCenter)
                lbl_arrow.setStyleSheet("color:#8E8E93; font-size:18px;")
                l.addWidget(lbl_delay)
                l.addWidget(lbl_arrow)
                w.setFixedWidth(arrow_w)
                w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.grid.addWidget(w, row, col + 1)
            col_slot += 1
            if col_slot >= cols:
                row += 1
                col_slot = 0
