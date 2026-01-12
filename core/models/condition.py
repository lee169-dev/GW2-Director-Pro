from dataclasses import dataclass
from enum import Enum

class ConditionType(Enum):
    ALWAYS = "ALWAYS"
    HP_BELOW = "HP_BELOW"
    BUFF_ACTIVE = "BUFF_ACTIVE"

@dataclass
class Condition:
    type: ConditionType
    value: float | str | None = None

    def evaluate(self, context) -> bool:
        if self.type == ConditionType.ALWAYS:
            return True
        return False
