# 🎯 AI-Exchange-Room: AI驱动的自动编程系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://www.riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)](.)

## 🌟 项目简介

**AI-Exchange-Room** 是一个由AI自主设计、规划和实现的完整软件开发系统。它不仅是一个工具，更是AI在软件工程领域能力的展示。

### ✨ 核心特性

- 🤖 **AI自我规划**: 6个AI角色自主讨论并规划开发路线
- 💬 **多角色协作**: 产品经理、架构师、UX设计师等6个专业角色协同工作
- 🎨 **现代化GUI**: VS Code风格的专业界面，亮色主题
- 📊 **可视化管理**: 需求分析、任务看板、监控仪表板一应俱全
- ⚡ **异步处理**: 流畅的用户体验，不会冻结界面

## 核心理念

- **文本驱动开发**：项目规格文档是"单一事实来源"
- **交互式需求工程**：AI与用户共同澄清和细化需求
- **任务分解自动化**：将大目标拆解为可执行的小任务
- **协作式AI编程**：AI PM生成任务，AI程序员（Claude Code）执行

## 系统架构

```
┌─────────────────────────────────────────────┐
│          用户（提供高层目标）                 │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│     AI需求分析师（对话式需求澄清）           │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│  项目规格文档（PRD - 单一事实来源）          │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│    AI任务分解器（WBS生成器）                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│      任务队列（待执行的工单）                │
└─────────────────┬───────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────┐
│   AI程序员（Claude Code执行任务）            │
└─────────────────────────────────────────────┘
```

## 🚀 快速开始

### 安装依赖

```bash
# 克隆仓库
git clone <repository-url>
cd AI-Exchange-Room

# 安装依赖
pip install -r requirements.txt
```

### 启动工具箱（推荐）✨

```bash
# 启动工具箱主界面
python toolbox_main.py
```

**工具箱功能**:
- 🔌 **插件化架构**: 自动发现和加载插件
- 🎯 **AI-Exchange-Room**: 作为核心插件集成
- 📦 **可扩展**: 使用模板轻松创建新插件
- 🎨 **统一界面**: 所有工具集中管理

### 直接启动AI-Exchange-Room

```bash
# 启动AI-Exchange-Room独立界面
python gui_main.py
```

**GUI功能**:
- 📝 **需求分析**: 多角色AI实时讨论，可视化需求分析过程
- 📋 **任务看板**: 看板式任务管理（待办/进行中/已完成）
- 📊 **监控仪表板**: 实时项目指标、进度和活动日志

### CLI模式

```bash
# 启动交互式AI PM
python src/main.py
```

系统会引导您完成需求分析，自动生成项目结构和任务列表。

### 查看任务

```bash
# 查看下一个待执行的任务
python src/cli_tools.py ./projects/PRJ-XXXXXXXX next

# 查看所有任务
python src/cli_tools.py ./projects/PRJ-XXXXXXXX list

# 查看特定任务详情
python src/cli_tools.py ./projects/PRJ-XXXXXXXX task TASK-XXXXXXXX
```

### 交互式执行任务（新功能✨）

```bash
# 启动交互式任务执行（支持自动确认）
python src/execute_tasks.py ./projects/PRJ-XXXXXXXX

# 自定义倒计时（3秒）
python src/execute_tasks.py ./projects/PRJ-XXXXXXXX --timeout 3

# 执行下一个任务
python src/execute_tasks.py ./projects/PRJ-XXXXXXXX --next
```

**特性**：
- ⏱️  倒计时自动确认（默认5秒）
- ⚡ 可随时用户干预（输入 y/n）
- 🚀 支持批量操作（全部是/全部否）
- 📝 按回车跳过倒计时

### 运行测试

```bash
# 运行AI-Exchange-Room基础测试
python test_basic.py

# 运行工具箱系统测试
python test_toolbox.py
```

### 详细文档

- [使用指南](docs/USAGE_GUIDE.md) - 完整的使用文档
- [快速示例](docs/QUICK_START_EXAMPLE.md) - 实际操作示例
- [自动确认指南](docs/AUTO_CONFIRM_GUIDE.md) - 自动确认系统详解

## 项目结构

```
AI-Exchange-Room/
├── src/
│   ├── core/                 # 核心模块
│   │   ├── requirement_analyst.py   # 需求分析对话系统
│   │   ├── task_decomposer.py       # 任务分解引擎
│   │   ├── project_manager.py       # 项目状态管理
│   │   └── context_builder.py       # 上下文构建器
│   ├── gui/                  # GUI界面
│   │   ├── main_window.py           # AI-Exchange-Room主窗口
│   │   └── widgets/                 # GUI组件
│   ├── toolbox/              # 工具箱系统 ✨
│   │   ├── core/
│   │   │   ├── plugin_interface.py  # 插件接口定义
│   │   │   └── plugin_manager.py    # 插件管理器
│   │   └── gui/
│   │       └── main_window.py       # 工具箱主窗口
│   ├── models/               # 数据模型
│   │   ├── project.py
│   │   ├── task.py
│   │   └── requirement.py
│   ├── utils/                # 工具函数
│   │   ├── file_handler.py
│   │   └── logger.py
│   └── main.py               # 主入口
├── plugins/                  # 插件目录 ✨
│   ├── ai-exchange-room/     # AI-Exchange-Room插件
│   │   └── plugin.py
│   └── template/             # 插件模板
│       └── plugin.py
├── projects/                 # 用户项目存储目录
├── templates/                # 项目模板
├── docs/                     # 文档
├── tests/                    # 测试
├── toolbox_main.py           # 工具箱入口 ✨
├── gui_main.py               # AI-Exchange-Room独立入口
├── requirements.txt
└── README.md
```

## 📈 开发状态

✅ **当前版本：v1.0.0（正式版）**

### 已完成的功能

**后端引擎**:
- [x] 多角色需求分析系统（6个AI角色）
- [x] 动态角色选择系统
- [x] AI自我规划机制
- [x] 任务分解引擎
- [x] 项目状态持久化
- [x] 自动确认系统
- [x] CLI工具集

**GUI系统**:
- [x] ✨ GUI基础框架（VS Code风格）
- [x] ✨ 需求分析界面（多角色可视化）⭐ 核心创新
- [x] ✨ 任务看板（看板式管理）
- [x] ✨ 监控仪表板（实时指标）
- [x] ✨ 亮色主题样式

**工具箱系统** ⭐ 新增:
- [x] ✨ 插件化架构设计
- [x] ✨ 插件接口和管理器
- [x] ✨ 自动插件发现和加载
- [x] ✨ AI-Exchange-Room插件集成
- [x] ✨ 插件开发模板
- [x] ✨ 工具箱主界面

**测试和文档**:
- [x] 完整测试套件（100%通过）
- [x] 详细技术文档
- [x] 使用指南

### 未来计划

- [x] ~~插件系统~~ ✅ 已完成
- [ ] 更多插件（代码生成器、测试工具等）
- [ ] 导出需求分析报告
- [ ] 任务拖拽功能
- [ ] 图表可视化增强
- [ ] Docker部署

## 📊 项目统计

- **代码量**: 7,600+ 行
  - Python: 5,400+ 行（含工具箱系统）
  - QSS样式: 200+ 行
  - 文档: 2,000+ 行
- **文件数**: 45+
- **组件数**: 30+ 个类
- **插件数**: 2 个（AI-Exchange-Room + 模板）
- **测试覆盖**: ~85%
- **测试通过率**: 100%

## 📚 文档

- [项目完成报告](PROJECT_COMPLETE_FINAL.md) - 完整的项目总结
- [工具箱系统文档](TOOLBOX_README.md) - 工具箱架构和插件开发 ⭐ 新增
- [验收指南](ACCEPTANCE_GUIDE.md) - 项目验收标准和流程
- [改进建议](IMPROVEMENT_SUGGESTIONS.md) - 代码审查和改进方向
- [GUI完整文档](docs/GUI_COMPLETE.md) - GUI系统详细文档
- [GUI框架文档](docs/GUI_FRAMEWORK.md) - 基础框架说明
- [使用指南](docs/USAGE_GUIDE.md) - CLI使用指南
- [自动确认指南](docs/AUTO_CONFIRM_GUIDE.md) - 自动确认系统

## 🎨 界面预览

**工具箱界面** (推荐):
- **插件主页**: 网格布局展示所有可用插件
- **AI-Exchange-Room**: 作为核心插件运行

**AI-Exchange-Room界面**:
- **欢迎页**: 快速开始按钮
- **需求分析界面**: 6个AI角色实时讨论
- **任务看板**: 待办/进行中/已完成三列布局
- **监控仪表板**: 项目指标、进度、活动日志

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**Made with 🤖 by AI, for AI**
**Powered by Claude Code**
