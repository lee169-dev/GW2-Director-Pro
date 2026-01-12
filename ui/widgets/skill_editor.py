# ui/widgets/skill_editor.py
from PySide6 import QtWidgets
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFormLayout
from PySide6.QtCore import Qt
from ui.constants import PLACEHOLDER_NAME, PLACEHOLDER_KEY, PLACEHOLDER_DELAY, BTN_SAVE, BTN_CANCEL

class SkillEditor(QDialog):
    """
    技能属性编辑面板
    注意：这里只做“展示 / 编辑”，不做逻辑判断
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Skill")
        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        self.input_name = QLineEdit()
        self.input_key = QLineEdit()
        self.input_delay = QLineEdit()
        self.input_name.setPlaceholderText(PLACEHOLDER_NAME)
        self.input_key.setPlaceholderText(PLACEHOLDER_KEY)
        self.input_delay.setPlaceholderText(PLACEHOLDER_DELAY)

        form = QFormLayout()
        form.addRow("名称:", self.input_name)            # Name -> 名称
        form.addRow("按键:", self.input_key)            # Key -> 按键
        form.addRow("延迟（毫秒）:", self.input_delay)  # Delay -> 延迟（毫秒）

        btn_save = QPushButton(BTN_SAVE)   # Save -> 保存
        btn_cancel = QPushButton(BTN_CANCEL) # Cancel -> 取消
        btn_save.clicked.connect(self._on_save)
        btn_cancel.clicked.connect(self.reject)

        h = QHBoxLayout()
        h.addStretch()
        h.addWidget(btn_save)
        h.addWidget(btn_cancel)

        v = QVBoxLayout(self)
        v.addLayout(form)
        v.addLayout(h)

        self._save_cb = None
        self._orig = None

    def exec_for(self, skill, save_callback):
        # 填充初始数据（支持 dict 或对象）
        self._orig = skill
        name = skill.get("name") if isinstance(skill, dict) else getattr(skill, "name", "")
        key = skill.get("key") if isinstance(skill, dict) else getattr(skill, "key", "")
        delay = skill.get("delay") if isinstance(skill, dict) else getattr(skill, "delay", "")
        self.input_name.setText(str(name))
        self.input_key.setText(str(key))
        self.input_delay.setText(str(delay or "0"))
        self._save_cb = save_callback
        return self.exec_()

    def _on_save(self):
        if self._save_cb:
            new_data = {
                "name": self.input_name.text(),
                "key": self.input_key.text(),
                "delay": int(self.input_delay.text() or 0)
            }
            try:
                self._save_cb(self._orig, new_data)
            except Exception as e:
                print("Save callback failed:", e)
        self.accept()
