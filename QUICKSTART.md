# 快速参考卡 - 树木点云分析

## 🚀 一键运行

```bash
cd /Users/zyc/Downloads/Niigata_Research_Prep
./run_tree_detection.sh
```

**输出**: `04_Results/tables/tree_cylinders.csv`

---

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `run_tree_detection.sh` | 主运行脚本 |
| `run_forest_analysis.sh` | 生物量/图表一键脚本 |
| `03_Scripts/detect_cylinders_v2.py` | 检测算法（可调参数） |
| `03_Scripts/analyze_forest_data.py` | 数据清洗与生物量 |
| `04_Results/tables/tree_cylinders.csv` | 主输出结果 |
| `docs/PROJECT_STRUCTURE.md` | 目录与命名规则 |

---

## 🔧 常用参数调整

编辑 `03_Scripts/detect_cylinders_v2.py`：

```python
DISTANCE_THRESHOLD = 0.06  # 精度容差
MIN_RADIUS = 0.03          # 最小树干半径 (m)
MAX_RADIUS = 0.8           # 最大树干半径 (m)
MIN_HEIGHT = 1.0           # 最小树高 (m)
MIN_POINTS = 50            # 最少点数
MAX_ITERATIONS = 100       # 最多检测树木数量
```

---

## 📊 结果格式

```csv
Radius (m),Diameter_DBH (cm),Height (m),Num_Points
0.0785,15.70,30.52,167
```

- **Radius**: 半径（米）
- **Diameter_DBH**: 胸径（厘米）
- **Height**: 高度（米）
- **Num_Points**: 点云数量

---

## 🛠️ CloudCompare 工作流

1. **打开** → 选择 .laz 文件
2. **CSF 滤波** → 分离地面/树木
3. **Segment/Clipping Box** → 提取目标区域
4. **Slice** → 切片处理
5. **保存** → .bin 和 .ply 格式

---

## 📞 问题排查

### 未检测到树木
→ 调低 `MIN_RADIUS`、`MIN_HEIGHT`、`MIN_POINTS`

### 检测结果太多噪点
→ 调高 `MIN_POINTS`、减小 `DISTANCE_THRESHOLD`

### Open3D 错误
→ 脚本会自动创建 Python 3.11 环境

---

## 📖 详细文档

查看完整操作手册：`README.md`
