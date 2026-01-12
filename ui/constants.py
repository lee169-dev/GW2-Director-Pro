# ui/constants.py
"""
UI 中文常量集中管理
原则：
- UI 中不允许出现硬编码英文
- 状态 / 颜色 / 文案统一在这里维护
"""

from core.models.skill import SkillState

# ===== 应用级 =====
APP_TITLE = "GW2 Director Pro"
APP_SUBTITLE = "激战 2 自动化控制台"

# ===== 技能状态 =====
SKILL_STATE_TEXT = {
    SkillState.READY: "可释放",
    SkillState.COOLDOWN: "冷却中",
    SkillState.FAIL: "不可用",
}

SKILL_STATE_COLOR = {
    SkillState.READY: "#30D158",     # 绿色
    SkillState.COOLDOWN: "#8E8E93",  # 灰色
    SkillState.FAIL: "#FF453A",      # 红色
}

# ===== 通用提示 =====
TEXT_NO_SKILLS = "未配置技能"
TEXT_READY = "待命中"
TEXT_CASTING = "正在施放"
TEXT_WAITING = "等待冷却"
