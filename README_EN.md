# 🌲 UAV-LiDAR Single Tree Detection & Automated Measurement

<div align="center">

![Version](https://img.shields.io/badge/Version-2.1-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-Academic-orange)

**Automated forest survey tool based on UAV-borne LiDAR point cloud data**

[中文](README.md) | [日本語](README_JP.md)

[Quick Start](#-quick-start) • [Features](#-features) • [Structure](#-project-structure) • [Usage](#-usage-guide) • [Validation](#-validation-tools)

</div>

---

## 📋 Overview

This project implements a complete workflow from raw LiDAR point clouds to individual tree parameter extraction, supporting:
- 🌳 **Tree Detection**: Tree trunk identification based on RANSAC cylinder fitting
- 📏 **DBH Extraction**: Automatic measurement of Diameter at Breast Height
- 📍 **Spatial Localization**: UTM coordinate output for each tree
- 📊 **Visualization**: 2D distribution maps + 3D superposition maps + Interactive preview
- ✅ **Validation Tools**: Stratified sampling + RMSE statistics

**Research Direction**: Automated individual tree identification and tree information measurement using UAV-borne LiDAR (including RC helicopter) point cloud data.

---

## 🚀 Quick Start

```bash
# 1. Navigate to project directory
cd /Users/zyc/Downloads/Niigata_Research_Prep

# 2. Launch GUI (Recommended)
./03_Scripts/run.sh

# 3. In the GUI:
#    - Select input point cloud (.ply)
#    - Adjust parameters (or use defaults)
#    - Click "Start Detection"
```

---

## ✨ Features

| Feature | Description | Tool |
|---------|-------------|------|
| **GUI Interface** | Tabbed design, integrated detection + visualization | `gui_app.py` |
| **CLI Detection** | Batch processing without interface | `detect_cylinders_v2.py` |
| **3D Visualization** | Matplotlib static plots + Open3D interactive | `visualize_forest.py` |
| **Accuracy Validation** | Stratified sampling + RMSE/MAE calculation | `generate_validation_sample.py` |
| **Biomass Analysis** | Diameter distribution, carbon stock estimation | `analyze_forest_data.py` |

---

## 📁 Project Structure

```
Niigata_Research_Prep/
├── 00_Raw_Data/                    # Raw LiDAR Data (.laz)
│   ├── SJFE_final_ULS.laz         # San Juan Fault (1.1GB)
│   └── SL_Winter2021_*.laz        # StREAM Lab (473MB)
│
├── 01_Processed/                   # Processed Point Clouds
│   ├── San Juan Fault/            # Main Research Area
│   └── StREAM Lab/                # Auxiliary Validation Area
│
├── 02_Screenshots/                 # Learning Process Screenshots
│   └── failures/                  # Failure cases (for Deep Learning data engineering)
│
├── 03_Scripts/                     # 🐍 Core Scripts
│   ├── run.sh                     # Unified Entry Point
│   ├── gui_app.py                 # GUI Main Program
│   ├── tree_utils.py              # RANSAC Algorithm Core
│   ├── detect_cylinders_v2.py     # CLI Detection
│   ├── visualize_forest.py        # Visualization Generation
│   └── MANUAL.md                  # Tool Manual
│
├── 04_Results/                     # Output Results
│   ├── figures/                   # Figures (.png)
│   ├── tables/                    # Data Tables (.csv)
│   └── reports/                   # 📅 Planning & Learning Docs
│       ├── path_ab_learning_plan.html      # Deep Learning Roadmap
│       ├── iti_learning_summary.md         # Short-term Learning Summary
│       └── graduate_career_roadmap.html    # 2-Year Career Roadmap
│
├── docs/                           # 📚 Core Project Documentation
│   ├── research_master_guideline.html  # 🏆 Master Research Guideline (Entry)
│   └── career_skill_mapping.md         # Skill-Career Mapping
│
└── README.md                       # Main Documentation (Chinese)
```

---

## 🔧 Usage Guide

### Method 1: GUI (Recommended)

```bash
./03_Scripts/run.sh
```

**🌲 Detection Tab**:
1. Select input point cloud file (`.ply`)
2. Set output CSV path
3. Adjust RANSAC parameters (optional)
4. Click "Start Detection"
5. Check "Auto Visualization" to generate images automatically after completion

**🎨 Visualization Tab**:
1. Select point cloud and results directory
2. Click "Generate Visualization Charts"
3. Click "Interactive 3D Preview" to open Open3D window

### Method 2: Command Line

```bash
# Detection
python 03_Scripts/detect_cylinders_v2.py

# Visualization
python 03_Scripts/visualize_forest.py <path_to_ply>
```

---

## ⚙️ Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Distance Threshold | 0.06 m | Max distance from point to cylinder axis |
| Min Points | 50 | Minimum points for one cylinder |
| Min Radius | 0.03 m | Minimum radius (3 cm) |
| Max Radius | 0.8 m | Maximum radius (80 cm) |
| Min Height | 1.0 m | Minimum height |
| Max Iterations | 100 | Max number of trees to detect |

---

## ✅ Validation Tools

### 1. Generate Stratified Sampling Table

```bash
python 03_Scripts/generate_validation_sample.py
```

Output: `validation_sample.csv` (9 trees sampled by DBH size)

### 2. Verify in CloudCompare

Locate each tree using coordinates, manually measure diameter, and fill in `Manual_DBH_cm` column.

### 3. Calculate Error Statistics

```bash
python 03_Scripts/calculate_validation_stats.py
```

Output: RMSE, MAE, Mean Error, etc.

---

## 📊 Output Format

### CSV Columns

| Column | Unit | Description |
|--------|------|-------------|
| Radius (m) | m | Tree radius |
| Diameter_DBH (cm) | cm | DBH |
| Height (m) | m | Fitted height (May be overestimated due to point density) |
| Num_Points | count | Number of points |
| X, Y, Z | m | UTM Coordinates |

---

## 🏗 Tech Stack

- **Point Cloud Processing**: Open3D, CloudCompare
- **Algorithms**: RANSAC, PCA (scikit-learn)
- **Visualization**: Matplotlib, Open3D
- **GUI**: Tkinter
- **Data Analysis**: Pandas, NumPy

---

## 📄 License

For academic research use only.
