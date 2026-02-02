# 🌲 UAV-LiDAR 单木识别与树木信息自动测量

<div align="center">

![Version](https://img.shields.io/badge/Version-2.2-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-Academic-orange)

**基于无人机载激光雷达点云数据的森林调查自动化工具**

[English](README_EN.md) | [日本語](README_JP.md)

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [项目结构](#-项目结构) • [使用指南](#-使用指南) • [验证工具](#-验证工具)

</div>

---

## 📋 项目概述

本项目实现了从原始 LiDAR 点云到单木参数提取的完整流程，支持：
- 🌳 **单木检测**: 基于 RANSAC 圆柱拟合的树干识别
- 📏 **DBH 提取**: 胸径（Diameter at Breast Height）自动测量
- 📍 **空间定位**: 每棵树的 UTM 坐标输出
- 📊 **可视化**: 2D 分布图 + 3D 叠加图 + 交互式预览
- ✅ **验证工具**: 分层抽样 + RMSE 统计

**研究方向**: UAV搭載レーザ（RCヘリ含む）点群データによる単木識別と樹木情報の自動計測

---

## 🚀 快速开始

```bash
# 1. 进入项目目录
cd /Users/zyc/Downloads/Niigata_Research_Prep

# 2. 启动 GUI（推荐）
./03_Scripts/run.sh

# 3. 在 GUI 中:
#    - 选择输入点云 (.ply)
#    - 调整参数（或使用默认值）
#    - 点击 "开始检测"
```

---

## ✨ 功能特性

| 功能 | 描述 | 工具 |
|------|------|------|
| **GUI 交互界面** | 分页设计，检测+可视化一体 | `tools/gui_app.py` |
| **命令行检测** | 批量处理，无需界面 | `core/detect_cylinders_v2.py` |
| **3D 可视化** | Matplotlib 静态图 + Open3D 交互 | `tools/visualize_forest.py` |
| **精度验证** | 分层抽样 + RMSE/MAE 计算 | `tools/generate_validation_sample.py` |
| **生物量分析** | 径阶分布、碳储量估算 | `analysis/analyze_forest_data.py` |

---

## 📁 项目结构

```
Niigata_Research_Prep/
├── 00_Raw_Data/                    # 原始 LiDAR 数据 (.laz)
│
├── 01_Processed/                   # 预处理后的点云
│
├── 02_Screenshots/                 # 学习过程截图
│
├── 03_Scripts/                     # 🐍 核心脚本
│   ├── run.sh                     # 统一入口
│   ├── core/                      # 核心算法
│   │   ├── tree_utils.py          # RANSAC 算法核心
│   │   └── detect_cylinders_v2.py # CLI 检测
│   ├── pipelines/                 # 完整流程
│   ├── tools/                     # 工具与可视化
│   │   ├── gui_app.py             # GUI 主程序
│   │   └── visualize_forest.py    # 可视化生成
│   ├── analysis/                  # 数据分析
│   └── experiments/               # 实验对比
│
├── 04_Results/                     # 输出结果
│   ├── figures/                   # 图件 (.png)
│   └── tables/                    # 数据表 (.csv)
│
├── docs/                           # � 项目核心文档
│   ├── technical/                 # 技术原理与结构
│   ├── reports/                   # � 实验报告与学习规划
│   ├── research_master_guideline.html  # 🏆 研究总纲领 (入口)
│   └── career_skill_mapping.md         # 技能-职业映射
│
└── README.md                       # 本文档
```

---

## 🔧 使用指南

### 方式一：GUI 界面（推荐）

```bash
./03_Scripts/run.sh
```

**🌲 检测标签页**:
1. 选择输入点云文件 (`.ply`)
2. 设置输出 CSV 路径
3. 调整 RANSAC 参数（可选）
4. 点击 "开始检测"
5. 勾选 "自动可视化" 可在完成后自动生成图像

**🎨 可视化标签页**:
1. 选择点云和结果目录
2. 点击 "生成可视化图表"
3. 点击 "交互式 3D 预览" 打开 Open3D 窗口

### 方式二：命令行

```bash
# 检测
python 03_Scripts/core/detect_cylinders_v2.py

# 可视化
python 03_Scripts/tools/visualize_forest.py <path_to_ply>
```

---

## ⚙️ 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| Distance Threshold | 0.06 m | 点到圆柱轴的最大距离 |
| Min Points | 50 | 一个圆柱体最少点数 |
| Min Radius | 0.03 m | 最小半径 (3 cm) |
| Max Radius | 0.8 m | 最大半径 (80 cm) |
| Min Height | 1.0 m | 最小高度 |
| Max Iterations | 100 | 最多检测树木数量 |

---

## ✅ 验证工具

### 1. 生成分层抽样验证表

```bash
python 03_Scripts/tools/generate_validation_sample.py
```

输出: `validation_sample.csv`（按 DBH 大小分层抽取 9 棵树）

### 2. 在 CloudCompare 中验证

使用坐标定位每棵树，手动测量直径，填入 `Manual_DBH_cm` 列

### 3. 计算误差统计

```bash
python 03_Scripts/analysis/calculate_validation_stats.py
```

输出: RMSE, MAE, 平均误差等指标

---

## 📊 输出格式

### CSV 文件列说明

| 列名 | 单位 | 说明 |
|------|------|------|
| Radius (m) | 米 | 树干半径 |
| Diameter_DBH (cm) | 厘米 | 胸径 |
| Height (m) | 米 | 拟合高度（注：受限于点云密度，可能偏高）|
| Num_Points | 个 | 点云数量 |
| X, Y, Z | 米 | UTM 坐标 |

---

## ⚠️ 已知限制

| 问题 | 原因 | 建议解决方案 |
|------|------|--------------|
| 高度值异常 | 稀疏点云导致 RANSAC 拟合偏差 | 使用 CHM（冠层高度模型）替代 |
| 需要手动预处理 | CloudCompare 切片/滤波 | 未来集成自动化流程 |
| 内存占用大 | 大型点云加载 | 分块处理 |

---

## 📚 技术栈

- **点云处理**: Open3D, CloudCompare
- **算法**: RANSAC, PCA (scikit-learn)
- **可视化**: Matplotlib, Open3D
- **界面**: Tkinter
- **数据分析**: Pandas, NumPy

---

## 📈 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v2.2 | 2026-02-02 | 项目结构重构：模块化拆分、文档归档整理 |
| v2.1 | 2026-01-27 | 分页 GUI、验证工具、3D 预览、显示高度截断 |
| v2.0 | 2026-01-25 | RANSAC 检测、基础 GUI |
| v1.0 | 初始 | CloudCompare 手动流程 |

---

## 👤 项目信息

- **创建者**: zyc
- **研究方向**: 森林 UAV LiDAR 单木识别
- **最后更新**: 2026-02-02

---

## 📄 许可证

本项目仅供学术研究使用。
