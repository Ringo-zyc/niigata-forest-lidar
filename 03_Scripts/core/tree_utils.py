
import numpy as np
import open3d as o3d
from sklearn.decomposition import PCA

def fit_cylinder_ransac(points, n_iterations=1000, threshold=0.05):
    """
    使用 RANSAC 拟合圆柱体
    
    Args:
        points: numpy array of shape (N, 3)
        n_iterations: RANSAC iterations
        threshold: distance threshold for inliers
        
    Returns:
        dict with keys: axis, center, radius, height, inliers, num_points
        or None if fitting fails
    """
    best_inliers = []
    best_params = None
    
    n_points = len(points)
    if n_points < 3:
        return None
    
    # Pre-allocate random indices for speed improvement if needed, 
    # but basic loop is fine for this scale
    
    for _ in range(n_iterations):
        # 随机选择3个点
        idx = np.random.choice(n_points, 3, replace=False)
        sample_points = points[idx]
        
        try:
            # 使用 PCA 估算圆柱体轴方向
            pca = PCA(n_components=3)
            pca.fit(sample_points)
            axis = pca.components_[0]  # 主方向
            
            # 估算圆柱体中心（投影到轴的平面）
            center = sample_points.mean(axis=0)
            
            # 计算每个点到圆柱体轴的距离
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
        except Exception:
            continue
    
    if len(best_inliers) < 3:
        return None
    
    # 用所有内点重新拟合以获得更好的参数
    inlier_points = points[best_inliers]
    
    try:
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
            'num_points': best_inliers.sum()
        }
    except Exception:
        return None

def detect_cylinders(points, min_points, distance_threshold, min_radius, 
                     max_radius, min_height, max_iterations, log_callback=None):
    """
    检测多个圆柱体
    
    Args:
        points: (N, 3) numpy array
        min_points: minimum points for a valid cylinder
        distance_threshold: RANSAC distance threshold
        min_radius: minimum radius (m)
        max_radius: maximum radius (m)
        min_height: minimum height (m)
        max_iterations: maximum number of cylinders to detect
        log_callback: function(str) -> None for logging messages
    
    Returns:
        list of dicts containing cylinder parameters
    """
    cylinders = []
    remaining_mask = np.ones(len(points), dtype=bool)
    
    if log_callback:
        log_callback(f"点云共有 {len(points)} 个点")
        log_callback("开始检测圆柱体...\n")
    
    for iteration in range(max_iterations):
        remaining_points = points[remaining_mask]
        
        if len(remaining_points) < min_points:
            break
        
        # 拟合圆柱体
        result = fit_cylinder_ransac(remaining_points, n_iterations=500, threshold=distance_threshold)
        
        if result is None:
            break
        
        # 检查参数是否合理
        if (min_radius <= result['radius'] <= max_radius and 
            result['height'] >= min_height and
            result['num_points'] >= min_points):
            
            cyl_data = {
                'radius': result['radius'],
                'diameter': result['radius'] * 2 * 100,  # 转厘米
                'height': result['height'],
                'num_points': result['num_points'],
                'axis': result['axis'],
                'center': result['center']
            }
            cylinders.append(cyl_data)
            
            msg = (f"  圆柱体 #{len(cylinders)}: "
                   f"r={result['radius']:.3f}m, "
                   f"d={result['radius']*2*100:.1f}cm, "
                   f"h={result['height']:.2f}m, "
                   f"{result['num_points']} 点")
            if log_callback:
                log_callback(msg)
            
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
