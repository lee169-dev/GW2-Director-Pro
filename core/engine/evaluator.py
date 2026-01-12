from PIL import ImageGrab
from core.models.skill import SkillAction, SkillState

def evaluate_skill(skill: SkillAction) -> SkillState:
    if not (skill.cr and skill.p11r):
        return SkillState.FAIL

    try:
        grab = ImageGrab.grab()
        c = grab.getpixel((skill.cx, skill.cy))
        p = grab.getpixel((skill.p11x, skill.p11y))

        def near(a, b): return abs(a - b) < 30

        ok_c = all(near(skill.cr[i], c[i]) for i in range(3))
        ok_p = all(near(skill.p11r[i], p[i]) for i in range(3))

        return SkillState.READY if (ok_c and ok_p) else SkillState.COOLDOWN

    except Exception:
        return SkillState.FAIL
