"""
对分离出的单棵树进行 DBH 测量
整合 RANSAC 圆柱拟合

功能：
- 提取胸径高度切片 (1.3m)
- RANSAC 圆柱拟合测量 DBH
- 批量处理所有分离的树木
"""

import numpy as np
import open3d as o3d
import os
import pandas as pd
from tree_utils import fit_cylinder_ransac  # 复用你已有的代码


def extract_breast_height_slice(points, breast_height=1.3, slice_thickness=0.1):
    """
    提取胸径高度（1.3m）的切片
    
    Args:
        points: (N, 3) 点云
        breast_height: 胸径高度（相对于最低点）
        slice_thickness: 切片厚度
    
    Returns:
        切片内的点
    """
    z_min = points[:, 2].min()
    target_z = z_min + breast_height
    
    mask = (points[:, 2] >= target_z - slice_thickness/2) & \
           (points[:, 2] <= target_z + slice_thickness/2)
    
    slice_points = points[mask]
    return slice_points


def fit_circle_2d(points_2d):
    """
    2D 圆拟合（最小二乘法）
    用于切片的直径测量
    
    Args:
        points_2d: (N, 2) XY 坐标
    
    Returns:
        center: (x, y)
        radius: 半径
    """
    if len(points_2d) < 3:
        return None, None
    
    # 代数拟合
    A = np.column_stack([points_2d * 2, np.ones(len(points_2d))])
    b = np.sum(points_2d ** 2, axis=1)
    
    try:
        result = np.linalg.lstsq(A, b, rcond=None)[0]
        center = result[:2]
        radius = np.sqrt(result[2] + np.sum(center ** 2))
        return center, radius
    except:
        return None, None


def measure_tree_dbh(tree_points, min_slice_points=10, method='circle'):
    """
    测量单棵树的 DBH
    
    Args:
        tree_points: 单棵树的点云
        min_slice_points: 切片最少点数
        method: 'circle' (2D圆拟合) 或 'ransac' (3D圆柱)
    
    Returns:
        测量结果字典，或 None
    """
    # 提取切片
    slice_points = extract_breast_height_slice(tree_points)
    
    if len(slice_points) < min_slice_points:
        return None
    
    if method == 'circle':
        # 2D 圆拟合（更适合薄切片）
        center, radius = fit_circle_2d(slice_points[:, :2])
        if radius is None or radius < 0.01 or radius > 1.5:
            return None
        
        return {
            'dbh_cm': radius * 2 * 100,
            'radius_m': radius,
            'slice_points': len(slice_points),
            'method': 'circle_2d'
        }
    
    else:  # ransac
        # 3D RANSAC 拟合（你已有的方法）
        result = fit_cylinder_ransac(slice_points, n_iterations=500, threshold=0.03)
        
        if result is None:
            return None
        
        if result['radius'] < 0.01 or result['radius'] > 1.5:
            return None
        
        return {
            'dbh_cm': result['radius'] * 2 * 100,
            'radius_m': result['radius'],
            'slice_points': len(slice_points),
            'inlier_ratio': result['num_points'] / len(slice_points),
            'method': 'ransac_3d'
        }


def batch_measure_trees(input_dir, output_csv, method='circle'):
    """
    批量测量所有分离出的树木
    
    Args:
        input_dir: 包含单木 .ply 文件的目录
        output_csv: 输出 CSV 路径
        method: 测量方法
    
    Returns:
        DataFrame with measurements
    """
    print(f"\n批量测量 DBH (方法: {method})")
    print(f"输入目录: {input_dir}")
    print("-" * 50)
    
    results = []
    files = sorted([f for f in os.listdir(input_dir) 
                   if f.endswith('.ply') and f.startswith('tree_')])
    
    success = 0
    for filename in files:
        filepath = os.path.join(input_dir, filename)
        pcd = o3d.io.read_point_cloud(filepath)
        points = np.asarray(pcd.points)
        
        tree_id = filename.replace('.ply', '').replace('tree_', '')
        
        measurement = measure_tree_dbh(points, method=method)
        
        if measurement:
            height = points[:, 2].max() - points[:, 2].min()
            results.append({
                'tree_id': int(tree_id),
                'height_m': round(height, 2),
                'dbh_cm': round(measurement['dbh_cm'], 2),
                'n_points': len(points),
                'slice_points': measurement['slice_points'],
                **{k: v for k, v in measurement.items() 
                   if k not in ['dbh_cm', 'slice_points']}
            })
            success += 1
            print(f"  tree_{tree_id}: DBH = {measurement['dbh_cm']:.1f} cm, H = {height:.1f} m")
        else:
            print(f"  tree_{tree_id}: 测量失败（切片点数不足或拟合失败）")
    
    # 保存结果
    df = pd.DataFrame(results)
    if len(df) > 0:
        df = df.sort_values('tree_id')
        df.to_csv(output_csv, index=False)
        print("-" * 50)
        print(f"成功测量: {success}/{len(files)} 棵树")
        print(f"保存到: {output_csv}")
        
        print(f"\nDBH 统计:")
        print(f"  范围: {df['dbh_cm'].min():.1f} - {df['dbh_cm'].max():.1f} cm")
        print(f"  平均: {df['dbh_cm'].mean():.1f} cm")
        print(f"  中位数: {df['dbh_cm'].median():.1f} cm")
    
    return df


# 使用示例
if __name__ == "__main__":
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    INPUT_DIR = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_dbscan"
    OUTPUT_CSV = f"{PROJECT_ROOT}/04_Results/tables/isolated_trees_dbh.csv"
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    
    # 批量测量（使用 2D 圆拟合，更适合切片）
    df = batch_measure_trees(INPUT_DIR, OUTPUT_CSV, method='circle')
    
    if len(df) > 0:
        print("\n前 10 棵树:")
        print(df.head(10).to_string(index=False))
