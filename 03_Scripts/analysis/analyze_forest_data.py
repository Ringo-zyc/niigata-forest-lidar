#!/usr/bin/env python3
"""
树木数据清洗和林业分析脚本
功能：
1. 数据清洗（剔除噪点和异常值）
2. 计算径阶分布
3. 计算生物量和碳储量
4. 生成可视化图表
5. 输出分析报告
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import json
from datetime import datetime

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

PROJECT_DIR = "/Users/zyc/Downloads/Niigata_Research_Prep"
OUTPUT_ROOT = os.path.join(PROJECT_DIR, "04_Results")
FIGURES_DIR = os.path.join(OUTPUT_ROOT, "figures")
TABLES_DIR = os.path.join(OUTPUT_ROOT, "tables")
REPORTS_DIR = os.path.join(OUTPUT_ROOT, "reports")
for _dir in (FIGURES_DIR, TABLES_DIR, REPORTS_DIR):
    os.makedirs(_dir, exist_ok=True)

# 文件路径
INPUT_CSV = "/Users/zyc/Downloads/Niigata_Research_Prep/04_Results/tables/tree_cylinders.csv"
CLEANED_CSV = os.path.join(TABLES_DIR, "tree_cylinders_cleaned.csv")
REPORT_FILE = os.path.join(REPORTS_DIR, "forest_analysis_report.txt")
REPORT_JSON = os.path.join(TABLES_DIR, "forest_analysis_data.json")

# 数据清洗参数
MIN_DIAMETER_CM = 5.0      # 最小胸径 (cm)
MAX_DIAMETER_CM = 100.0    # 最大胸径 (cm)
MIN_POINTS = 30            # 最小点数（可信度阈值）
MIN_HEIGHT_M = 1.0         # 最小树高 (m)
MAX_HEIGHT_M = 80.0        # 最大树高 (m)
# 高度修正参数（基于径高比/细长比控制）
MAX_SLENDERNESS_RATIO = 120    # 允许的最大细长比 (Height / DBH_in_m)
TARGET_SLENDERNESS_RATIO = 90  # 调整时使用的目标细长比

# 生物量计算参数（针叶树通用公式）
# AGB = ρ * exp(a + b*ln(DBH) + c*ln(H))
# 日本常用的针叶树异速生长方程
WOOD_DENSITY = 0.45        # 木材密度 (g/cm³) - 针叶树平均值
BIOMASS_A = -2.5           # 异速生长参数 a
BIOMASS_B = 2.134          # 异速生长参数 b
BIOMASS_C = 0.683          # 异速生长参数 c
CARBON_FRACTION = 0.47     # 碳含量比例（干重的47%）

# 径阶分布设置
DBH_BINS = [0, 5, 10, 15, 20, 25, 30, 35, 40, 50, 60, 100]  # 径阶范围 (cm)

def load_data():
    """加载数据"""
    print("=" * 60)
    print("第一步：加载原始数据")
    print("=" * 60)
    
    df = pd.read_csv(INPUT_CSV)
    print(f"✅ 成功加载数据")
    print(f"   原始数据行数: {len(df)} 棵树")
    print(f"   数据列: {', '.join(df.columns)}")
    
    return df

def clean_data(df):
    """数据清洗"""
    print("\n" + "=" * 60)
    print("第二步：数据清洗")
    print("=" * 60)
    
    original_count = len(df)
    cleaning_log = []
    
    # 记录原始数据统计
    print(f"\n原始数据统计:")
    print(f"  总数: {original_count} 棵树")
    print(f"  直径范围: {df['Diameter_DBH (cm)'].min():.2f} - {df['Diameter_DBH (cm)'].max():.2f} cm")
    print(f"  高度范围: {df['Height (m)'].min():.2f} - {df['Height (m)'].max():.2f} m")
    print(f"  点数范围: {df['Num_Points'].min()} - {df['Num_Points'].max()}")
    
    # 1. 剔除直径过小的（小树枝）
    mask_small_diameter = df['Diameter_DBH (cm)'] < MIN_DIAMETER_CM
    removed_small = df[mask_small_diameter]
    df = df[~mask_small_diameter]
    
    if len(removed_small) > 0:
        cleaning_log.append(f"剔除直径 < {MIN_DIAMETER_CM}cm 的小树枝: {len(removed_small)} 棵")
        print(f"\n❌ 剔除小树枝（直径 < {MIN_DIAMETER_CM}cm）: {len(removed_small)} 棵")
        print(f"   示例: 直径范围 {removed_small['Diameter_DBH (cm)'].min():.2f} - {removed_small['Diameter_DBH (cm)'].max():.2f} cm")
    
    # 2. 剔除直径过大的（误判）
    mask_large_diameter = df['Diameter_DBH (cm)'] > MAX_DIAMETER_CM
    removed_large = df[mask_large_diameter]
    df = df[~mask_large_diameter]
    
    if len(removed_large) > 0:
        cleaning_log.append(f"剔除直径 > {MAX_DIAMETER_CM}cm 的误判数据: {len(removed_large)} 棵")
        print(f"\n❌ 剔除异常大径（直径 > {MAX_DIAMETER_CM}cm）: {len(removed_large)} 棵")
        print(f"   示例: 直径范围 {removed_large['Diameter_DBH (cm)'].min():.2f} - {removed_large['Diameter_DBH (cm)'].max():.2f} cm")
    
    # 3. 剔除点数过少的（可信度低）
    mask_few_points = df['Num_Points'] < MIN_POINTS
    removed_few_points = df[mask_few_points]
    df = df[~mask_few_points]
    
    if len(removed_few_points) > 0:
        cleaning_log.append(f"剔除点数 < {MIN_POINTS} 的低可信度数据: {len(removed_few_points)} 棵")
        print(f"\n❌ 剔除低可信度数据（点数 < {MIN_POINTS}）: {len(removed_few_points)} 棵")
        print(f"   示例: 点数范围 {removed_few_points['Num_Points'].min()} - {removed_few_points['Num_Points'].max()}")
    
    # 4. 剔除高度异常的
    mask_abnormal_height = (df['Height (m)'] < MIN_HEIGHT_M) | (df['Height (m)'] > MAX_HEIGHT_M)
    removed_height = df[mask_abnormal_height]
    df = df[~mask_abnormal_height]
    
    if len(removed_height) > 0:
        cleaning_log.append(f"剔除高度异常数据 (< {MIN_HEIGHT_M}m 或 > {MAX_HEIGHT_M}m): {len(removed_height)} 棵")
        print(f"\n❌ 剔除高度异常数据: {len(removed_height)} 棵")
        print(f"   示例: 高度范围 {removed_height['Height (m)'].min():.2f} - {removed_height['Height (m)'].max():.2f} m")
    
    # 总结
    cleaned_count = len(df)
    removed_total = original_count - cleaned_count
    
    print(f"\n{'─' * 60}")
    print(f"清洗结果汇总:")
    print(f"  原始数据: {original_count} 棵树")
    print(f"  剔除总数: {removed_total} 棵树 ({removed_total/original_count*100:.1f}%)")
    print(f"  保留数据: {cleaned_count} 棵树 ({cleaned_count/original_count*100:.1f}%)")
    print(f"{'─' * 60}")
    
    # 清洗后统计
    print(f"\n清洗后数据统计:")
    print(f"  直径范围: {df['Diameter_DBH (cm)'].min():.2f} - {df['Diameter_DBH (cm)'].max():.2f} cm")
    print(f"  高度范围: {df['Height (m)'].min():.2f} - {df['Height (m)'].max():.2f} m")
    print(f"  平均直径: {df['Diameter_DBH (cm)'].mean():.2f} cm (标准差: {df['Diameter_DBH (cm)'].std():.2f})")
    print(f"  平均高度: {df['Height (m)'].mean():.2f} m (标准差: {df['Height (m)'].std():.2f})")
    
    return df, cleaning_log

def adjust_heights(df):
    """根据细长比调整异常树高"""
    print("\n" + "=" * 60)
    print("第三步：树高合理化处理 (Height Adjustment)")
    print("=" * 60)
    
    df = df.copy()
    df['Height_raw (m)'] = df['Height (m)']
    df['Slenderness'] = 100.0 * df['Height (m)'] / df['Diameter_DBH (cm)']
    
    mask_too_slender = df['Slenderness'] > MAX_SLENDERNESS_RATIO
    adjusted_count = mask_too_slender.sum()
    
    if adjusted_count > 0:
        df.loc[mask_too_slender, 'Height (m)'] = (
            TARGET_SLENDERNESS_RATIO * df.loc[mask_too_slender, 'Diameter_DBH (cm)'] / 100.0
        )
        print(f"\n⚠️  检测到 {adjusted_count} 棵树的细长比超过 {MAX_SLENDERNESS_RATIO}")
        print(f"   已将其树高调整为细长比 {TARGET_SLENDERNESS_RATIO}")
        sample = df[mask_too_slender].head()
        for _, row in sample.iterrows():
            print(f"   树 (DBH={row['Diameter_DBH (cm)']:.2f}cm): "
                  f"原高度 {row['Height_raw (m)']:.2f}m → 调整后 {row['Height (m)']:.2f}m")
    else:
        print("\n✅ 未检测到异常细长比，树高保持原值")
    
    print(f"\n调整后高度范围: {df['Height (m)'].min():.2f} - {df['Height (m)'].max():.2f} m")
    print(f"调整后平均高度: {df['Height (m)'].mean():.2f} m")
    
    return df, int(adjusted_count)

def calculate_biomass(df):
    """计算生物量和碳储量"""
    print("\n" + "=" * 60)
    print("第三步：计算生物量和碳储量")
    print("=" * 60)
    
    # 使用异速生长方程计算地上生物量 (AGB)
    # AGB (kg) = ρ * exp(a + b*ln(DBH) + c*ln(H))
    
    dbh_cm = df['Diameter_DBH (cm)']
    height_m = df['Height (m)']
    
    # 计算 AGB (kg/tree)
    df['AGB_kg'] = WOOD_DENSITY * np.exp(
        BIOMASS_A + 
        BIOMASS_B * np.log(dbh_cm) + 
        BIOMASS_C * np.log(height_m)
    )
    
    # 计算碳储量 (kg C/tree)
    df['Carbon_kg'] = df['AGB_kg'] * CARBON_FRACTION
    
    # 总量统计
    total_agb = df['AGB_kg'].sum()
    total_carbon = df['Carbon_kg'].sum()
    
    # 转换为吨
    total_agb_ton = total_agb / 1000
    total_carbon_ton = total_carbon / 1000
    
    print(f"\n生物量计算参数:")
    print(f"  木材密度 (ρ): {WOOD_DENSITY} g/cm³")
    print(f"  异速生长参数: a={BIOMASS_A}, b={BIOMASS_B}, c={BIOMASS_C}")
    print(f"  碳含量比例: {CARBON_FRACTION * 100}%")
    
    print(f"\n生物量与碳储量结果:")
    print(f"  总地上生物量 (AGB): {total_agb:.2f} kg = {total_agb_ton:.3f} 吨")
    print(f"  总碳储量: {total_carbon:.2f} kg = {total_carbon_ton:.3f} 吨")
    print(f"  平均单株生物量: {df['AGB_kg'].mean():.2f} kg")
    print(f"  平均单株碳储量: {df['Carbon_kg'].mean():.2f} kg")
    
    biomass_stats = {
        'total_agb_kg': total_agb,
        'total_agb_ton': total_agb_ton,
        'total_carbon_kg': total_carbon,
        'total_carbon_ton': total_carbon_ton,
        'mean_agb_kg': df['AGB_kg'].mean(),
        'mean_carbon_kg': df['Carbon_kg'].mean()
    }
    
    return df, biomass_stats

def diameter_class_analysis(df):
    """径阶分布分析"""
    print("\n" + "=" * 60)
    print("第四步：径阶分布分析")
    print("=" * 60)
    
    # 按径阶分组
    df['DBH_Class'] = pd.cut(df['Diameter_DBH (cm)'], bins=DBH_BINS, right=False)
    dbh_distribution = df.groupby('DBH_Class', observed=False).size()
    
    print(f"\n径阶分布 (Diameter Class Distribution):")
    print(f"{'径阶 (cm)':<15} {'数量':<8} {'百分比':<10} {'柱状图'}")
    print("─" * 60)
    
    distribution_data = []
    for dbh_class, count in dbh_distribution.items():
        if count > 0:
            percentage = count / len(df) * 100
            bar = '█' * int(percentage / 2)
            print(f"{str(dbh_class):<15} {count:<8} {percentage:>5.1f}%    {bar}")
            distribution_data.append({
                'class': str(dbh_class),
                'count': int(count),
                'percentage': float(percentage)
            })
    
    return dbh_distribution, distribution_data

def generate_visualizations(df, dbh_distribution):
    """生成可视化图表"""
    print("\n" + "=" * 60)
    print("第五步：生成可视化图表")
    print("=" * 60)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('新泻研究项目 - 森林结构分析', fontsize=16, fontweight='bold')
    
    # 图1: 径阶分布柱状图
    ax1 = axes[0, 0]
    dbh_dist_filtered = dbh_distribution[dbh_distribution > 0]
    class_labels = [str(x) for x in dbh_dist_filtered.index]
    ax1.bar(range(len(dbh_dist_filtered)), dbh_dist_filtered.values, color='forestgreen', alpha=0.7, edgecolor='black')
    ax1.set_xlabel('Diameter Class (cm)', fontweight='bold')
    ax1.set_ylabel('Number of Trees', fontweight='bold')
    ax1.set_title('Diameter Class Distribution (径阶分布)', fontweight='bold')
    ax1.set_xticks(range(len(dbh_dist_filtered)))
    ax1.set_xticklabels(class_labels, rotation=45, ha='right')
    ax1.grid(axis='y', alpha=0.3)
    
    # 图2: DBH vs Height 散点图
    ax2 = axes[0, 1]
    scatter = ax2.scatter(df['Diameter_DBH (cm)'], df['Height (m)'], 
                         c=df['AGB_kg'], cmap='YlGn', alpha=0.6, edgecolor='black', s=100)
    ax2.set_xlabel('DBH (cm)', fontweight='bold')
    ax2.set_ylabel('Height (m)', fontweight='bold')
    ax2.set_title('DBH vs Height (Colored by Biomass)', fontweight='bold')
    ax2.grid(alpha=0.3)
    plt.colorbar(scatter, ax=ax2, label='AGB (kg)')
    
    # 图3: 生物量分布饼图
    ax3 = axes[1, 0]
    biomass_by_class = df.groupby('DBH_Class', observed=False)['AGB_kg'].sum()
    biomass_filtered = biomass_by_class[biomass_by_class > 0]
    colors = plt.cm.Greens(np.linspace(0.4, 0.9, len(biomass_filtered)))
    ax3.pie(biomass_filtered.values, labels=[str(x) for x in biomass_filtered.index], 
            autopct='%1.1f%%', colors=colors, startangle=90)
    ax3.set_title('Biomass Distribution by Diameter Class\n(各径阶生物量占比)', fontweight='bold')
    
    # 图4: 碳储量累积曲线
    ax4 = axes[1, 1]
    df_sorted = df.sort_values('Diameter_DBH (cm)')
    cumulative_carbon = df_sorted['Carbon_kg'].cumsum()
    ax4.plot(df_sorted['Diameter_DBH (cm)'], cumulative_carbon, 
             color='darkgreen', linewidth=2, marker='o', markersize=4)
    ax4.fill_between(df_sorted['Diameter_DBH (cm)'], cumulative_carbon, alpha=0.3, color='green')
    ax4.set_xlabel('DBH (cm)', fontweight='bold')
    ax4.set_ylabel('Cumulative Carbon (kg)', fontweight='bold')
    ax4.set_title('Cumulative Carbon Storage (碳储量累积)', fontweight='bold')
    ax4.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_plot = os.path.join(FIGURES_DIR, "forest_analysis_plots.png")
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    print(f"\n✅ 图表已保存: forest_analysis_plots.png")
    
    return output_plot

def generate_report(df, cleaning_log, biomass_stats, distribution_data, original_count, adjusted_count):
    """生成分析报告"""
    print("\n" + "=" * 60)
    print("第六步：生成分析报告")
    print("=" * 60)
    
    report = []
    report.append("=" * 80)
    report.append("新泻研究项目 - 森林结构分析报告")
    report.append("Forest Structure Analysis Report - Niigata Research Project")
    report.append("=" * 80)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"数据来源: tree_cylinders.csv")
    
    # 数据清洗部分
    report.append("\n" + "─" * 80)
    report.append("一、数据清洗结果 (Data Cleaning Results)")
    report.append("─" * 80)
    
    for log in cleaning_log:
        report.append(f"  • {log}")
    
    report.append(f"\n  原始样本: {original_count} 棵")
    report.append(f"  通过清洗: {len(df)} 棵 (剔除 {original_count - len(df)} 棵)")
    
    if adjusted_count > 0:
        report.append(f"  异常树高修正: {adjusted_count} 棵 (细长比>{MAX_SLENDERNESS_RATIO})")
        report.append(f"  修正目标细长比: {TARGET_SLENDERNESS_RATIO}")
        if 'Height_raw (m)' in df.columns:
            report.append(f"  调整前平均高度: {df['Height_raw (m)'].mean():.2f} m")
            report.append(f"  调整后平均高度: {df['Height (m)'].mean():.2f} m")
    
    # 基础统计
    report.append("\n" + "─" * 80)
    report.append("二、基础统计 (Basic Statistics)")
    report.append("─" * 80)
    
    report.append(f"\n  样本数量: {len(df)} 棵树")
    report.append(f"\n  胸径 (DBH):")
    report.append(f"    - 范围: {df['Diameter_DBH (cm)'].min():.2f} - {df['Diameter_DBH (cm)'].max():.2f} cm")
    report.append(f"    - 平均值: {df['Diameter_DBH (cm)'].mean():.2f} ± {df['Diameter_DBH (cm)'].std():.2f} cm")
    report.append(f"    - 中位数: {df['Diameter_DBH (cm)'].median():.2f} cm")
    
    report.append(f"\n  树高 (Height):")
    report.append(f"    - 范围: {df['Height (m)'].min():.2f} - {df['Height (m)'].max():.2f} m")
    report.append(f"    - 平均值: {df['Height (m)'].mean():.2f} ± {df['Height (m)'].std():.2f} m")
    report.append(f"    - 中位数: {df['Height (m)'].median():.2f} m")
    
    # 径阶分布
    report.append("\n" + "─" * 80)
    report.append("三、径阶分布 (Diameter Class Distribution)")
    report.append("─" * 80)
    report.append("\n  径阶 (cm)        数量      占比      ")
    report.append("  " + "─" * 40)
    
    for item in distribution_data:
        report.append(f"  {item['class']:<15} {item['count']:<8} {item['percentage']:>5.1f}%")
    
    # 生物量和碳储量
    report.append("\n" + "─" * 80)
    report.append("四、生物量与碳储量 (Biomass and Carbon Storage)")
    report.append("─" * 80)
    
    report.append(f"\n  计算公式: AGB = ρ × exp(a + b×ln(DBH) + c×ln(H))")
    report.append(f"  参数设置:")
    report.append(f"    - 木材密度 ρ = {WOOD_DENSITY} g/cm³")
    report.append(f"    - a = {BIOMASS_A}, b = {BIOMASS_B}, c = {BIOMASS_C}")
    report.append(f"    - 碳含量比例 = {CARBON_FRACTION * 100}%")
    
    report.append(f"\n  总量统计:")
    report.append(f"    - 地上生物量 (AGB): {biomass_stats['total_agb_ton']:.3f} 吨")
    report.append(f"    - 碳储量: {biomass_stats['total_carbon_ton']:.3f} 吨")
    report.append(f"    - CO₂当量: {biomass_stats['total_carbon_ton'] * 3.67:.3f} 吨 (碳储量 × 3.67)")
    
    report.append(f"\n  单株平均:")
    report.append(f"    - 平均生物量: {biomass_stats['mean_agb_kg']:.2f} kg/树")
    report.append(f"    - 平均碳储量: {biomass_stats['mean_carbon_kg']:.2f} kg/树")
    
    # 论文用数据
    report.append("\n" + "─" * 80)
    report.append("五、论文数据摘要 (Summary for Publication)")
    report.append("─" * 80)
    
    report.append(f"\n  样本规模:")
    report.append(f"    N = {len(df)} trees")
    
    report.append(f"\n  胸径 (DBH):")
    report.append(f"    Mean ± SD: {df['Diameter_DBH (cm)'].mean():.2f} ± {df['Diameter_DBH (cm)'].std():.2f} cm")
    report.append(f"    Range: {df['Diameter_DBH (cm)'].min():.2f} - {df['Diameter_DBH (cm)'].max():.2f} cm")
    
    report.append(f"\n  树高 (Height):")
    report.append(f"    Mean ± SD: {df['Height (m)'].mean():.2f} ± {df['Height (m)'].std():.2f} m")
    report.append(f"    Range: {df['Height (m)'].min():.2f} - {df['Height (m)'].max():.2f} m")
    
    report.append(f"\n  碳储量:")
    report.append(f"    Total: {biomass_stats['total_carbon_ton']:.3f} Mg C (= {biomass_stats['total_carbon_ton'] * 3.67:.3f} Mg CO₂e)")
    report.append(f"    Per tree: {biomass_stats['mean_carbon_kg']:.2f} ± {df['Carbon_kg'].std():.2f} kg C")
    
    # 森林结构特征
    report.append("\n" + "─" * 80)
    report.append("六、森林结构特征 (Stand Structure)")
    report.append("─" * 80)
    
    # 优势径阶（数量最多的径阶）
    dominant_class = distribution_data[0]['class'] if distribution_data else "N/A"
    report.append(f"\n  优势径阶: {dominant_class}")
    
    # DBH/Height 比率
    df['DBH_Height_Ratio'] = df['Diameter_DBH (cm)'] / df['Height (m)']
    report.append(f"  平均径高比: {df['DBH_Height_Ratio'].mean():.3f}")
    
    # 林分密度（假设样地面积）
    # 注意：这需要知道实际样地面积，这里仅作示例
    report.append(f"\n  注: 林分密度需提供样地面积信息")
    
    report.append("\n" + "=" * 80)
    report.append("报告结束")
    report.append("=" * 80)
    
    # 保存报告
    report_text = "\n".join(report)
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    print(f"\n✅ 报告已保存: forest_analysis_report.txt")
    
    return report_text

def save_results(df, biomass_stats, distribution_data, cleaning_log, original_count, adjusted_count):
    """保存所有结果"""
    print("\n" + "=" * 60)
    print("第七步：保存结果")
    print("=" * 60)
    
    # 保存清洗后的 CSV
    df.to_csv(CLEANED_CSV, index=False, float_format='%.4f')
    print(f"\n✅ 清洗后数据已保存: tree_cylinders_cleaned.csv")
    print(f"   包含列: {', '.join(df.columns)}")
    
    # 保存 JSON 格式的分析数据（便于其他工具使用）
    removed_count = original_count - len(df)
    
    analysis_data = {
        'metadata': {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'original_count': original_count,
            'cleaned_count': len(df),
            'removed_count': removed_count,
            'height_adjusted_count': adjusted_count
        },
        'cleaning_parameters': {
            'min_diameter_cm': MIN_DIAMETER_CM,
            'max_diameter_cm': MAX_DIAMETER_CM,
            'min_points': MIN_POINTS,
            'min_height_m': MIN_HEIGHT_M,
            'max_height_m': MAX_HEIGHT_M
        },
        'statistics': {
            'dbh_mean': float(df['Diameter_DBH (cm)'].mean()),
            'dbh_std': float(df['Diameter_DBH (cm)'].std()),
            'dbh_min': float(df['Diameter_DBH (cm)'].min()),
            'dbh_max': float(df['Diameter_DBH (cm)'].max()),
            'height_mean': float(df['Height (m)'].mean()),
            'height_std': float(df['Height (m)'].std()),
            'height_min': float(df['Height (m)'].min()),
            'height_max': float(df['Height (m)'].max())
        },
        'biomass': biomass_stats,
        'diameter_distribution': distribution_data,
        'cleaning_log': cleaning_log
    }
    
    with open(REPORT_JSON, 'w', encoding='utf-8') as f:
        json.dump(analysis_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 分析数据已保存: forest_analysis_data.json")

def main():
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "树木数据清洗与林业分析工具" + " " * 32 + "║")
    print("║" + " " * 24 + "Forest Data Cleaning & Analysis" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    print("\n")
    
    # 1. 加载数据
    df = load_data()
    original_count = len(df)
    
    # 2. 数据清洗
    df_cleaned, cleaning_log = clean_data(df)
    
    # 3. 树高调整
    df_cleaned, adjusted_count = adjust_heights(df_cleaned)
    
    # 3. 计算生物量（使用调整后的高度）
    df_cleaned, biomass_stats = calculate_biomass(df_cleaned)
    
    # 4. 径阶分布
    dbh_distribution, distribution_data = diameter_class_analysis(df_cleaned)
    
    # 5. 生成图表
    plot_file = generate_visualizations(df_cleaned, dbh_distribution)
    
    # 6. 生成报告
    report = generate_report(df_cleaned, cleaning_log, biomass_stats, distribution_data, original_count, adjusted_count)
    
    # 7. 保存结果
    save_results(df_cleaned, biomass_stats, distribution_data, cleaning_log, original_count, adjusted_count)
    
    # 最终总结
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 32 + "分析完成！" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝")
    
    print(f"\n📊 输出文件:")
    print(f"  1. tree_cylinders_cleaned.csv    (清洗后的数据)")
    print(f"  2. forest_analysis_plots.png     (4张可视化图表)")
    print(f"  3. forest_analysis_report.txt    (详细分析报告)")
    print(f"  4. forest_analysis_data.json     (结构化数据)")
    
    print(f"\n📈 关键结果:")
    print(f"  • 有效树木: {len(df_cleaned)} 棵")
    print(f"  • 平均胸径: {df_cleaned['Diameter_DBH (cm)'].mean():.2f} cm")
    print(f"  • 平均树高: {df_cleaned['Height (m)'].mean():.2f} m")
    print(f"  • 总碳储量: {biomass_stats['total_carbon_ton']:.3f} 吨")
    print(f"  • 树高被调整: {adjusted_count} 棵 (阈值 {MAX_SLENDERNESS_RATIO})")
    
    print(f"\n{'─' * 80}\n")

if __name__ == "__main__":
    main()
