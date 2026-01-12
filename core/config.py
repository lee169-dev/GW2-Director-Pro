# -*- coding: utf-8 -*-
import json
import os
from core.models.skill import SkillAction

def load_config(path="config.json"):
	"""
	加载配置文件

	参数:
		path -- 配置文件路径，默认为 "config.json"

	返回:
		global_coords -- 全局坐标配置
		profiles -- 技能配置文件，包含各个角色的技能设置

	说明:
		- 使用 utf-8-sig 读取以兼容带 BOM 的 JSON 文件
		- 缺失文件时创建默认空配置文件
		- JSON 解析失败时尝试去除 BOM 再次解析，仍失败则返回空结构
	"""
	if not os.path.exists(path):
		default = {"global_coords": {}, "profiles": {}}
		with open(path, "w", encoding="utf-8-sig") as f:
			json.dump(default, f, indent=2, ensure_ascii=False)
		return {}, {}

	try:
		with open(path, "r", encoding="utf-8-sig") as f:
			data = json.load(f)
	except json.JSONDecodeError:
		try:
			with open(path, "r", encoding="utf-8") as f:
				text = f.read()
			text = text.lstrip('\ufeff')
			data = json.loads(text)
		except Exception as e:
			print(f"Failed to parse config file '{path}': {e}")
			return {}, {}

	global_coords = data.get("global_coords", {})
	profiles = {}

	for name, skills in data.get("profiles", {}).items():
		profiles[name] = [SkillAction.from_dict(s) for s in skills]

	return global_coords, profiles


def save_config(path, global_coords, profiles):
	"""
	保存配置文件

	参数:
		path -- 配置文件路径
		global_coords -- 全局坐标配置
		profiles -- 技能配置文件，包含各个角色的技能设置

	说明:
		- 使用 utf-8-sig 写出，确保文件带 BOM（某些编辑器需要）
	"""
	data = {
		"global_coords": global_coords,
		"profiles": {
			name: [s.to_dict() for s in skills]
			for name, skills in profiles.items()
		}
	}
	with open(path, "w", encoding="utf-8-sig") as f:
		json.dump(data, f, indent=2, ensure_ascii=False)
