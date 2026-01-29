# 🌲 LiDAR 树木检测工具箱手册 (LiDAR Tree Detection Toolbox Manual)

这份手册详细介绍了如何使用本工具箱从 LiDAR 点云数据中检测树木（圆柱体）并进行可视化。本工具箱已经过优化，提供了统一的 `run.sh` 脚本来管理所有功能。

## 📁 文件概览

- **`run.sh`**: 核心启动脚本。这是你唯一需要运行的文件。
- **`gui_app.py`**: 图形用户界面 (GUI) 程序，用于参数调整和可视化检测。
- **`detect_cylinders_v2.py`**: 命令行 (CLI) 检测脚本，适合批量处理。
- **`visualize_forest.py`**: 结果可视化脚本，生成 3D 覆盖图和空间分布图。
- **`tree_utils.py`**: 共享算法库，包含核心的 RANSAC 检测逻辑。

---

## 🚀 快速开始

所有的功能都可以通过 `./run.sh` 脚本来调用。

### 1. 启动 GUI（推荐）
这是最简单的使用方式。v2.1 版本引入了分页界面，集成了检测和可视化功能。
```bash
./run.sh
# 或者
./run.sh gui
```

**GUI 使用流程：**

**🌲 标签页 1：树木检测**
1.  **选择输入文件**：点击"浏览..."选择 `.ply` 或 `.laz` 点云文件。
2.  **设置输出路径**：默认会自动生成。
3.  **调整参数**：根据需要调整 RANSAC 参数。
4.  **开始检测**：点击"▶ 开始检测"。
5.  **自动可视化**：勾选"检测完成后自动切换到可视化"，程序会在检测结束后自动跳转到第二页并生成图表。

**🎨 标签页 2：结果可视化**
如果你已经有检测结果（CSV文件），可以直接使用此页面生成图表。
1.  **选择点云文件**：原始的点云数据。
2.  **选择结果目录**：包含 `tree_positions.csv`（或生成的 CSV）的文件夹。
3.  **生成图表**：点击"🎨 生成可视化图表"。
4.  **查看结果**：生成的 3D 覆盖图和分布图会自动打开。

### 2. 命令行检测
如果你需要在服务器上运行，或需要批量处理，可以使用命令行模式。
```bash
./run.sh detect
```
*注意：命令行模式默认使用脚本内硬编码的路径。若需修改输入/输出路径，请直接编辑 `detect_cylinders_v2.py` 文件顶部的配置部分。*

### 3. 结果可视化
检测完成后，可以生成 3D 可视化图表。
```bash
./run.sh visualize
```
此命令会读取 `04_Results/tree_positions.csv`（默认路径）并生成可视化图片到 `04_Results/figures`。

**指定输入文件：**
如果默认路径不正确，你可以手动指定点云文件路径：
```bash
./run.sh visualize "path/to/your/file.ply"
```

---

## ⚙️ 参数调优指南

在 GUI 中，你可以调整以下核心参数来优化检测效果：

| 参数名 | 默认值 | 说明 |
| :--- | :--- | :--- |
| **Distance Threshold** | 0.06 m | **距离阈值**。点到圆柱模型的最大距离。值越小，拟合越紧密但可能漏检；值越大，容错率越高但可能包含噪声。 |
| **Min Points** | 50 | **最小点数**。构成一个有效圆柱体所需的最少点数。小树建议设为 20-30，大树建议 100+。 |
| **Min Radius** | 0.03 m | **最小半径**。用于过滤过细的噪声（如树枝）。建议至少 0.03 (3cm)。 |
| **Max Radius** | 0.8 m | **最大半径**。用于过滤过大的物体（如地面或建筑物）。 |
| **Min Height** | 1.0 m | **最小高度**。检测到的圆柱体必须达到的高度。用于过滤灌木或地面噪声。 |
| **Max Iterations** | 100 | **最大迭代次数**。最多检测多少棵树。防止程序无限运行。 |

### 典型场景建议

- **检测幼树/细树**：
  - `Min Points`: 20-30
  - `Min Radius`: 0.01
  - `Distance Threshold`: 0.08 (增加容错)

- **检测成熟林/大树**：
  - `Min Points`: 100-150
  - `Max Radius`: 1.5
  - `Min Height`: 2.0
  - `Distance Threshold`: 0.05 (提高精度)

- **快速预览**：
  - `Max Iterations`: 50
  - `Distance Threshold`: 0.10

---

## 📊 输出结果说明

脚本运行后会生成一个 CSV 文件，包含以下列：
- `Radius (m)`: 树木半径（米）
- `Diameter_DBH (cm)`: 胸径（厘米），即 `Radius * 2 * 100`
- `Height (m)`: 估算的树干高度
- `Num_Points`: 拟合该树干的点云数量

---

## 🛠 环境搭建与故障排查

### 依赖环境
本项目依赖 Python 环境。脚本会自动尝试寻找以下环境：
1. 项目目录下的 `.venv`
2. 项目目录下的 `venv`
3.名为 `tree_detection` 的 Conda 环境
4. 系统默认的 `python3` 或 `python`

**必需的库：**
- `open3d`
- `numpy`
- `scipy`
- `sklearn` (scikit-learn)
- `pandas`
- `matplotlib`
- `tkinter` (通常随 Python 安装，用于 GUI)

### 常见问题

**Q: 运行 `./run.sh` 提示 Permission denied?**
A: 请赋予脚本执行权限：
```bash
chmod +x run.sh
```

**Q: 提示 "ModuleNotFoundError"?**
A: 你的 Python 环境缺少依赖。请确保你激活了正确的环境，并运行安装：
```bash
pip install open3d numpy scipy scikit-learn pandas matplotlib
```

**Q: GUI 无法启动，报错 "No module named '_tkinter'"?**
A: 这通常是因为你的 Python 安装时没有包含 Tkinter 支持。
- Mac (Homebrew): `brew install python-tk`
- Linux (Ubuntu): `sudo apt-get install python3-tk`
- Conda: 通常自带支持，无需额外安装。

**Q: 检测结果为 0 棵树？**
A: 可能是参数太严格。尝试：
1. 降低 `Min Points`
2. 增大 `Distance Threshold`
3. 减小 `Min Radius`

---
*Niigata Forest Research Team - 2026*
