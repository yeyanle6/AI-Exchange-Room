# 自动确认系统使用指南

## 概述

自动确认系统是AI-Exchange-Room的核心特性之一，它在自动化和用户控制之间取得完美平衡。

### 核心理念

**"倒计时5秒，没有用户干预时自动确认进行下一步"**

- ⏱️  **倒计时机制**：每个操作默认5秒后自动确认
- ⚡ **用户可干预**：倒计时期间随时可输入y/n
- 🚀 **批量支持**：可选择"全部是"或"全部否"
- 📝 **快速跳过**：按回车立即使用默认值

---

## 快速开始

### 1. 基本使用

```python
from src.utils import AutoConfirm

ac = AutoConfirm(timeout=5)

# 自动确认（5秒后自动选择"是"）
if ac.confirm("是否创建新文件？", auto_yes=True):
    create_file()

# 自动取消（5秒后自动选择"否"）
if ac.confirm("是否删除文件？", auto_yes=False):
    delete_file()
```

### 2. 快速确认函数

```python
from src.utils import quick_confirm

# 3秒倒计时，自动确认
if quick_confirm("是否保存？", timeout=3):
    save()
```

### 3. 批量确认

```python
from src.utils import BatchAutoConfirm

batch = BatchAutoConfirm(timeout=3)

for task in tasks:
    if batch.confirm(f"是否执行 {task}？"):
        execute(task)
```

用户可以选择：
- `y` - 确认当前操作
- `n` - 取消当前操作
- `a` - **全部确认**（后续所有操作自动确认）
- `x` - **全部取消**（后续所有操作自动取消）

---

## 交互式任务执行

### 启动交互式任务执行

```bash
# 执行项目的所有任务（5秒倒计时）
python src/execute_tasks.py ./projects/PRJ-ABC12345

# 使用自定义倒计时（3秒）
python src/execute_tasks.py ./projects/PRJ-ABC12345 --timeout 3

# 执行单个任务
python src/execute_tasks.py ./projects/PRJ-ABC12345 --task TASK-12345678

# 执行下一个待执行的任务
python src/execute_tasks.py ./projects/PRJ-ABC12345 --next
```

### 执行流程

```
开始任务
   ↓
┌──────────────────────────────────┐
│ 是否执行任务 [任务名称]？         │
│                                  │
│ [█████████░░░░░░░] 3秒           │
│                                  │
│ 请选择 [Y/n]:                     │
└──────────────────────────────────┘
   ↓
倒计时中（可随时输入y/n干预）
   ↓
倒计时结束 或 用户输入
   ↓
┌─ 确认 ──────────────┐
│  ✅ 执行任务         │
│  ⏳ 等待完成         │
│  📝 收集产出文件     │
└─────────────────────┘
   ↓
完成
```

---

## 使用场景

### 场景1：开发任务自动执行

**需求**：执行一系列开发任务，但保留人工审核的机会

```bash
# 启动交互式执行
python src/execute_tasks.py ./projects/PRJ-TODO-APP

# 系统会：
# 1. 显示下一个任务
# 2. 倒计时5秒
# 3. 用户可以：
#    - 什么都不做 → 自动确认并执行
#    - 输入 y → 立即确认
#    - 输入 n → 跳过此任务
#    - 按回车 → 立即使用默认值
```

### 场景2：批量文件操作

**需求**：创建多个文件，但希望控制哪些要创建

```python
from src.utils import BatchAutoConfirm

batch = BatchAutoConfirm(timeout=3)

files = ["README.md", "setup.py", ".gitignore", "requirements.txt"]

for file in files:
    if batch.confirm(f"创建文件 {file}？"):
        create_file(file)
        print(f"✅ 已创建: {file}")
```

**用户体验**：
- 第一个文件：倒计时3秒，或输入 `a` 选择"全部是"
- 后续文件：如果选择了"全部是"，自动创建所有文件

### 场景3：代码写入确认

**需求**：Claude Code生成代码后，自动写入文件（保留干预机会）

```python
from src.utils import AutoConfirm

ac = AutoConfirm(timeout=5)

def write_code_to_file(file_path, code):
    """写入代码到文件，带自动确认"""
    if ac.confirm(f"是否写入代码到 {file_path}？", auto_yes=True):
        with open(file_path, 'w') as f:
            f.write(code)
        print(f"✅ 已写入: {file_path}")
        return True
    else:
        print(f"⏭️  已跳过: {file_path}")
        return False
```

**工作流程**：
1. Claude Code生成代码
2. 显示确认提示
3. 倒计时5秒
4. 如果用户没有干预 → 自动写入
5. 如果用户输入 `n` → 跳过写入

---

## 高级用法

### 1. 自定义倒计时

```python
# 紧急操作：更短的倒计时
ac = AutoConfirm(timeout=2)
ac.confirm("删除临时文件？", auto_yes=True)

# 重要操作：更长的倒计时
ac = AutoConfirm(timeout=10)
ac.confirm("是否发布到生产环境？", auto_yes=False)
```

### 2. 确认并执行

```python
from src.utils import AutoConfirm

ac = AutoConfirm()

def deploy_to_production():
    print("🚀 部署中...")
    # ... 部署逻辑

# 确认后自动执行
ac.confirm_action(
    action_name="部署到生产环境",
    action_func=deploy_to_production,
    timeout=10,
    auto_yes=False  # 重要操作不自动确认
)
```

### 3. 集成到工作流

```python
from src.core import TaskExecutor

# 创建任务执行器（3秒倒计时）
executor = TaskExecutor(project, auto_confirm_timeout=3)

# 执行所有任务
stats = executor.execute_all_tasks_interactive()

print(f"完成: {stats['completed']}/{stats['total']}")
```

---

## 最佳实践

### 1. 倒计时时长建议

| 操作类型 | 推荐倒计时 | 默认动作 | 理由 |
|---------|-----------|---------|------|
| 创建文件 | 3-5秒 | 自动确认 | 低风险操作 |
| 修改文件 | 5-7秒 | 自动确认 | 需要时间查看 |
| 删除文件 | 7-10秒 | 自动取消 | 高风险操作 |
| 部署发布 | 10-15秒 | 自动取消 | 关键操作 |

### 2. 批量操作策略

**推荐做法**：
```python
batch = BatchAutoConfirm(timeout=3)

# 先显示所有将要执行的操作
print("将要执行的操作：")
for i, task in enumerate(tasks, 1):
    print(f"  {i}. {task}")

print("\n提示：可选择 [a]全部是 或 [x]全部否\n")

# 然后逐个确认
for task in tasks:
    if batch.confirm(task):
        execute(task)
```

### 3. 错误处理

```python
from src.utils import AutoConfirm

ac = AutoConfirm()

try:
    if ac.confirm("是否执行危险操作？", auto_yes=False):
        dangerous_operation()
except KeyboardInterrupt:
    print("\n操作已被用户中断")
except Exception as e:
    print(f"操作失败: {e}")
    # 记录日志
```

---

## 演示示例

运行完整的演示脚本：

```bash
python demo_auto_confirm.py
```

这将展示：
1. 基本自动确认
2. 快速确认函数
3. 批量确认
4. 带操作的确认
5. 完整的任务执行流程

---

## 用户交互示例

### 示例1：自动确认

```
是否创建文件 test.txt？
将在 5 秒后自动确认 (输入 y/n 可立即选择，回车跳过倒计时)
请选择 [Y/n]:
⏳ [██████████████████░░░░░░░░░░] 3秒
```

**如果用户什么都不做**：
```
⏱ 倒计时结束，自动确认
✅ 文件已创建: test.txt
```

**如果用户输入 `n`**：
```
✗ 用户选择：取消
⏭️ 操作已跳过
```

### 示例2：批量操作

```
[1/5]
创建目录 src/
选项: [y]是 [n]否 [a]全部是 [x]全部否 [回车]自动确认
请选择: a

✓✓✓ 全部确认（后续操作将自动确认）

[2/5]
创建目录 tests/
✓ 自动确认（全部是模式）

[3/5]
创建文件 README.md
✓ 自动确认（全部是模式）

...
```

---

## 与Claude Code协作

### 典型工作流

```
用户:
  执行下一个任务

  ↓

系统:
  📋 任务: 创建数据模型
  [显示任务详细指令]
  是否开始执行？ [5秒倒计时]

  ↓

用户:
  [不操作，等待自动确认]
  或
  [输入 y 立即开始]

  ↓

系统:
  ✅ 任务开始
  请按照指令完成开发...

  ↓

Claude Code:
  [读取指令]
  [生成代码]
  [显示代码预览]

  ↓

系统:
  是否写入文件？ [5秒倒计时]

  ↓

用户:
  [不操作 → 自动写入]
  或
  [查看代码后决定 y/n]

  ↓

完成！
```

---

## 配置建议

### 针对不同用户类型

**新手用户**：
```python
# 更长的倒计时，更多思考时间
executor = TaskExecutor(project, auto_confirm_timeout=10)
```

**熟练用户**：
```python
# 较短的倒计时，提高效率
executor = TaskExecutor(project, auto_confirm_timeout=3)
```

**完全自动化**：
```python
# 最短倒计时，接近自动执行
executor = TaskExecutor(project, auto_confirm_timeout=1)
```

---

## 常见问题

**Q: 如果我想完全跳过确认怎么办？**

A: 选择"全部是"模式（输入`a`），后续所有操作将自动确认。

**Q: 倒计时可以暂停吗？**

A: 不能暂停，但可以按回车立即使用默认值跳过倒计时。

**Q: 如何修改默认倒计时时长？**

A: 创建AutoConfirm时指定timeout参数，或使用`--timeout`命令行参数。

**Q: 能否在倒计时中查看更多信息？**

A: 可以。任务指令在倒计时前就已显示完整，您有充足时间查看。

---

## 总结

自动确认系统的核心价值：

✅ **效率**：大部分操作自动执行，无需手动确认
✅ **控制**：关键时刻可以干预，保留人工决策权
✅ **灵活**：支持批量、单个、快速等多种模式
✅ **直观**：倒计时进度条清晰展示剩余时间

这正是"AI辅助开发"的最佳实践 —— **在自动化与控制之间取得平衡**。
