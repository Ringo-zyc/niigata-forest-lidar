#!/usr/bin/env python3
"""
使用 RANSAC 从点云中检测圆柱体（树木）
"""
import open3d as o3d
import numpy as np
import csv
import os
from scipy.spatial import KDTree
from sklearn.decomposition import PCA

# 配置参数
INPUT_FILE = "/Users/zyc/Downloads/Niigata_Research_Prep/01_Processed/tree.ply"
OUTPUT_CSV = "/Users/zyc/Downloads/Niigata_Research_Prep/04_Results/tree_cylinders.csv"

# RANSAC 参数
DISTANCE_THRESHOLD = 0.06  # 点到圆柱体的最大距离
MIN_POINTS = 50           # 一个圆柱体的最少点数
MIN_RADIUS = 0.03         # 最小半径 (m)
MAX_RADIUS = 0.8          # 最大半径 (m)
MIN_HEIGHT = 1.0          # 最小高度 (m)
MAX_ITERATIONS = 100      # 最多检测多少个圆柱体

def fit_cylinder_ransac(points, n_iterations=1000, threshold=0.05):
    """
    使用 RANSAC 拟合圆柱体
    返回: (axis_direction, center_point, radius, inliers)
    """
    best_inliers = []
    best_params = None
    
    n_points = len(points)
    if n_points < 3:
        return None
    
    for _ in range(n_iterations):
        # 随机选择3个点
        idx = np.random.choice(n_points, 3, replace=False)
        sample_points = points[idx]
        
        # 使用 PCA 估算圆柱体轴方向
        pca = PCA(n_components=3)
        pca.fit(sample_points)
        axis = pca.components_[0]  # 主方向
        
        # 估算圆柱体中心（投影到轴的平面）
        center = sample_points.mean(axis=0)
        
        # 计算每个点到圆柱体轴的距离
        # 点到轴的距离 = ||(p - center) - ((p - center) · axis) * axis||
        vectors = points - center
        projections = np.dot(vectors, axis)[:, np.newaxis] * axis
        perpendiculars = vectors - projections
        distances = np.linalg.norm(perpendiculars, axis=1)
        
        # 估算半径
        radius = np.median(distances[distances < threshold])
        
        # 找到内点
        inliers = np.abs(distances - radius) < threshold
        
        if inliers.sum() > len(best_inliers):
            best_inliers = inliers
            best_params = (axis, center, radius)
    
    if len(best_inliers) < MIN_POINTS:
        return None
    
    # 用所有内点重新拟合以获得更好的参数
    inlier_points = points[best_inliers]
    pca = PCA(n_components=3)
    pca.fit(inlier_points)
    axis = pca.components_[0]
    center = inlier_points.mean(axis=0)
    
    vectors = inlier_points - center
    projections = np.dot(vectors, axis)[:, np.newaxis] * axis
    perpendiculars = vectors - projections
    distances = np.linalg.norm(perpendiculars, axis=1)
    radius = np.median(distances)
    
    # 计算高度
    heights_along_axis = np.dot(inlier_points - center, axis)
    height = heights_along_axis.max() - heights_along_axis.min()
    
    return {
        'axis': axis,
        'center': center,
        'radius': radius,
        'height': height,
        'inliers': best_inliers,
        'num_points': inliers.sum()
    }

def detect_cylinders(pcd):
    """检测多个圆柱体"""
    points = np.asarray(pcd.points)
    cylinders = []
    remaining_mask = np.ones(len(points), dtype=bool)
    
    print(f"点云共有 {len(points)} 个点")
    print("开始检测圆柱体...\n")
    
    for iteration in range(MAX_ITERATIONS):
        remaining_points = points[remaining_mask]
        
        if len(remaining_points) < MIN_POINTS:
            break
        
        # 拟合圆柱体
        result = fit_cylinder_ransac(remaining_points, n_iterations=500, threshold=DISTANCE_THRESHOLD)
        
        if result is None:
            break
        
        # 检查参数是否合理
        if (MIN_RADIUS <= result['radius'] <= MAX_RADIUS and 
            result['height'] >= MIN_HEIGHT and
            result['num_points'] >= MIN_POINTS):
            
            cylinders.append({
                'radius': result['radius'],
                'diameter': result['radius'] * 2 * 100,  # 转厘米
                'height': result['height'],
                'num_points': result['num_points']
            })
            
            print(f"  圆柱体 #{len(cylinders)}: "
                  f"r={result['radius']:.3f}m, "
                  f"d={result['radius']*2*100:.1f}cm, "
                  f"h={result['height']:.2f}m, "
                  f"{result['num_points']} 点")
            
            # 更新 remaining_mask
            remaining_indices = np.where(remaining_mask)[0]
            inlier_global_indices = remaining_indices[result['inliers']]
            remaining_mask[inlier_global_indices] = False
        else:
            # 如果检测到的不符合条件，移除一部分点后继续
            remaining_indices = np.where(remaining_mask)[0]
            inlier_global_indices = remaining_indices[result['inliers']]
            remaining_mask[inlier_global_indices] = False
    
    return cylinders

def save_results(cylinders, output_path):
    """保存结果到 CSV"""
    if not cylinders:
        print("\n⚠️  未检测到任何圆柱体")
        print("提示：可能需要调整参数 MIN_RADIUS, MAX_RADIUS, MIN_HEIGHT, DISTANCE_THRESHOLD")
        return
    
    # 按直径排序
    cylinders.sort(key=lambda x: x['diameter'], reverse=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Radius (m)', 'Diameter_DBH (cm)', 'Height (m)', 'Num_Points'])
        for cyl in cylinders:
            writer.writerow([
                f"{cyl['radius']:.4f}",
                f"{cyl['diameter']:.2f}",
                f"{cyl['height']:.2f}",
                cyl['num_points']
            ])
    
    print(f"\n✅ 成功！检测到 {len(cylinders)} 棵树")
    print(f"结果已保存到: {output_path}")

def main():
    # 检查文件
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 文件不存在: {INPUT_FILE}")
        return
    
    # 加载点云
    print(f"正在加载点云: {INPUT_FILE}")
    pcd = o3d.io.read_point_cloud(INPUT_FILE)
    
    if len(pcd.points) == 0:
        print("❌ 点云为空")
        return
    
    print(f"✅ 成功加载 {len(pcd.points)} 个点\n")
    
    # 检测圆柱体
    cylinders = detect_cylinders(pcd)
    
    # 保存结果
    save_results(cylinders, OUTPUT_CSV)

if __name__ == "__main__":
    main()
