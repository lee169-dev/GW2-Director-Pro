import json
import os
from core.models.skill import SkillAction

def load_config(path="config.json"):
    if not os.path.exists(path):
        return {}, {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    global_coords = data.get("global_coords", {})
    profiles = {}

    for name, skills in data.get("profiles", {}).items():
        profiles[name] = [SkillAction.from_dict(s) for s in skills]

    return global_coords, profiles


def save_config(path, global_coords, profiles):
    data = {
        "global_coords": global_coords,
        "profiles": {
            name: [s.to_dict() for s in skills]
            for name, skills in profiles.items()
        }
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
