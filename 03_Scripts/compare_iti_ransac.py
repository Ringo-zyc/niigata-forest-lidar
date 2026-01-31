"""
ITI 与 RANSAC 方法结果对比分析
Compare Individual Tree Isolation results with original RANSAC detection
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
import os


def load_ransac_results(csv_path):
    """加载原有的 RANSAC 检测结果"""
    df = pd.read_csv(csv_path)
    print(f"RANSAC 结果: {len(df)} 棵树")
    print(f"  列名: {list(df.columns)}")
    return df


def load_iti_results(csv_path):
    """加载 ITI 测量结果"""
    df = pd.read_csv(csv_path)
    print(f"ITI 结果: {len(df)} 棵树")
    print(f"  列名: {list(df.columns)}")
    return df


def match_trees_by_location(ransac_df, iti_df, distance_threshold=1.0):
    """
    通过空间位置匹配两种方法检测到的同一棵树
    
    Args:
        ransac_df: RANSAC 结果（需要有 X, Y 列）
        iti_df: ITI 结果（需要有 x_center, y_center 列）
        distance_threshold: 匹配距离阈值（米）
    
    Returns:
        matched pairs DataFrame
    """
    # 提取坐标
    if 'X' in ransac_df.columns:
        ransac_coords = ransac_df[['X', 'Y']].values
    else:
        print("警告: RANSAC 结果缺少 X, Y 列")
        return None
    
    if 'x_center' in iti_df.columns:
        iti_coords = iti_df[['x_center', 'y_center']].values
    else:
        print("警告: ITI 结果缺少 x_center, y_center 列")
        return None
    
    # 使用 KD-Tree 进行最近邻匹配
    tree = cKDTree(iti_coords)
    distances, indices = tree.query(ransac_coords, k=1)
    
    # 筛选匹配成功的
    matched = []
    for i, (dist, idx) in enumerate(zip(distances, indices)):
        if dist < distance_threshold:
            matched.append({
                'ransac_idx': i,
                'iti_idx': idx,
                'distance': dist,
                'ransac_dbh': ransac_df.iloc[i].get('Diameter_DBH (cm)', 
                             ransac_df.iloc[i].get('diameter', None)),
                'iti_dbh': iti_df.iloc[idx]['dbh_cm'],
                'ransac_x': ransac_coords[i, 0],
                'ransac_y': ransac_coords[i, 1],
                'iti_x': iti_coords[idx, 0],
                'iti_y': iti_coords[idx, 1]
            })
    
    matched_df = pd.DataFrame(matched)
    print(f"\n匹配成功: {len(matched_df)} 棵树 / RANSAC {len(ransac_df)} / ITI {len(iti_df)}")
    
    return matched_df


def calculate_comparison_stats(matched_df):
    """计算对比统计指标"""
    if matched_df is None or len(matched_df) == 0:
        print("没有匹配的树木，无法计算统计")
        return None
    
    # 计算差异
    matched_df['dbh_diff'] = matched_df['iti_dbh'] - matched_df['ransac_dbh']
    matched_df['dbh_diff_abs'] = matched_df['dbh_diff'].abs()
    matched_df['dbh_diff_pct'] = (matched_df['dbh_diff'] / matched_df['ransac_dbh']) * 100
    
    stats = {
        'n_matched': len(matched_df),
        'mean_diff': matched_df['dbh_diff'].mean(),
        'std_diff': matched_df['dbh_diff'].std(),
        'mae': matched_df['dbh_diff_abs'].mean(),
        'rmse': np.sqrt((matched_df['dbh_diff'] ** 2).mean()),
        'mean_diff_pct': matched_df['dbh_diff_pct'].mean(),
        'correlation': matched_df['ransac_dbh'].corr(matched_df['iti_dbh'])
    }
    
    print("\n📊 DBH 对比统计:")
    print(f"  匹配树木数: {stats['n_matched']}")
    print(f"  平均差异: {stats['mean_diff']:.2f} cm (ITI - RANSAC)")
    print(f"  平均绝对误差 (MAE): {stats['mae']:.2f} cm")
    print(f"  均方根误差 (RMSE): {stats['rmse']:.2f} cm")
    print(f"  相关系数: {stats['correlation']:.3f}")
    
    return stats, matched_df


def plot_comparison(matched_df, output_path):
    """生成对比图表"""
    if matched_df is None or len(matched_df) == 0:
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # 1. 散点图：RANSAC vs ITI
    ax1 = axes[0]
    ax1.scatter(matched_df['ransac_dbh'], matched_df['iti_dbh'], alpha=0.6)
    max_dbh = max(matched_df['ransac_dbh'].max(), matched_df['iti_dbh'].max()) + 5
    ax1.plot([0, max_dbh], [0, max_dbh], 'r--', label='1:1 line')
    ax1.set_xlabel('RANSAC DBH (cm)')
    ax1.set_ylabel('ITI DBH (cm)')
    ax1.set_title('DBH Comparison: RANSAC vs ITI')
    ax1.legend()
    ax1.set_aspect('equal')
    
    # 2. 差异分布直方图
    ax2 = axes[1]
    ax2.hist(matched_df['dbh_diff'], bins=20, edgecolor='black', alpha=0.7)
    ax2.axvline(x=0, color='r', linestyle='--')
    ax2.axvline(x=matched_df['dbh_diff'].mean(), color='g', linestyle='-', 
                label=f'Mean: {matched_df["dbh_diff"].mean():.2f}')
    ax2.set_xlabel('DBH Difference (ITI - RANSAC) [cm]')
    ax2.set_ylabel('Count')
    ax2.set_title('Distribution of DBH Differences')
    ax2.legend()
    
    # 3. Bland-Altman 图
    ax3 = axes[2]
    mean_dbh = (matched_df['ransac_dbh'] + matched_df['iti_dbh']) / 2
    diff = matched_df['dbh_diff']
    mean_diff = diff.mean()
    std_diff = diff.std()
    
    ax3.scatter(mean_dbh, diff, alpha=0.6)
    ax3.axhline(y=mean_diff, color='g', linestyle='-', label=f'Mean: {mean_diff:.2f}')
    ax3.axhline(y=mean_diff + 1.96*std_diff, color='r', linestyle='--', 
                label=f'+1.96 SD: {mean_diff + 1.96*std_diff:.2f}')
    ax3.axhline(y=mean_diff - 1.96*std_diff, color='r', linestyle='--',
                label=f'-1.96 SD: {mean_diff - 1.96*std_diff:.2f}')
    ax3.set_xlabel('Mean DBH (cm)')
    ax3.set_ylabel('Difference (ITI - RANSAC) [cm]')
    ax3.set_title('Bland-Altman Plot')
    ax3.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n图表已保存: {output_path}")
    plt.show()


def run_comparison(ransac_csv, iti_csv, output_dir):
    """运行完整对比分析"""
    print("=" * 60)
    print("ITI vs RANSAC 方法对比分析")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载数据
    ransac_df = load_ransac_results(ransac_csv)
    iti_df = load_iti_results(iti_csv)
    
    # 匹配
    matched_df = match_trees_by_location(ransac_df, iti_df)
    
    if matched_df is not None and len(matched_df) > 0:
        # 统计
        stats, matched_df = calculate_comparison_stats(matched_df)
        
        # 保存匹配结果
        output_csv = os.path.join(output_dir, 'iti_ransac_comparison.csv')
        matched_df.to_csv(output_csv, index=False)
        print(f"\n匹配结果已保存: {output_csv}")
        
        # 生成图表
        output_fig = os.path.join(output_dir, 'iti_ransac_comparison.png')
        plot_comparison(matched_df, output_fig)
        
        return stats, matched_df
    
    return None, None


if __name__ == "__main__":
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    
    # 文件路径
    RANSAC_CSV = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m_cylinders.csv"
    ITI_CSV = f"{PROJECT_ROOT}/04_Results/iti_pipeline_output/tree_measurements.csv"
    OUTPUT_DIR = f"{PROJECT_ROOT}/04_Results/reports"
    
    # 运行对比
    stats, matched = run_comparison(RANSAC_CSV, ITI_CSV, OUTPUT_DIR)
