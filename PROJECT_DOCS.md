GW2 Director Pro (Qt Edition) 项目说明文档
版本: 3.2 Pro   最后更新: 2026-01-12   运行环境: Python 3.12 + PySide6 (Qt) + PyDirectInput

1. 概述 (Overview)
GW2 Director Pro 是一款专为《激战2》（Guild Wars 2）设计的游戏辅助工具，旨在提升玩家的游戏体验。

本工具的主要功能包括 "智能化" 的技能施放、状态监控与战斗执行等。通过对游戏角色的精准控制，帮助玩家更高效地进行游戏操作。

开发背景
鉴于市面上缺乏针对《激战2》的高质量辅助工具，因此开发了GW2 Director Pro。希望通过该工具，能够让更多的玩家享受到游戏的乐趣。

技术实现
本工具主要基于以下技术实现：

图像识别：利用 PIL.ImageGrab 实现对屏幕的实时抓取，并通过颜色匹配获取角色的状态信息。

状态引擎：通过分析游戏的状态变化，智能判断角色的准备与冷却状态（Ready/Cooldown）。

脚本引擎：通过 pydirectinput 实现对游戏的精准输入，达到自动化操作的目的。

界面呈现：采用 PySide6 设计并实现用户界面，并针对 Apple 平台进行了适配。

2. 快速开始 (Quick Start)
环境准备
确保已安装以下软件：

Python 3.12 或更高版本

相关依赖库：

Bash

pip install PySide6 pydirectinput keyboard pillow pyautogui
代码获取
将项目代码下载到本地：

Bash

git clone https://github.com/your-repo/gw2-director-pro-qt.git
运行项目
进入项目目录，运行主程序：

Bash

python app.py
界面说明
主界面分为四个区域：

状态栏：显示当前角色状态信息，如生命值、能量值等。

技能栏：显示可用技能及其冷却时间。

操作区域：提供一键施放技能、自动战斗等功能按钮。

设置菜单：用于配置软件参数，如热键设置、技能配置等。

使用指南
新手指导：首次运行时，软件会自动弹出新手指导，带您了解各个功能模块。

手动设置：可在设置菜单中手动配置热键、技能等参数。

状态监控：软件会实时监控角色状态，并在状态变化时通过视觉或听觉提示玩家。

3. 架构设计 (Architecture)
本项目采用经典的 MVC 架构设计模式，主要分为以下三个部分：

UI 层（ui/）：负责与用户的直接交互，接收用户输入并反馈信息。

核心层（core/）：负责实现游戏逻辑，包括状态监控、技能施放等。

数据层（data/）：负责存取游戏数据及用户配置。

模块间通过信号与槽（Signals/Slots）机制进行通信，确保各模块间的解耦与协作。

4. 文件结构说明 (File Structure)
为了便于开发与维护，项目文件结构如下：

?? 根目录
app.py: 程序入口，负责初始化 QApplication 并启动主窗口。

config.json: 存储用户配置，如热键设置、技能配置等。

?? core/ (核心逻辑)
config.py: 配置文件，负责读取与写入 JSON 格式的配置数据。

models/:

skill.py: 定义技能动作（SkillAction）类，描述技能的基本属性及行为。

condition.py: 定义状态条件类，用于描述角色在特定状态下的行为。

engine/:

engine.py: 核心引擎，负责游戏逻辑的执行，包括战斗循环（Combat Loop）。

evaluator.py: 评估器，负责判断角色的当前状态及可执行的操作。

calibration.py: 校准模块，负责对软件进行初始设置与参数校准。

?? ui/ (用户界面)
main_window.py: 主窗口，程序的主要交互界面。

overlay.py: 悬浮窗，用于游戏中实时显示角色状态及其他信息。

constants.py: 常量定义，存放程序中用到的各种常量值，如颜色值、坐标值等。

widgets/:

modern.py: 自定义按钮组件，提供比默认按钮更丰富的样式。

skill_card.py: 技能卡片组件，用于在界面上显示技能信息。

skill_editor.py: 技能编辑器，用于编辑与配置技能参数。

log_panel.py: 日志面板，用于显示程序运行日志及错误信息。

panels/:

skill_list.py: 技能列表面板，显示所有可用技能及其状态。

5. 主要流程 (Key Workflows)
A. 程序启动
app.py -> MainWindow 初始化 -> Engine 启动

B. 状态监控
Engine -> on_coords_update -> UI 更新

C. 战斗循环 (Combat Loop)
核心在于 core/engine/engine.py 的 _combat_loop 方法：

快照 (Snapshot): 定期获取角色状态快照。

推送 (Push): 将状态变化推送至 UI 层，更新界面显示。

执行 (Execute): 根据当前状态执行相应的技能或操作。

6. 扩展指南 (Extension Guide)
如需对本工具进行功能扩展，可参考以下步骤：

新增技能支持
修改 Model: 在 core/models/skill.py 中新增技能属性或方法。

修改 UI: 在 ui/widgets/skill_editor.py 中新增对应的编辑控件。

修改 Logic: 在 core/engine/evaluator.py 中新增技能的评估逻辑。

新增界面主题
仅需修改 ui/widgets/modern.py 中的样式表（stylesheet），即可实现全局主题更换。

7. 常见问题 (FAQ)
Q: 为什么 F8 无效？

A: 请检查是否赋予了程序足够的权限，以及游戏是否在窗口化模式下运行。

Q: 校准失败，怎么办？

A: 请确保游戏窗口已打开，并且在游戏主界面进行校准。

Q: 为什么我的技能没有冷却时间？

A: 请检查技能配置是否正确，以及游戏内是否存在网络延迟。

8. 说明
已将此文档内容和此文件保存为 UTF-8 带 BOM（UTF-8 BOM），以避免在某些编辑器或平台上出现中文乱码。