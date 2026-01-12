# -*- coding: utf-8 -*-
from PySide6 import QtWidgets
from ui.widgets.skill_card import SkillCard

class SkillListPanel(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cards = []

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.addStretch()

    def set_skills(self, skills, on_select):
        for c in self.cards:
            c.setParent(None)
        self.cards.clear()

        for skill in skills:
            card = SkillCard(skill)
            card.clicked.connect(on_select)
            self.layout.insertWidget(self.layout.count() - 1, card)
            self.cards.append(card)

    def refresh(self):
        for c in self.cards:
            if hasattr(c.skill, "runtime"):
                c.update_state(
                    c.skill.runtime.text,
                    c.skill.runtime.color
                )
