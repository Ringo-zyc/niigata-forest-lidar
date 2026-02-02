"""
DBSCAN Parameter Comparison
DBSCAN 参数对比实验 - 纯英文图表
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import os
import open3d as o3d
from sklearn.cluster import DBSCAN
from datetime import datetime

# 配置
PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
OUTPUT_DIR = f"{PROJECT_ROOT}/04_Results/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 60)
print("DBSCAN Parameter Comparison")
print("=" * 60)

# 加载点云
pcd = o3d.io.read_point_cloud(INPUT_FILE)
points = np.asarray(pcd.points)
print(f"Loaded {len(points):,} points")

# 测试不同参数组合
param_sets = [
    {'eps': 0.3, 'min_samples': 50},
    {'eps': 0.5, 'min_samples': 50},
    {'eps': 0.8, 'min_samples': 50},
    {'eps': 1.0, 'min_samples': 50},
    {'eps': 0.5, 'min_samples': 30},
    {'eps': 0.5, 'min_samples': 100},
]

results = []

for params in param_sets:
    eps = params['eps']
    min_samples = params['min_samples']
    
    print(f"\nTesting eps={eps}, min_samples={min_samples}...")
    
    # 2D 投影聚类
    cluster_data = points[:, :2]
    clustering = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
    labels = clustering.fit_predict(cluster_data)
    
    n_trees = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = (labels == -1).sum()
    noise_ratio = n_noise / len(points) * 100
    
    # 计算平均每棵树的点数
    tree_sizes = []
    for label in set(labels):
        if label != -1:
            tree_sizes.append((labels == label).sum())
    avg_points = np.mean(tree_sizes) if tree_sizes else 0
    
    results.append({
        'eps': eps,
        'min_samples': min_samples,
        'n_trees': n_trees,
        'noise_ratio': noise_ratio,
        'avg_points': avg_points,
        'param_str': f"eps={eps}, min={min_samples}"
    })
    
    print(f"  Trees: {n_trees}, Noise: {noise_ratio:.1f}%")

# 转换为 DataFrame
df = pd.DataFrame(results)

# 创建英文图表
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('DBSCAN Parameter Comparison', fontsize=16, fontweight='bold')

# 1. 不同 eps 的效果 (固定 min_samples=50)
ax1 = axes[0, 0]
df_eps = df[df['min_samples'] == 50]
ax1.bar(df_eps['eps'].astype(str), df_eps['n_trees'], color='#3498db', edgecolor='white', linewidth=2)
ax1.set_xlabel('eps value', fontsize=12)
ax1.set_ylabel('Number of Trees Detected', fontsize=12)
ax1.set_title('Effect of eps (min_samples=50)', fontsize=14, fontweight='bold')
for i, row in df_eps.iterrows():
    ax1.text(list(df_eps['eps'].astype(str)).index(str(row['eps'])), row['n_trees'] + 2, 
             str(int(row['n_trees'])), ha='center', fontsize=11, fontweight='bold')

# 2. 噪声比例对比
ax2 = axes[0, 1]
ax2.bar(df_eps['eps'].astype(str), df_eps['noise_ratio'], color='#e74c3c', edgecolor='white', linewidth=2)
ax2.set_xlabel('eps value', fontsize=12)
ax2.set_ylabel('Noise Ratio (%)', fontsize=12)
ax2.set_title('Noise Ratio by eps', fontsize=14, fontweight='bold')
for i, row in df_eps.iterrows():
    ax2.text(list(df_eps['eps'].astype(str)).index(str(row['eps'])), row['noise_ratio'] + 1, 
             f"{row['noise_ratio']:.1f}%", ha='center', fontsize=10)

# 3. 不同 min_samples 的效果 (固定 eps=0.5)
ax3 = axes[1, 0]
df_min = df[df['eps'] == 0.5]
ax3.bar(df_min['min_samples'].astype(str), df_min['n_trees'], color='#2ecc71', edgecolor='white', linewidth=2)
ax3.set_xlabel('min_samples value', fontsize=12)
ax3.set_ylabel('Number of Trees Detected', fontsize=12)
ax3.set_title('Effect of min_samples (eps=0.5)', fontsize=14, fontweight='bold')
for i, row in df_min.iterrows():
    ax3.text(list(df_min['min_samples'].astype(str)).index(str(row['min_samples'])), row['n_trees'] + 2, 
             str(int(row['n_trees'])), ha='center', fontsize=11, fontweight='bold')

# 4. 统计表格
ax4 = axes[1, 1]
ax4.axis('off')
summary_data = [
    ['Parameters', 'Trees', 'Noise%', 'Avg Points/Tree'],
]
for _, row in df.iterrows():
    summary_data.append([
        f"eps={row['eps']}, min={int(row['min_samples'])}",
        str(int(row['n_trees'])),
        f"{row['noise_ratio']:.1f}%",
        f"{int(row['avg_points'])}"
    ])

table = ax4.table(cellText=summary_data[1:], colLabels=summary_data[0],
                  loc='center', cellLoc='center',
                  colColours=['#f5f5f5']*4,
                  cellColours=[['#ffffff']*4]*len(df))
table.auto_set_font_size(False)
table.set_fontsize(11)
table.scale(1.2, 1.8)
ax4.set_title('Parameter Comparison Summary', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/dbscan_parameter_comparison.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print(f"\n✅ Chart saved: {OUTPUT_DIR}/dbscan_parameter_comparison.png")

# 保存结果表格
df.to_csv(f'{PROJECT_ROOT}/04_Results/tables/dbscan_params_comparison.csv', index=False)
print(f"✅ Data saved: 04_Results/tables/dbscan_params_comparison.csv")

print("\n" + "=" * 60)
print("Parameter comparison complete!")
print("=" * 60)
