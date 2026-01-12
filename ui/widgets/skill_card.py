# ui/widgets/skill_card.py
from PySide6 import QtWidgets, QtCore
from ui.constants import SKILL_STATE_TEXT, SKILL_STATE_COLOR

class SkillCard(QtWidgets.QFrame):
    """
    技能卡片：
    - 显示技能名称
    - 显示技能状态（中文）
    - 圆点颜色反映运行态
    """

    clicked = QtCore.Signal(object)

    def __init__(self, skill):
        super().__init__()
        self.skill = skill
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.setObjectName("SkillCard")
        self.setStyleSheet("""
        QFrame#SkillCard {
            background-color: #1E1E1E;
            border-radius: 8px;
        }
        QFrame#SkillCard:hover {
            background-color: #2A2A2A;
        }
        """)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)

        # 第一行：状态点 + 名称 + 延迟
        top = QtWidgets.QHBoxLayout()
        self.dot = QtWidgets.QLabel("●")
        self.dot.setFixedWidth(14)

        self.lbl_name = QtWidgets.QLabel(self.skill.name)
        self.lbl_name.setStyleSheet("font-weight: 600;")

        self.lbl_delay = QtWidgets.QLabel(f"{self.skill.delay} ms")
        self.lbl_delay.setStyleSheet("color: #AAAAAA;")

        top.addWidget(self.dot)
        top.addWidget(self.lbl_name)
        top.addStretch()
        top.addWidget(self.lbl_delay)

        # 第二行：按键 + 状态
        self.lbl_state = QtWidgets.QLabel()
        self.lbl_state.setStyleSheet("color: #8E8E93; font-size: 11px;")

        layout.addLayout(top)
        layout.addWidget(self.lbl_state)

    def refresh(self):
        """根据技能运行态刷新显示"""
        state = self.skill.runtime.state

        self.dot.setStyleSheet(
            f"color: {SKILL_STATE_COLOR[state]}; font-size: 14px;"
        )
        self.lbl_state.setText(
            f"按键：{self.skill.key}    状态：{SKILL_STATE_TEXT[state]}"
        )

    def mousePressEvent(self, event):
        self.clicked.emit(self.skill)
