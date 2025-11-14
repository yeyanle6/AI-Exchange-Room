# rPPG心率检测插件

基于MediaPipe Face Mesh (468特征点) 的非接触式心率检测插件

## 功能特性

- ✅ **实时心率检测** - 通过普通摄像头检测心率
- ✅ **精确ROI追踪** - 基于468个面部特征点的精确皮肤区域定位
- ✅ **多算法支持** - GREEN, G-R, CHROM, POS, ICA
- ✅ **动态可视化** - 实时ROI标记、信号波形、频谱分析
- ✅ **数据性能面板** - 5个标签页展示详细数据
- ✅ **性能监控** - CPU、FPS、内存实时监控
- ✅ **数据导出** - 支持CSV/JSON格式导出

## 技术架构

### 核心模块 (core/)
- `face_detector.py` - MediaPipe Face Mesh人脸检测
- `roi_tracker.py` - 基于468特征点的ROI追踪
- `signal_extractor.py` - RGB信号提取
- `rppg_algorithms.py` - rPPG算法（GREEN/CHROM/POS等）
- `signal_processor.py` - 信号处理（滤波/FFT）
- `heartrate_calculator.py` - 心率计算

### GUI模块 (gui/)
- `main_widget.py` - 主界面
- `data_panel.py` - 数据性能面板（5标签页）

### 工具模块 (utils/)
- `performance_monitor.py` - 性能监控
- `data_recorder.py` - 数据记录和导出

## 依赖安装

```bash
pip install mediapipe opencv-python numpy scipy PyQt5 pyqtgraph psutil
```

## 使用方法

1. 启动工具箱
2. 点击"rPPG心率检测"插件
3. 点击"开始检测"
4. 保持面部正对摄像头，静止不动
5. 等待10秒左右，心率将稳定显示

## 算法说明

### POS算法（推荐）
- **准确度**: 最高
- **抗干扰性**: 最强
- **适用场景**: 通用推荐

### CHROM算法
- **准确度**: 高
- **抗干扰性**: 强
- **适用场景**: 光照变化环境

### GREEN算法
- **准确度**: 中等
- **抗干扰性**: 一般
- **适用场景**: 理想条件演示

## ROI模式

### 前额+脸颊（推荐）
- 使用前额、左脸颊、右脸颊三个区域
- 准确度最高
- 抗运动性好

### 仅前额
- 只使用前额区域
- 速度快
- 适合静止场景

### 全脸
- 使用整个面部
- 数据量大
- 研究用途

## 性能指标

- **心率误差**: ±5 BPM
- **响应时间**: <10秒
- **CPU占用**: <30%
- **FPS**: ≥20fps

## 注意事项

1. **光照条件**: 需要充足稳定的光照
2. **保持静止**: 减少头部运动
3. **正脸朝向**: 保持面部正对摄像头
4. **距离**: 距离摄像头40-60cm

## 文件结构

```
plugins/rppg-detector/
├── plugin.py              # 插件入口
├── README.md             # 本文档
├── config/
│   └── config.py         # 配置文件
├── core/                 # 核心算法模块
│   ├── face_detector.py
│   ├── roi_tracker.py
│   ├── signal_extractor.py
│   ├── rppg_algorithms.py
│   ├── signal_processor.py
│   └── heartrate_calculator.py
├── gui/                  # GUI模块
│   ├── main_widget.py
│   └── data_panel.py
└── utils/                # 工具模块
    ├── performance_monitor.py
    └── data_recorder.py
```

## 开发者信息

- **基于**: MediaPipe Face Mesh
- **算法参考**: Wang et al. (IEEE TBME 2017)
- **框架**: PyQt5 + OpenCV + NumPy/SciPy
