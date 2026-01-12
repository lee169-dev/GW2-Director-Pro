# ui/panels/skill_list.py
from PySide6 import QtWidgets
from ui.widgets.skill_card import SkillCard

class SkillListPanel(QtWidgets.QWidget):
    """
    技能列表面板：
    - 管理多个 SkillCard
    - 提供统一刷新接口
    """

    def __init__(self):
        super().__init__()
        self.cards = []
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(6)
        self.layout.addStretch()

    def set_skills(self, skills, on_select):
        # 清空旧卡片
        for card in self.cards:
            card.setParent(None)
        self.cards.clear()

        for skill in skills:
            card = SkillCard(skill)
            card.clicked.connect(on_select)
            self.layout.insertWidget(self.layout.count() - 1, card)
            self.cards.append(card)

    def refresh(self):
        for card in self.cards:
            card.refresh()
