#!/usr/bin/env python3
"""
生成 3D 点云 + 圆柱叠加图 & 林木位置分布图
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import open3d as o3d
from matplotlib import cm
from datetime import datetime

PROJECT_DIR = "/Users/zyc/Downloads/Niigata_Research_Prep"
POINT_CLOUD_PATH = os.path.join(PROJECT_DIR, "01_Processed", "tree.ply")
RESULTS_DIR = os.path.join(PROJECT_DIR, "04_Results")
FIGURES_DIR = os.path.join(RESULTS_DIR, "figures")
TABLES_DIR = os.path.join(RESULTS_DIR, "tables")
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(TABLES_DIR, exist_ok=True)
POSITIONS_CSV = os.path.join(TABLES_DIR, "tree_positions.csv")
OVERLAY_IMG = os.path.join(FIGURES_DIR, "forest_pointcloud_cylinders.png")
SPATIAL_IMG = os.path.join(FIGURES_DIR, "tree_spatial_distribution.png")

# Parameters
DBSCAN_EPS = 0.35        # meters
DBSCAN_MIN_POINTS = 40
BASE_SLICE_THICKNESS = 0.35  # meters
MAX_SLENDERNESS = 120
TARGET_SLENDERNESS = 90
TOP_N_TREES = 61

# Biomass parameters (same as analysis script)
WOOD_DENSITY = 0.45
BIOMASS_A = -2.5
BIOMASS_B = 2.134
BIOMASS_C = 0.683
CARBON_FRACTION = 0.47


def load_point_cloud():
    if not os.path.exists(POINT_CLOUD_PATH):
        raise FileNotFoundError(f"Point cloud not found: {POINT_CLOUD_PATH}")
    pcd = o3d.io.read_point_cloud(POINT_CLOUD_PATH)
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
        if radius_m < 0.005:  # skip unrealistic
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
    df = pd.DataFrame(trees).sort_values(by="diameter_cm", ascending=False)
    return df

def render_overlay_matplotlib(pcd, df):
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

    cmap = cm.get_cmap("viridis")
    h_min, h_max = df["height_m"].min(), df["height_m"].max()

    theta = np.linspace(0, 2 * np.pi, 24)
    for _, row in df.iterrows():
        color_val = (row.height_m - h_min) / max(h_max - h_min, 1e-6)
        color = cmap(color_val)
        circle = np.stack([
            row.radius_m * np.cos(theta) + row.x,
            row.radius_m * np.sin(theta) + row.y
        ], axis=1)
        z_bottom = row.base_z
        z_top = row.base_z + row.height_m

        # side faces
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

        # top/bottom disks
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
    plt.savefig(OVERLAY_IMG, dpi=300)
    plt.close()
    print(f"3D overlay saved to {OVERLAY_IMG}")

def plot_spatial_map(df):
    print("Plotting spatial distribution...")
    plt.figure(figsize=(8, 8))
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
    plt.xlabel("X (m)")
    plt.ylabel("Y (m)")
    plt.title("Tree Spatial Distribution\nMarker size = DBH, color = height")
    plt.axis("equal")
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()
    plt.savefig(SPATIAL_IMG, dpi=300)
    plt.close()
    print(f"Spatial map saved to {SPATIAL_IMG}")

def main():
    pcd = load_point_cloud()
    labels, clusters = cluster_points(pcd)
    df = compute_tree_stats(pcd, labels, clusters)
    if TOP_N_TREES and len(df) > TOP_N_TREES:
        df = df.sort_values(by="diameter_cm", ascending=False).head(TOP_N_TREES)
    df["generated_at"] = datetime.now().isoformat()
    df.to_csv(POSITIONS_CSV, index=False, float_format="%.4f")
    print(f"Tree positions saved to {POSITIONS_CSV} (n={len(df)})")
    render_overlay_matplotlib(pcd, df)
    plot_spatial_map(df)

if __name__ == "__main__":
    main()
