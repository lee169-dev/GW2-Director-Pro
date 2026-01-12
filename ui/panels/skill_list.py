# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from ui.widgets.skill_card import SkillCard

class SkillListPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.selected_skill_index = None  # 保存当前选中的技能索引

    def set_skills(self, skills, on_select):
        for c in self.cards:
            c.setParent(None)
        self.cards.clear()

        for idx, skill in enumerate(skills):
            card = SkillCard(skill)
            card.clicked.connect(lambda skill=skill: self.on_card_clicked(skill, idx))
            self.layout.insertWidget(self.layout.count() - 1, card)
            self.cards.append(card)

    def on_card_clicked(self, skill, idx):
        self.selected_skill_index = idx  # 保存选中项的索引
        # 可选：显示选中项的详细信息（如编辑框填充）
    
    def get_selected_skill_index(self):
        return self.selected_skill_index
