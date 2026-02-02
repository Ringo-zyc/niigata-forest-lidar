"""
Comprehensive ITI Method Comparison
单木分离方法全面对比分析

对比内容：
1. TreeISO 优化前后对比
2. TreeISO vs DBSCAN 对比
3. 多种可视化图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
from datetime import datetime

# 配置
PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
OUTPUT_DIR = f"{PROJECT_ROOT}/04_Results/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("Comprehensive ITI Method Comparison")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# ============================================================
# 加载所有结果数据
# ============================================================

# DBSCAN 结果
dbscan_csv = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_dbscan/isolated_trees_summary.csv"
df_dbscan = pd.read_csv(dbscan_csv)

# TreeISO 默认参数结果
treeiso_default_csv = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_treeiso/treeiso_trees_summary.csv"
df_treeiso_default = pd.read_csv(treeiso_default_csv)

# TreeISO UAV 优化版结果
treeiso_uav_csv = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_treeiso_uav/treeiso_uav_optimized_summary.csv"
df_treeiso_uav = pd.read_csv(treeiso_uav_csv)

print("\n[Data Loaded]")
print(f"  DBSCAN: {len(df_dbscan)} trees")
print(f"  TreeISO (Default): {len(df_treeiso_default)} trees")
print(f"  TreeISO (UAV Optimized): {len(df_treeiso_uav)} trees")

# ============================================================
# 图表 1: TreeISO 优化前后对比
# ============================================================

fig1, axes1 = plt.subplots(1, 3, figsize=(15, 5))
fig1.suptitle('TreeISO Optimization: Before vs After', fontsize=16, fontweight='bold')

# 1.1 树木检测数量
ax = axes1[0]
labels = ['Default\n(TLS params)', 'UAV Optimized']
values = [len(df_treeiso_default), len(df_treeiso_uav)]
colors = ['#e74c3c', '#27ae60']
bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=2)
ax.set_ylabel('Number of Trees Detected', fontsize=12)
ax.set_title('Tree Detection Count', fontsize=14, fontweight='bold')
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, 
            str(val), ha='center', fontsize=14, fontweight='bold')
ax.set_ylim(0, max(values) * 1.2)

# 1.2 平均树高
ax = axes1[1]
heights = [df_treeiso_default['height'].mean(), df_treeiso_uav['height'].mean()]
bars = ax.bar(labels, heights, color=colors, edgecolor='white', linewidth=2)
ax.set_ylabel('Average Tree Height (m)', fontsize=12)
ax.set_title('Average Tree Height', fontsize=14, fontweight='bold')
for bar, val in zip(bars, heights):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
            f'{val:.1f}m', ha='center', fontsize=12, fontweight='bold')

# 1.3 参数对比表
ax = axes1[2]
ax.axis('off')
param_data = [
    ['Parameter', 'Default', 'Optimized'],
    ['REG_STRENGTH1', '1.0', '5.0'],
    ['REG_STRENGTH2', '20', '100'],
    ['MIN_NN1', '5', '10'],
    ['MIN_NN2', '20', '50'],
    ['SOR Filter', 'No', 'Yes'],
    ['Trees Detected', '12', '91'],
]
table = ax.table(cellText=param_data[1:], colLabels=param_data[0],
                 loc='center', cellLoc='center',
                 colColours=['#f5f5f5']*3,
                 cellColours=[['#fff', '#ffebee', '#e8f5e9']]*6)
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.6)
ax.set_title('Parameter Comparison', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/treeiso_optimization_comparison.png', dpi=150, 
            bbox_inches='tight', facecolor='white')
plt.close()
print(f"\n✅ Saved: treeiso_optimization_comparison.png")

# ============================================================
# 图表 2: 所有方法全面对比
# ============================================================

fig2, axes2 = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('Complete ITI Method Comparison', fontsize=16, fontweight='bold')

# 方法列表
methods = ['DBSCAN\n(eps=0.5)', 'DBSCAN\n(eps=0.8)', 'TreeISO\n(Default)', 'TreeISO\n(UAV Opt.)']
tree_counts = [155, 110, 12, 91]  # DBSCAN eps=0.8 从参数对比得到
colors = ['#3498db', '#2980b9', '#e74c3c', '#27ae60']

# 2.1 检测数量对比
ax = axes2[0, 0]
bars = ax.bar(methods, tree_counts, color=colors, edgecolor='white', linewidth=2)
ax.set_ylabel('Number of Trees', fontsize=12)
ax.set_title('Tree Detection Count by Method', fontsize=14, fontweight='bold')
for bar, val in zip(bars, tree_counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
            str(val), ha='center', fontsize=12, fontweight='bold')
ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Reference: ~100 trees')
ax.legend(loc='upper right')

# 2.2 树高分布对比
ax = axes2[0, 1]
ax.hist(df_dbscan['height'], bins=20, alpha=0.5, label='DBSCAN', color='#3498db', edgecolor='white')
ax.hist(df_treeiso_uav['height'], bins=15, alpha=0.5, label='TreeISO (UAV)', color='#27ae60', edgecolor='white')
ax.set_xlabel('Tree Height (m)', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Tree Height Distribution', fontsize=14, fontweight='bold')
ax.legend()

# 2.3 每棵树点数分布
ax = axes2[1, 0]
ax.hist(df_dbscan['n_points'], bins=30, alpha=0.5, label='DBSCAN', color='#3498db', edgecolor='white')
ax.hist(df_treeiso_uav['n_points'], bins=20, alpha=0.5, label='TreeISO (UAV)', color='#27ae60', edgecolor='white')
ax.set_xlabel('Points per Tree', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Points per Tree Distribution', fontsize=14, fontweight='bold')
ax.legend()

# 2.4 综合统计表
ax = axes2[1, 1]
ax.axis('off')
summary = [
    ['Metric', 'DBSCAN (0.5)', 'DBSCAN (0.8)', 'TreeISO Def.', 'TreeISO UAV'],
    ['Trees', '155', '110', '12', '91'],
    ['Avg Height (m)', f'{df_dbscan["height"].mean():.1f}', '~8', 
     f'{df_treeiso_default["height"].mean():.1f}', f'{df_treeiso_uav["height"].mean():.1f}'],
    ['Max Height (m)', f'{df_dbscan["height"].max():.1f}', '~25', 
     f'{df_treeiso_default["height"].max():.1f}', f'{df_treeiso_uav["height"].max():.1f}'],
    ['Noise Ratio', '43.6%', '14.3%', 'N/A', '6.7% (SOR)'],
    ['Algorithm Type', 'Density', 'Density', 'Graph-Cut', 'Graph-Cut'],
]
table = ax.table(cellText=summary[1:], colLabels=summary[0],
                 loc='center', cellLoc='center',
                 colColours=['#f5f5f5']*5,
                 cellColours=[['#fff', '#e3f2fd', '#bbdefb', '#ffebee', '#e8f5e9']]*5)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.1, 1.6)
ax.set_title('Summary Statistics', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/complete_method_comparison.png', dpi=150, 
            bbox_inches='tight', facecolor='white')
plt.close()
print(f"✅ Saved: complete_method_comparison.png")

# ============================================================
# 图表 3: 方法特性雷达图
# ============================================================

fig3 = plt.figure(figsize=(10, 8))
ax = fig3.add_subplot(111, projection='polar')

# 评估维度
categories = ['Detection\nCount', 'Height\nAccuracy', 'Low\nNoise', 'Speed', 'Ease of\nUse']
N = len(categories)

# 归一化评分 (1-5)
scores = {
    'DBSCAN': [4, 3, 2, 5, 5],         # 数量多，但噪声高
    'TreeISO (UAV)': [3, 4, 4, 3, 2],  # 数量适中，噪声低，需调参
}

angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]

ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=11)

for method, score in scores.items():
    values = score + score[:1]
    color = '#3498db' if 'DBSCAN' in method else '#27ae60'
    ax.plot(angles, values, 'o-', linewidth=2, label=method, color=color)
    ax.fill(angles, values, alpha=0.25, color=color)

ax.set_ylim(0, 5)
ax.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
plt.title('Method Characteristics Comparison', fontsize=14, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/method_radar_chart.png', dpi=150, 
            bbox_inches='tight', facecolor='white')
plt.close()
print(f"✅ Saved: method_radar_chart.png")

# ============================================================
# 图表 4: 优化过程时间线
# ============================================================

fig4, ax = plt.subplots(figsize=(12, 6))

# 时间线数据
steps = ['TreeISO\nDefault', 'SOR\nFiltering', 'Increase\nRegularization', 'Skip Final\nMerge', 'TreeISO\nOptimized']
trees_at_step = [12, 12, 91, 91, 91]
improvements = ['12 trees\n(under-seg)', 'Remove\n6.7% noise', 'λ1: 1→5\nλ2: 20→100', 'Better for\nUAV data', '91 trees\n(7.6x ↑)']

x = np.arange(len(steps))
bars = ax.bar(x, trees_at_step, color=['#e74c3c', '#f39c12', '#f39c12', '#f39c12', '#27ae60'], 
              edgecolor='white', linewidth=2)

ax.set_xticks(x)
ax.set_xticklabels(steps, fontsize=11)
ax.set_ylabel('Trees Detected', fontsize=12)
ax.set_title('TreeISO Optimization Journey', fontsize=14, fontweight='bold')

# 添加改进标注
for i, (bar, imp) in enumerate(zip(bars, improvements)):
    y_pos = bar.get_height() + 3
    ax.text(bar.get_x() + bar.get_width()/2, y_pos, imp, ha='center', fontsize=9)

ax.set_ylim(0, 120)
ax.axhline(y=91, color='#27ae60', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/optimization_journey.png', dpi=150, 
            bbox_inches='tight', facecolor='white')
plt.close()
print(f"✅ Saved: optimization_journey.png")

# ============================================================
# 打开图表
# ============================================================

print("\n" + "=" * 60)
print("All charts generated successfully!")
print("=" * 60)

import subprocess
subprocess.run(['open', f'{OUTPUT_DIR}/treeiso_optimization_comparison.png'])
subprocess.run(['open', f'{OUTPUT_DIR}/complete_method_comparison.png'])
subprocess.run(['open', f'{OUTPUT_DIR}/method_radar_chart.png'])
subprocess.run(['open', f'{OUTPUT_DIR}/optimization_journey.png'])
