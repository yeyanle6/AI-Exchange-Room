# 🧰 AI ToolBox - AI驱动的智能工具箱

## 项目概述

**AI ToolBox** 是一个可扩展的AI工具集合平台，采用插件化架构，方便添加和管理各种AI驱动的工具。

### 核心特性

- 🔌 **插件化架构** - 每个工具作为独立插件，易于扩展
- 🎨 **统一界面** - 现代化的GUI，所有工具共享一致的用户体验
- 🚀 **快速启动** - 一键启动，自动发现和加载所有插件
- 📦 **模块化设计** - 插件间相互独立，互不影响
- 🔧 **易于开发** - 简单的插件接口，方便开发新工具

## 已集成工具

### 1. AI-Exchange-Room 🎯
**AI驱动的自动编程系统**

- 多角色需求分析（6个AI专家）
- 智能任务分解
- 任务看板管理
- 项目监控仪表板

[查看详细文档](plugins/ai-exchange-room/README.md)

## 架构设计

```
AI-ToolBox/
├── toolbox_main.py              # 工具箱主程序
├── src/
│   └── toolbox/
│       ├── core/
│       │   ├── plugin_manager.py    # 插件管理器
│       │   ├── plugin_interface.py  # 插件接口定义
│       │   └── app_manager.py       # 应用管理
│       └── gui/
│           ├── main_window.py       # 工具箱主窗口
│           └── plugin_panel.py      # 插件面板
│
├── plugins/                     # 插件目录
│   ├── ai-exchange-room/       # AI-Exchange-Room插件
│   │   ├── plugin.py           # 插件入口
│   │   ├── icon.png            # 插件图标
│   │   └── ... (原有代码)
│   │
│   └── template/               # 插件模板
│
├── requirements.txt
└── README.md
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动工具箱
python toolbox_main.py
```

## 插件开发指南

### 创建新插件

1. 在 `plugins/` 目录下创建插件文件夹
2. 实现插件接口
3. 重启工具箱自动加载

### 插件接口

```python
from src.toolbox.core.plugin_interface import PluginInterface

class MyPlugin(PluginInterface):
    def get_name(self) -> str:
        return "我的工具"

    def get_description(self) -> str:
        return "工具描述"

    def get_icon(self) -> str:
        return "path/to/icon.png"

    def get_widget(self) -> QWidget:
        return MyToolWidget()
```

## 许可证

MIT License
