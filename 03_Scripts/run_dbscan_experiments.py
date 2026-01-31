"""
DBSCAN 参数实验脚本
自动测试多组参数组合，找到最佳分割效果
"""

import numpy as np
import pandas as pd
from datetime import datetime
import os
from tree_isolation_dbscan import load_point_cloud, isolate_trees_dbscan


def run_experiments(input_file, output_csv):
    """
    系统性测试 DBSCAN 参数组合
    """
    print("=" * 60)
    print("DBSCAN 参数实验")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载数据
    pcd, points = load_point_cloud(input_file)
    
    # 参数网格
    eps_values = [0.3, 0.5, 0.8, 1.0, 1.5]
    min_samples_values = [30, 50, 100, 150]
    use_2d_values = [True, False]
    
    results = []
    total = len(eps_values) * len(min_samples_values) * len(use_2d_values)
    current = 0
    
    for use_2d in use_2d_values:
        for eps in eps_values:
            for min_samples in min_samples_values:
                current += 1
                mode = "2D" if use_2d else "3D"
                print(f"\n[{current}/{total}] eps={eps}, min_samples={min_samples}, mode={mode}")
                
                labels, n_trees = isolate_trees_dbscan(
                    points, eps, min_samples, use_2d
                )
                
                n_noise = (labels == -1).sum()
                noise_ratio = n_noise / len(points)
                
                # 计算平均每棵树的点数
                if n_trees > 0:
                    tree_sizes = []
                    for label in set(labels):
                        if label != -1:
                            tree_sizes.append((labels == label).sum())
                    avg_points = np.mean(tree_sizes)
                    std_points = np.std(tree_sizes)
                else:
                    avg_points = 0
                    std_points = 0
                
                results.append({
                    'eps': eps,
                    'min_samples': min_samples,
                    'use_2d': use_2d,
                    'n_trees': n_trees,
                    'n_noise': n_noise,
                    'noise_ratio': round(noise_ratio, 4),
                    'avg_points_per_tree': round(avg_points, 1),
                    'std_points': round(std_points, 1)
                })
    
    # 保存实验结果
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    
    print("\n" + "=" * 60)
    print("实验完成！")
    print(f"结果保存到: {output_csv}")
    print("=" * 60)
    
    # 显示最佳结果
    print("\n🏆 推荐参数（按树数量排序，噪声比例 < 30%）:")
    good_results = df[(df['noise_ratio'] < 0.3) & (df['n_trees'] > 50)]
    if len(good_results) > 0:
        print(good_results.sort_values('n_trees', ascending=False).head(5).to_string(index=False))
    else:
        print("没有找到符合条件的参数，尝试调整阈值")
        print(df.sort_values('n_trees', ascending=False).head(5).to_string(index=False))
    
    return df


if __name__ == "__main__":
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
    OUTPUT_CSV = f"{PROJECT_ROOT}/04_Results/tables/dbscan_experiments.csv"
    
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    df = run_experiments(INPUT_FILE, OUTPUT_CSV)
