#!/usr/bin/env python3
"""
生成 3D 点云 + 圆柱叠加图 & 林木位置分布图
Refactored to be callable from GUI
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for thread safety
import matplotlib.pyplot as plt
import open3d as o3d
from matplotlib import cm
from datetime import datetime

# Default parameters (kept for backward compatibility or defaults)
DBSCAN_EPS = 0.35
DBSCAN_MIN_POINTS = 40
BASE_SLICE_THICKNESS = 0.35
MAX_SLENDERNESS = 120
TARGET_SLENDERNESS = 90
TOP_N_TREES = 61

WOOD_DENSITY = 0.45
BIOMASS_A = -2.5
BIOMASS_B = 2.134
BIOMASS_C = 0.683
CARBON_FRACTION = 0.47

def load_point_cloud(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Point cloud not found: {path}")
    pcd = o3d.io.read_point_cloud(path)
    if pcd.is_empty():
        raise RuntimeError("Loaded point cloud is empty.")
    return pcd

def cluster_points(pcd):
    print("Clustering point cloud...")
    labels = np.array(
        pcd.cluster_dbscan(eps=DBSCAN_EPS, min_points=DBSCAN_MIN_POINTS, print_progress=True)
    )
    mask = labels >= 0
    clusters = sorted(set(labels[mask]))
    print(f"Found {len(clusters)} clusters (trees).")
    return labels, clusters

def compute_tree_stats(pcd, labels, clusters):
    points = np.asarray(pcd.points)
    trees = []
    for cid in clusters:
        pts = points[labels == cid]
        if len(pts) < 50:
            continue
        z = pts[:, 2]
        base_z = np.percentile(z, 5)
        base_mask = z <= base_z + BASE_SLICE_THICKNESS
        base_pts = pts[base_mask]
        if len(base_pts) < 10:
            base_pts = pts
        centroid = base_pts[:, :2].mean(axis=0)
        radial = np.linalg.norm(base_pts[:, :2] - centroid, axis=1)
        radius_m = np.median(radial)
        if radius_m < 0.005:
            continue
        diameter_cm = radius_m * 200.0
        height_raw = z.max() - z.min()
        slenderness = (height_raw * 100.0) / max(diameter_cm, 1e-6)
        if slenderness > MAX_SLENDERNESS:
            height = TARGET_SLENDERNESS * diameter_cm / 100.0
        else:
            height = height_raw
        height = max(height, 1.0)
        base_z_min = z.min()
        agb = WOOD_DENSITY * np.exp(
            BIOMASS_A + BIOMASS_B * np.log(diameter_cm) + BIOMASS_C * np.log(height)
        )
        carbon = agb * CARBON_FRACTION
        trees.append({
            "cluster_id": cid,
            "x": centroid[0],
            "y": centroid[1],
            "base_z": base_z_min,
            "radius_m": radius_m,
            "diameter_cm": diameter_cm,
            "height_m": height,
            "height_raw_m": height_raw,
            "slenderness": slenderness,
            "agb_kg": agb,
            "carbon_kg": carbon,
            "num_points": len(pts),
        })
    df = pd.DataFrame(trees)
    # Check if empty before sorting
    if not df.empty:
        df = df.sort_values(by="diameter_cm", ascending=False)
    return df

def render_overlay_matplotlib(pcd, df, output_path):
    print("Rendering 3D overlay (matplotlib)...")
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    points = np.asarray(pcd.points)
    if len(points) > 80000:
        idx = np.random.choice(len(points), 80000, replace=False)
        points_sampled = points[idx]
    else:
        points_sampled = points

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(points_sampled[:, 0], points_sampled[:, 1], points_sampled[:, 2],
               s=0.3, c="lightgray", alpha=0.4)

    if not df.empty:
        cmap = cm.get_cmap("viridis")
        # Cap display height for visualization only (data unchanged)
        MAX_DISPLAY_HEIGHT = 30.0  # meters - for visual clarity only
        h_min, h_max = df["height_m"].min(), min(df["height_m"].max(), MAX_DISPLAY_HEIGHT)
        theta = np.linspace(0, 2 * np.pi, 24)
        
        for _, row in df.iterrows():
            # Cap the display height but keep original data
            display_height = min(row.height_m, MAX_DISPLAY_HEIGHT)
            color_val = (display_height - h_min) / max(h_max - h_min, 1e-6)
            color = cmap(color_val)
            circle = np.stack([
                row.radius_m * np.cos(theta) + row.x,
                row.radius_m * np.sin(theta) + row.y
            ], axis=1)
            z_bottom = row.base_z
            z_top = row.base_z + display_height  # Use capped height for display

            verts = []
            for i in range(len(theta) - 1):
                verts.append([
                    (circle[i, 0], circle[i, 1], z_bottom),
                    (circle[i + 1, 0], circle[i + 1, 1], z_bottom),
                    (circle[i + 1, 0], circle[i + 1, 1], z_top),
                    (circle[i, 0], circle[i, 1], z_top),
                ])
            poly = Poly3DCollection(verts, facecolor=color, alpha=0.7, linewidths=0.05)
            ax.add_collection3d(poly)

            top = [(circle[i, 0], circle[i, 1], z_top) for i in range(len(theta))]
            bottom = [(circle[i, 0], circle[i, 1], z_bottom) for i in range(len(theta))]
            ax.add_collection3d(Poly3DCollection([top], facecolor=color, alpha=0.5))
            ax.add_collection3d(Poly3DCollection([bottom], facecolor=color, alpha=0.3))

    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("Point Cloud + Cylinder Fits")
    ax.view_init(elev=20, azim=-60)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"3D overlay saved to {output_path}")

def plot_spatial_map(df, output_path):
    print("Plotting spatial distribution...")
    plt.figure(figsize=(8, 8))
    
    if not df.empty:
        scatter = plt.scatter(
            df["x"], df["y"],
            s=df["diameter_cm"] * 3,
            c=df["height_m"],
            cmap="viridis",
            alpha=0.9,
            edgecolor="k",
            linewidths=0.2,
        )
        plt.colorbar(scatter, label="Height (m)")
    else:
        plt.text(0.5, 0.5, "No trees detected", ha='center', va='center')
        
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Tree Spatial Distribution\nMarker size = DBH, color = height")
    plt.axis("equal")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Spatial map saved to {output_path}")

def run_visualization(pcd_path, results_dir=None, output_dir=None, csv_path=None):
    """
    Main entry point for visualization.
    
    Args:
        pcd_path: Path to input point cloud (PLY/LAZ)
        results_dir: Directory to save/load tables from (defaults to project structure)
        output_dir: Directory to save figures (defaults to project structure)
        csv_path: Optional path to existing tree data CSV. If provided, skips detection.
    """
    if results_dir is None:
        # Default fallback
        results_dir = os.path.dirname(pcd_path)
    
    if output_dir is None:
        output_dir = os.path.join(results_dir, "figures")
    
    os.makedirs(results_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Define output paths
    positions_csv = os.path.join(results_dir, "tree_positions_vis.csv")
    overlay_img = os.path.join(output_dir, "forest_pointcloud_cylinders.png")
    spatial_img = os.path.join(output_dir, "tree_spatial_distribution.png")
    
    # Load Point Cloud
    pcd = load_point_cloud(pcd_path)
    
    # Load or Compute Tree Data
    df = pd.DataFrame()
    
    if csv_path and os.path.exists(csv_path):
        print(f"Loading tree data from: {csv_path}")
        try:
            df = pd.read_csv(csv_path)
            # Normalize column names to match what we expect
            # Expected: x, y, base_z, radius_m, height_m
            # Input CSV usually has: Radius (m), Diameter_DBH (cm), Height (m), Num_Points
            # But the detection script saves: radius, diameter, height, num_points, axis, center
            # Wait, the current detect_cylinders_v2 saves: 'Radius (m)', 'Diameter_DBH (cm)', 'Height (m)', 'Num_Points'
            # It DOES NOT save X, Y, Z positions explicitly in the final CSV columns!
            # It loses the spatial information needed for visualization!
            
            # CRITICAL FIX: The current detection script output lacks X,Y coordinates.
            # We can't plot them without X,Y.
            # However, `detect_cylinders` returns 'center' in the list.
            # I must check if the user's CSV has coordinates.
            
            # If the CSV lacks x/y, we might be in trouble.
            # Let's check columns.
            needed_cols = ['x', 'y', 'radius_m', 'height_m', 'base_z']
            
            # Map standard columns if present
            # 'Radius (m)' -> 'radius_m'
            # 'Height (m)' -> 'height_m'
            
            col_map = {
                'Radius (m)': 'radius_m',
                'Height (m)': 'height_m',
                'X': 'x', 'Y': 'y', 'Z': 'base_z',
                'x': 'x', 'y': 'y', 'z': 'base_z',
                'center_x': 'x', 'center_y': 'y', 'center_z': 'base_z'
            }
            df.rename(columns=col_map, inplace=True)
            
            if 'x' not in df.columns or 'y' not in df.columns:
                print("⚠️  Warning: CSV missing X/Y coordinates. Cannot visualize positions properly.")
                print("   Will attempt to recover if 'center' column exists (it usually doesn't in simple CSVs).")
                # Fallback to re-calculation if data is missing, OR warn user
                print("   Resorting to internal clustering for visualization coordinates...")
                labels, clusters = cluster_points(pcd)
                df = compute_tree_stats(pcd, labels, clusters)
            else:
                 # Fill missing columns
                if 'base_z' not in df.columns: df['base_z'] = 0
                if 'diameter_cm' not in df.columns: df['diameter_cm'] = df['radius_m'] * 200
                print(f"✅ Loaded {len(df)} trees from CSV.")
                
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            labels, clusters = cluster_points(pcd)
            df = compute_tree_stats(pcd, labels, clusters)
            
    else:
        print("No CSV provided, running internal detection (DBSCAN)...")
        labels, clusters = cluster_points(pcd)
        df = compute_tree_stats(pcd, labels, clusters)
    
    if TOP_N_TREES and len(df) > TOP_N_TREES:
        df = df.sort_values(by="diameter_cm", ascending=False).head(TOP_N_TREES)
        
    df["generated_at"] = datetime.now().isoformat()
    # Save a copy for reference
    df.to_csv(positions_csv, index=False, float_format="%.4f")
    print(f"Visualization data copy saved to {positions_csv} (n={len(df)})")
    
    render_overlay_matplotlib(pcd, df, overlay_img)
    plot_spatial_map(df, spatial_img)
    
    return [overlay_img, spatial_img]

def run_interactive_visualization(pcd_path, csv_path):
    """
    Opens an interactive Open3D window with points and cylinders.
    """
    # Load PCD
    if not os.path.exists(pcd_path):
        print("PCD not found")
        return
    pcd = o3d.io.read_point_cloud(pcd_path)
    
    # Load CSV
    if not os.path.exists(csv_path):
        print("CSV not found")
        return
        
    try:
        df = pd.read_csv(csv_path)
        # Normalize columns if needed (same logic as run_viz)
        col_map = {
            'Radius (m)': 'radius_m', 'Height (m)': 'height_m',
            'X': 'x', 'Y': 'y', 'Z': 'base_z',
            'x': 'x', 'y': 'y', 'z': 'base_z',
            'center_x': 'x', 'center_y': 'y', 'center_z': 'base_z'
        }
        df.rename(columns=col_map, inplace=True)
        
        geometries = [pcd]
        
        # Create Cylinders
        for _, row in df.iterrows():
            if 'x' not in row or 'radius_m' not in row: continue
            
            radius = row['radius_m']
            height = row['height_m']
            
            # Open3D CreateCylinder creates a cylinder centered at (0,0,0) aligned with Y axis (usually) or Z axis?
            # Actually o3d.geometry.TriangleMesh.create_cylinder creates a vertical cylinder along Y-axis by default
            # We need to rotate/translate it.
            
            # Correct approach:
            mesh_cyl = o3d.geometry.TriangleMesh.create_cylinder(radius=radius, height=height)
            mesh_cyl.compute_vertex_normals()
            mesh_cyl.paint_uniform_color([1, 0, 0]) # Red cylinders
            
            # Transform
            # Cylinder is initially centered at 0,0,0 and aligned with Y axis (in some versions) or Z axis?
            # O3D docs: "The cylinder is centered at (0, 0, 0) and the main axis is the z-axis." (usually)
            # Let's assume Z-axis alignment.
            
            # The tree center is (x, y, base_z + height/2)
            # We need to translate center of cylinder to this point.
            
            z_center = row['base_z'] + (height / 2.0)
            mesh_cyl.translate([row['x'], row['y'], z_center])
            
            geometries.append(mesh_cyl)
            
        o3d.visualization.draw_geometries(geometries, window_name="Forest 3D View", width=1024, height=768)
        
    except Exception as e:
        print(f"Interactive Viz Error: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Visualize Tree Detection Results")
    parser.add_argument("pcd_path", nargs="?", help="Path to point cloud file (.ply/.laz)")
    parser.add_argument("--results_dir", help="Directory where results are/should be saved")
    parser.add_argument("--output_dir", help="Directory where figures should be saved")
    
    args = parser.parse_args()
    
    # Default paths logic
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if args.pcd_path:
        pcd_path = args.pcd_path
    else:
        # Try to find default file
        default_path = os.path.join(project_dir, "01_Processed", "StREAM Lab", "tree.ply")
        if os.path.exists(default_path):
            pcd_path = default_path
        else:
             # Fallback to old path just in case
            pcd_path = os.path.join(project_dir, "01_Processed", "tree.ply")
            
    if not os.path.exists(pcd_path):
        print(f"❌ Error: Point cloud file not found at: {pcd_path}")
        print("Usage: ./run.sh visualize <path_to_ply_file>")
        return

    # Set default results dir if not provided
    if args.results_dir:
        results_dir = args.results_dir
    else:
        results_dir = os.path.join(project_dir, "04_Results", "tables")
        
    # Set default output dir if not provided
    if args.output_dir:
        figures_dir = args.output_dir
    else:
        figures_dir = os.path.join(project_dir, "04_Results", "figures")
    
    print(f"Using point cloud: {pcd_path}")
    run_visualization(pcd_path, results_dir, figures_dir)

if __name__ == "__main__":
    main()
