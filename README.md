# 新泻研究项目 - 树木点云分析操作手册

## 📋 项目概述

本项目用于从激光雷达（LiDAR）点云数据中提取树木信息，包括胸径（DBH）和树高数据。

**项目负责人**: zyc  
**创建日期**: 2026-01-25  
**数据来源**: 新泻冬季 ULS 点云数据

---

## 📁 项目文件结构

```
Niigata_Research_Prep/
├── 00_Raw_Data/                    # 原始数据
│   ├── SJFE_final_ULS.laz         # 原始 LiDAR 数据
│   └── SL_Winter2021_classified_projected_clipped.laz
│
├── 01_Processed/                   # 处理后的数据
│   ├── tree.bin                   # CloudCompare 二进制格式
│   ├── tree.ply                   # PLY 格式（用于 Python 处理）
│   └── Niigata_Project_Day1_Done.bin
│
├── 02_Screenshots/                 # 操作截图（用于参考）
│   ├── CSF (布料模拟滤波)算法处理.png
│   ├── RANSAC设置.png
│   └── ... (其他截图)
│
├── 03_Scripts/                     # 分析脚本
│   ├── detect_cylinders_v2.py     # 圆柱体检测 + Slenderness 修正
│   ├── analyze_forest_data.py     # 数据清洗、径阶、生物量
│   └── visualize_forest.py        # 3D 叠加图 & 空间分布
│
├── 04_Results/                     # 分析输出
│   ├── figures/                   # *.png 图件
│   ├── tables/                    # CSV/JSON/XLSX 数据表
│   ├── reports/                   # 文本/报告
│   └── geometry/                  # BIN/PLY 等 3D 导出
│
├── docs/                           # 学习手册（PROJECT_STRUCTURE.md 等）
├── run_tree_detection.sh           # 主运行脚本
├── run_forest_analysis.sh          # 生物量分析脚本
└── README.md                       # 本文档
```

---

## 🚀 快速开始

### 运行树木检测

直接运行主脚本即可：

```bash
cd /Users/zyc/Downloads/Niigata_Research_Prep
./run_tree_detection.sh
```

或者：

```bash
bash /Users/zyc/Downloads/Niigata_Research_Prep/run_tree_detection.sh
```

**输出结果**：`04_Results/tables/tree_cylinders.csv`

---

## 📊 完整操作流程

### 第一步：数据预处理（CloudCompare）

#### 1.1 打开原始数据

1. 启动 CloudCompare
2. 文件 → 打开 → 选择 `00_Raw_Data/*.laz` 文件
3. 设置 Global Shift/Scale（如果提示）

#### 1.2 地面点滤波（CSF 算法）

1. 选择点云
2. 插件 → CSF Filter（布料模拟滤波）
3. 参数设置：
   - Cloth resolution: 1.0
   - Max iterations: 500
   - Classification threshold: 0.5
4. 运行后会生成：
   - Ground points（地面点）
   - Off-ground points（非地面点 = 树木）

#### 1.3 提取目标树木

**方法 1：使用 Segment（分割工具）**
1. 工具 → Segmentation → Segment
2. 在 3D 视图中框选目标区域
3. 确认选择后导出

**方法 2：使用 Clipping Box（裁剪盒）**
1. 工具 → Clipping Box
2. 调整裁剪盒大小和位置
3. 提取内部点云

#### 1.4 切片处理

1. 工具 → Segmentation → Cross Section（Slice）
2. 设置切片参数：
   - 厚度：根据需要调整
   - 方向：通常为 Z 轴（垂直）
3. 导出切片结果

#### 1.5 保存处理后的数据

```bash
文件 → 保存 → 选择格式：
- .bin (CloudCompare 原生格式)
- .ply (用于 Python 处理)
```

保存位置：`01_Processed/tree.bin` 和 `tree.ply`

---

### 第二步：圆柱体检测（自动化）

#### 2.1 环境要求

- **Python**: 3.11（通过 conda 管理）
- **必需库**: 
  - open3d
  - numpy
  - scipy
  - scikit-learn

#### 2.2 首次运行设置

脚本会自动：
1. 创建 conda 环境（名称：`tree_detection`）
2. 安装所需依赖
3. 转换 .bin 文件为 .ply 格式
4. 运行圆柱体检测

#### 2.3 运行检测

```bash
cd /Users/zyc/Downloads/Niigata_Research_Prep
./run_tree_detection.sh
```

#### 2.4 参数调整（如需）

编辑 `03_Scripts/detect_cylinders_v2.py`：

```python
# RANSAC 参数
DISTANCE_THRESHOLD = 0.06  # 点到圆柱体的最大距离
MIN_POINTS = 50           # 一个圆柱体的最少点数
MIN_RADIUS = 0.03         # 最小半径 (m) - 3cm
MAX_RADIUS = 0.8          # 最大半径 (m) - 80cm
MIN_HEIGHT = 1.0          # 最小高度 (m) - 1m
MAX_ITERATIONS = 100      # 最多检测圆柱体数量
```

---

## 📈 结果说明

### 输出文件：`04_Results/tables/tree_cylinders.csv`

**列说明**：

| 列名 | 说明 | 单位 |
|------|------|------|
| Radius (m) | 树干半径 | 米 |
| Diameter_DBH (cm) | 胸径（DBH，Diameter at Breast Height） | 厘米 |
| Height (m) | 树高 | 米 |
| Num_Points | 该树的点云数量 | 个 |

**示例数据**：

```csv
Radius (m),Diameter_DBH (cm),Height (m),Num_Points
0.0785,15.70,30.52,167
0.0783,15.67,37.14,86
0.0765,15.31,31.98,87
```

**数据排序**：按直径（DBH）从大到小排列

---

## 🛠️ 技术细节

### CloudCompare 命令行使用

#### 基本命令格式

```bash
/Applications/CloudCompare.app/Contents/MacOS/CloudCompare \
    -SILENT \                    # 静默模式
    -O "input.bin" \             # 打开文件
    -NO_TIMESTAMP \              # 不添加时间戳
    -RANSAC \                    # 运行 RANSAC
    -C_EXPORT_FMT PLY \          # 导出格式
    -SAVE_CLOUDS FILE "output.ply"
```

#### 重要说明

❌ **不支持的参数**（命令行模式）：
- `-EPS`、`-BITMAP_EPS`、`-SUPPORT`、`-PROB`
- `-OUT_CLOUD_DIR`（输出总是在输入文件同目录）

✅ **支持的功能**：
- `-RANSAC`：RANSAC 形状检测
- `-CSF`：地面滤波
- `-C_EXPORT_FMT`：格式转换

### Python 圆柱体检测算法

#### 算法原理

1. **RANSAC 拟合**：
   - 随机采样 3 个点
   - 使用 PCA 估算圆柱体轴方向
   - 计算点到轴的距离
   - 估算半径和高度

2. **迭代检测**：
   - 检测一个圆柱体后移除对应点
   - 继续检测下一个圆柱体
   - 重复直到无法检测或达到上限

3. **参数过滤**：
   - 半径范围：3-80 cm
   - 最小高度：1 m
   - 最少点数：50 个

#### 算法优化建议

1. **提高精度**：
   - 增加 `n_iterations`（RANSAC 迭代次数）
   - 减小 `DISTANCE_THRESHOLD`

2. **检测更多树**：
   - 减小 `MIN_POINTS`
   - 增加 `MAX_ITERATIONS`

3. **过滤小树**：
   - 增大 `MIN_RADIUS`
   - 增大 `MIN_HEIGHT`

---

## 🔧 故障排除

### 问题 1: Open3D 安装失败

**错误信息**：
```
ERROR: Could not find a version that satisfies the requirement open3d
```

**原因**: Python 3.14 不支持 Open3D

**解决方案**：
脚本会自动创建 Python 3.11 的 conda 环境，无需手动处理。

---

### 问题 2: 未检测到圆柱体

**可能原因**：
1. 点云质量不足
2. 参数设置过严格
3. 数据预处理不当

**解决方案**：
1. 检查输入点云文件是否正确
2. 调整检测参数（见上文"参数调整"）
3. 确认数据预处理步骤正确

---

### 问题 3: 检测结果不准确

**优化方法**：

1. **增加点云密度**：
   - 在 CloudCompare 中减小切片厚度
   - 使用更高分辨率的原始数据

2. **调整 RANSAC 参数**：
   ```python
   DISTANCE_THRESHOLD = 0.04  # 降低容差
   MIN_POINTS = 100           # 增加最小点数
   ```

3. **手动验证**：
   - 在 CloudCompare 中打开结果文件
   - 可视化检查检测的圆柱体

---

## 📚 参考资料

### CloudCompare 相关

- 官方文档: https://www.cloudcompare.org/doc/
- 命令行文档: https://www.cloudcompare.org/doc/wiki/index.php/Command_line_mode
- CSF 算法论文: Zhang et al. (2016)

### Python 库文档

- Open3D: http://www.open3d.org/docs/
- NumPy: https://numpy.org/doc/
- scikit-learn: https://scikit-learn.org/

### RANSAC 算法

- 原理介绍: https://en.wikipedia.org/wiki/Random_sample_consensus
- 圆柱体拟合: Schnabel et al. (2007)

---

## 📝 版本历史

### v2.0 (2026-01-25)
- ✅ 实现自动化圆柱体检测
- ✅ 使用 Python + Open3D + RANSAC
- ✅ 成功检测 61 棵树
- ✅ 输出标准 CSV 格式

### v1.0 (初始版本)
- ❌ 尝试使用 CloudCompare 命令行
- ❌ 发现不支持圆柱体参数自定义
- ✅ 完成数据预处理流程

---

## 👥 联系方式

如有问题或建议，请联系项目负责人。

---

## 📄 许可证

本项目仅供学术研究使用。

---

**最后更新**: 2026-01-25  
**文档版本**: 1.0
