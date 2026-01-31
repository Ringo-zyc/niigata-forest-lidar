# 项目结构与文件导航

> **更新日期**: 2026-01-30
> **用途**: 帮助你快速找到需要的文件

---

## 📁 目录树

```
Niigata_Research_Prep/
│
├── 📂 00_Raw_Data/                    # 原始 LiDAR 数据 (只读)
│   ├── SJFE_final_ULS.laz            # San Juan Fault 原始数据 (1.1GB)
│   └── SL_Winter2021_*.laz           # StREAM Lab 原始数据 (473MB)
│
├── 📂 01_Processed/                   # 处理后的点云
│   ├── San Juan Fault/
│   │   ├── Off-Ground_Good-5m.ply    # ⭐ 主要练习数据
│   │   ├── Off-Ground_Good-5m_cylinders.csv  # RANSAC 结果
│   │   └── isolated_trees_dbscan/    # [新] ITI 分离结果
│   └── StREAM Lab/
│       └── tree.ply                  # 验证数据
│
├── 📂 02_Screenshots/                 # 截图存放处
│   └── [按 dayX_主题_细节.png 命名]
│
├── 📂 03_Scripts/                     # Python 脚本
│   │
│   │ -- 原有脚本 --
│   ├── tree_utils.py                 # RANSAC 核心算法
│   ├── detect_cylinders_v2.py        # 树干检测
│   ├── gui_app.py                    # GUI 程序
│   ├── visualize_forest.py           # 可视化
│   │
│   │ -- 新增 ITI 脚本 --
│   ├── tree_isolation_dbscan.py      # ⭐ DBSCAN 单木分离
│   ├── measure_isolated_tree.py      # DBH 测量
│   ├── run_dbscan_experiments.py     # 参数网格搜索
│   ├── full_iti_pipeline.py          # ⭐ 完整流程
│   ├── compare_iti_ransac.py         # 方法对比
│   └── treeiso_wrapper.py            # Treeiso 封装
│
├── 📂 04_Results/                     # 输出结果
│   ├── figures/                      # 图表
│   ├── tables/                       # CSV 数据表
│   │   ├── dbscan_experiments.csv    # [新] 参数实验
│   │   └── isolated_trees_dbh.csv    # [新] DBH 测量
│   ├── reports/                      # ⭐ 报告文档
│   │   ├── task_checklist.md         # 任务清单 (每日打勾)
│   │   ├── iti_learning_summary.md   # 学习总结
│   │   ├── learning_diary.md         # 学习日记
│   │   └── comparison_notes.md       # [待创建] 对比分析
│   └── iti_pipeline_output/          # [新] Pipeline 输出
│
├── 📂 docs/                           # 项目文档
│   ├── algorithm_principles.md       # ⭐ 算法原理手册
│   ├── career_skill_mapping.md       # 技能-职业关联
│   ├── daily_workflow.md             # 每日工作流
│   └── PROJECT_STRUCTURE.md          # 本文件
│
├── README.md                         # 项目说明
├── QUICKSTART.md                     # 快速开始
└── OPERATION_SUMMARY.md              # 操作历史
```

---

## ⭐ 重要文件快速索引

| 场景 | 文件 |
|------|------|
| 每天开始前看 | `docs/algorithm_principles.md` |
| 查看今日任务 | `04_Results/reports/task_checklist.md` |
| 运行主程序 | `03_Scripts/full_iti_pipeline.py` |
| 记录学习进度 | `04_Results/reports/learning_diary.md` |
| 技能与久保田关联 | `docs/career_skill_mapping.md` |

---

## 🚀 常用命令

```bash
# 进入项目
cd /Users/zyc/Downloads/Niigata_Research_Prep

# 激活环境
source .venv/bin/activate

# 运行 DBSCAN 分割
python 03_Scripts/tree_isolation_dbscan.py

# 运行完整流程
python 03_Scripts/full_iti_pipeline.py

# 参数实验
python 03_Scripts/run_dbscan_experiments.py

# 方法对比
python 03_Scripts/compare_iti_ransac.py
```

---

*文件有问题？随时问我*
