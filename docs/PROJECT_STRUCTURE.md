# Project Structure & Naming Guide

## 1. Top-level layout

```
Niigata_Research_Prep/
├── 00_Raw_Data/          # 原始 LiDAR / 任何外部输入（只读备份）
├── 01_Processed/         # CloudCompare / Python 预处理产物
├── 02_Screenshots/       # 截图、参考素材（png/jpg，命名见 2.2）
├── 03_Scripts/           # 代码（仅 Python）；命名：verb_context.py
├── 04_Results/
│   ├── figures/          # 所有 PNG/JPG 图件
│   ├── tables/           # CSV / JSON / XLSX 等数据表
│   ├── reports/          # TXT / PDF / DOCX 报告
│   └── geometry/         # BIN / PLY / LAS 等 3D 导出
├── docs/                 # 手册、学习资料、结构指南
├── run_tree_detection.sh # 核心一键脚本
└── run_forest_analysis.sh
```

> 约定：`0x_` 前缀保留给数据阶段；`docs/`、`run_*.sh` 为跨阶段工具。若未来新增阶段，继续沿用 `05_Modeling`, `06_Reports` 等递增编码。

## 2. 命名规范

### 2.1 数据 / 表格
- 统一小写 + 下划线：`tree_positions.csv`, `forest_analysis_data.json`
- 结构：`subject_detail_version.ext`
  - `subject`: tree / forest / plot 等
  - `detail`: positions / cylinders / analysis
  - `version`: 可选，使用 `v1`, `20260125`, `draft`
- 中间成果留在 `01_Processed`，命名保留来源：`tree_cloud_slice1.ply`

### 2.2 图像 / 3D
- 图像：`context_view_modifier.png`，例如 `forest_pointcloud_cylinders.png`
- 截图放入 `02_Screenshots/`，命名：`step_tool_desc.png`
- 几何导出放 `04_Results/geometry/`，命名：`plotname_artifact.ext`

### 2.3 脚本 / 批处理
- Python：`verb_subject.py`（`analyze_forest_data.py`、`visualize_forest.py`）
- Shell：`run_*` 前缀表明入口；如果脚本仅用于一次性任务，放在 `scripts/archive/`
- 常量路径统一在脚本顶部定义 `PROJECT_DIR`，避免硬编码

## 3. 操作流程模板

1. **原始数据** → 放入 `00_Raw_Data/YYMMDD_dataset/`
2. **预处理** → 结果存 `01_Processed/<task>/`
3. **脚本** → 写在 `03_Scripts/`，同时更新 `docs/CHANGELOG.md`
4. **分析输出**  
   - 图：`04_Results/figures/`  
   - 表：`04_Results/tables/`  
   - 报告：`04_Results/reports/`  
   - 3D：`04_Results/geometry/`
5. **文档** → 所有指南、新学习手册放入 `docs/`

## 4. 文件添加 checklist

- [ ] 目录是否匹配阶段？（数据→00/01，代码→03，输出→04）
- [ ] 文件名是否使用英文、下划线、无空格？
- [ ] 是否更新 `docs/PROJECT_STRUCTURE.md` 或 README 说明？
- [ ] 如有新依赖，是否在 `run_*.sh` 或 README 中记录？

> 按上述结构整理其它项目时，只需复制该目录模板并替换数据/脚本即可，避免命名混乱。
