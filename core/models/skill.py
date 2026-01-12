from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Tuple, List

RGB = Tuple[int, int, int]

class SkillState(Enum):
    READY = "READY"
    COOLDOWN = "COOLDOWN"
    FAIL = "FAIL"

@dataclass
class SkillRuntimeState:
    state: SkillState = SkillState.FAIL
    reason: str = ""

@dataclass
class SkillAction:
    name: str
    key: str
    delay: int

    cx: int = 0
    cy: int = 0
    cr: Optional[RGB] = None

    p11x: int = 0
    p11y: int = 0
    p11r: Optional[RGB] = None

    runtime: SkillRuntimeState = field(default_factory=SkillRuntimeState)
    conditions: List["Condition"] = field(default_factory=list)

    def to_dict(self):
        return {
            "name": self.name,
            "key": self.key,
            "delay": self.delay,
            "cx": self.cx,
            "cy": self.cy,
            "cr": list(self.cr) if self.cr else None,
            "p11x": self.p11x,
            "p11y": self.p11y,
            "p11r": list(self.p11r) if self.p11r else None,
        }

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            key=d["key"],
            delay=d["delay"],
            cx=d.get("cx", 0),
            cy=d.get("cy", 0),
            cr=tuple(d["cr"]) if d.get("cr") else None,
            p11x=d.get("p11x", 0),
            p11y=d.get("p11y", 0),
            p11r=tuple(d["p11r"]) if d.get("p11r") else None,
        )
