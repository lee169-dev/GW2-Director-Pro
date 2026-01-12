# ui/widgets/skill_editor.py
from PySide6 import QtWidgets

class SkillEditor(QtWidgets.QFrame):
    """
    技能属性编辑面板
    注意：这里只做“展示 / 编辑”，不做逻辑判断
    """

    def __init__(self):
        super().__init__()
        self.skill = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: #151515; border-radius: 10px;")
        layout = QtWidgets.QFormLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        self.edt_name = QtWidgets.QLineEdit()
        self.edt_key = QtWidgets.QLineEdit()
        self.spin_delay = QtWidgets.QSpinBox()
        self.spin_delay.setRange(50, 5000)

        layout.addRow("技能名称", self.edt_name)
        layout.addRow("按键", self.edt_key)
        layout.addRow("延迟（毫秒）", self.spin_delay)

    def bind(self, skill):
        """绑定选中的技能"""
        self.skill = skill
        self.edt_name.setText(skill.name)
        self.edt_key.setText(skill.key)
        self.spin_delay.setValue(skill.delay)
