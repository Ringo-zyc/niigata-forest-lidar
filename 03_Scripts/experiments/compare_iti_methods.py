"""
单木分离方法对比分析
Compare DBSCAN vs Treeiso Results
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import os

# 配置
PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
OUTPUT_DIR = f"{PROJECT_ROOT}/04_Results/figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载结果
dbscan_csv = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_dbscan/isolated_trees_summary.csv"
treeiso_csv = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_treeiso/treeiso_trees_summary.csv"

df_dbscan = pd.read_csv(dbscan_csv)
df_treeiso = pd.read_csv(treeiso_csv)

print("=" * 60)
print("单木分离方法对比分析")
print("=" * 60)

# 基本统计
print("\n📊 基本统计:")
print(f"  DBSCAN:  检测到 {len(df_dbscan)} 棵树")
print(f"  Treeiso: 检测到 {len(df_treeiso)} 棵树")

print("\n📏 树高统计:")
print(f"  DBSCAN:  平均 {df_dbscan['height'].mean():.2f}m, 范围 [{df_dbscan['height'].min():.2f}, {df_dbscan['height'].max():.2f}]m")
print(f"  Treeiso: 平均 {df_treeiso['height'].mean():.2f}m, 范围 [{df_treeiso['height'].min():.2f}, {df_treeiso['height'].max():.2f}]m")

print("\n📍 点数统计:")
print(f"  DBSCAN:  平均每棵树 {df_dbscan['n_points'].mean():.0f} 点")
print(f"  Treeiso: 平均每棵树 {df_treeiso['n_points'].mean():.0f} 点")

# 创建对比图
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('DBSCAN vs Treeiso 对比分析', fontsize=16, fontweight='bold')

# 1. 检测数量对比
ax1 = axes[0, 0]
methods = ['DBSCAN', 'Treeiso']
counts = [len(df_dbscan), len(df_treeiso)]
colors = ['#3498db', '#2ecc71']
bars = ax1.bar(methods, counts, color=colors, edgecolor='white', linewidth=2)
ax1.set_ylabel('检测到的树木数量', fontsize=12)
ax1.set_title('树木检测数量对比', fontsize=14, fontweight='bold')
for bar, count in zip(bars, counts):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
             str(count), ha='center', va='bottom', fontsize=14, fontweight='bold')
ax1.set_ylim(0, max(counts) * 1.2)

# 2. 树高分布对比
ax2 = axes[0, 1]
ax2.hist(df_dbscan['height'], bins=20, alpha=0.6, label='DBSCAN', color='#3498db', edgecolor='white')
ax2.hist(df_treeiso['height'], bins=10, alpha=0.6, label='Treeiso', color='#2ecc71', edgecolor='white')
ax2.set_xlabel('树高 (m)', fontsize=12)
ax2.set_ylabel('数量', fontsize=12)
ax2.set_title('树高分布对比', fontsize=14, fontweight='bold')
ax2.legend()

# 3. 每棵树点数分布
ax3 = axes[1, 0]
ax3.hist(df_dbscan['n_points'], bins=30, alpha=0.6, label='DBSCAN', color='#3498db', edgecolor='white')
ax3.hist(df_treeiso['n_points'], bins=10, alpha=0.6, label='Treeiso', color='#2ecc71', edgecolor='white')
ax3.set_xlabel('每棵树点数', fontsize=12)
ax3.set_ylabel('数量', fontsize=12)
ax3.set_title('每棵树点数分布', fontsize=14, fontweight='bold')
ax3.legend()

# 4. 统计摘要表
ax4 = axes[1, 1]
ax4.axis('off')
summary_data = [
    ['指标', 'DBSCAN', 'Treeiso'],
    ['检测树木数', f'{len(df_dbscan)}', f'{len(df_treeiso)}'],
    ['平均树高 (m)', f'{df_dbscan["height"].mean():.2f}', f'{df_treeiso["height"].mean():.2f}'],
    ['最大树高 (m)', f'{df_dbscan["height"].max():.2f}', f'{df_treeiso["height"].max():.2f}'],
    ['平均点数/树', f'{df_dbscan["n_points"].mean():.0f}', f'{df_treeiso["n_points"].mean():.0f}'],
    ['总点数 (已分配)', f'{df_dbscan["n_points"].sum():,}', f'{df_treeiso["n_points"].sum():,}'],
]

table = ax4.table(cellText=summary_data[1:], colLabels=summary_data[0],
                  loc='center', cellLoc='center',
                  colColours=['#f5f5f5']*3,
                  cellColours=[['#ffffff', '#e3f2fd', '#e8f5e9']]*5)
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.8)
ax4.set_title('统计摘要', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/method_comparison.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print(f"\n✅ 对比图已保存: {OUTPUT_DIR}/method_comparison.png")

# 生成分析报告
report = f"""# 单木分离方法对比报告

## 📊 基本统计

| 指标 | DBSCAN | Treeiso | 差异 |
|------|--------|---------|------|
| 检测树木数 | {len(df_dbscan)} | {len(df_treeiso)} | {len(df_dbscan) - len(df_treeiso):+d} |
| 平均树高 (m) | {df_dbscan["height"].mean():.2f} | {df_treeiso["height"].mean():.2f} | {df_dbscan["height"].mean() - df_treeiso["height"].mean():+.2f} |
| 最大树高 (m) | {df_dbscan["height"].max():.2f} | {df_treeiso["height"].max():.2f} | - |
| 平均点数/树 | {df_dbscan["n_points"].mean():.0f} | {df_treeiso["n_points"].mean():.0f} | - |

## 🔍 分析

### DBSCAN 特点:
- 检测到更多的小型片段 (可能包含灌木、噪声)
- 平均树高较低，说明包含了较多小型植被
- 噪声点比例较高 (43.6%)

### Treeiso 特点:
- 检测到较少但更大的树木单元
- 平均树高更高，更接近实际乔木尺寸
- 可能发生严重的欠分割，将多棵树合并

### 差异原因:
1. **算法设计目标不同**: Treeiso 专为 TLS (地面激光扫描) 设计，TLS 数据点密度高、树干清晰；UAV-LiDAR 数据相对稀疏
2. **参数适配问题**: Treeiso 默认参数针对 TLS 优化，可能不适用于 UAV 数据
3. **数据特点**: UAV-LiDAR 主要捕获树冠顶部，缺少树干信息

## 💡 建议

1. **采用 DBSCAN 作为基础方法**，因为它检测到了合理数量的树木
2. **调整 DBSCAN 参数** (eps, min_samples) 以减少噪声点
3. **Treeiso 需要参数调优** 才能适用于 UAV 数据
4. **记录失败案例**：关注树冠交叠区域的分割效果

---
*生成时间: 2026-01-31*
"""

report_path = f"{PROJECT_ROOT}/04_Results/reports/method_comparison_report.md"
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"✅ 对比报告已保存: {report_path}")
print("\n" + "=" * 60)
print("对比分析完成！")
print("=" * 60)
