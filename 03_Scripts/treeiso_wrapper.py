"""
Treeiso Python 版本使用封装
基于 https://github.com/artemislab/treeiso

需要先安装：
  git clone https://github.com/artemislab/treeiso.git
  cd treeiso/PythonCPP && pip install -r requirements.txt

本脚本提供与项目集成的便捷接口
"""

import subprocess
import os
import sys


def check_treeiso_installed():
    """检查 Treeiso 是否已安装"""
    treeiso_path = os.path.expanduser("~/treeiso")
    if os.path.exists(treeiso_path):
        return treeiso_path
    
    # 检查其他常见位置
    alt_paths = [
        "/Users/zyc/treeiso",
        "/opt/treeiso",
        os.path.expanduser("~/Documents/treeiso")
    ]
    for path in alt_paths:
        if os.path.exists(path):
            return path
    
    return None


def install_treeiso():
    """安装 Treeiso"""
    print("=" * 60)
    print("Treeiso 安装指南")
    print("=" * 60)
    print("""
Treeiso 需要手动安装。请执行以下命令：

# 1. 克隆仓库
cd ~
git clone https://github.com/artemislab/treeiso.git

# 2. 安装依赖
cd treeiso/PythonCPP
pip install -r requirements.txt

# 3. 测试运行
python treeiso.py --help

安装完成后重新运行此脚本。
""")
    return False


def run_treeiso(input_las, output_dir=None):
    """
    运行 Treeiso 处理点云
    
    Args:
        input_las: 输入 LAS/LAZ 文件路径
        output_dir: 输出目录（可选）
    
    Returns:
        输出文件路径
    """
    treeiso_path = check_treeiso_installed()
    
    if not treeiso_path:
        install_treeiso()
        return None
    
    script_path = os.path.join(treeiso_path, "PythonCPP", "treeiso.py")
    
    if not os.path.exists(script_path):
        print(f"错误: 找不到 treeiso.py: {script_path}")
        return None
    
    print(f"运行 Treeiso: {input_las}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path, input_las],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(input_las)
        )
        
        if result.returncode == 0:
            print("Treeiso 处理完成！")
            print(result.stdout)
            
            # 查找输出文件
            base_name = os.path.splitext(input_las)[0]
            output_file = f"{base_name}_treeiso.laz"
            
            if os.path.exists(output_file):
                return output_file
        else:
            print(f"Treeiso 运行出错:")
            print(result.stderr)
            
    except Exception as e:
        print(f"运行 Treeiso 失败: {e}")
    
    return None


def convert_ply_to_las(input_ply, output_las):
    """
    将 PLY 转换为 LAS（Treeiso 需要 LAS 格式）
    需要安装 pdal 或使用 CloudCompare
    """
    print(f"转换 PLY -> LAS: {input_ply}")
    
    # 方法1: 使用 pdal（如果已安装）
    try:
        import pdal
        pipeline = f"""
        {{
            "pipeline": [
                "{input_ply}",
                {{
                    "type": "writers.las",
                    "filename": "{output_las}"
                }}
            ]
        }}
        """
        p = pdal.Pipeline(pipeline)
        p.execute()
        print(f"转换完成: {output_las}")
        return output_las
    except ImportError:
        pass
    
    # 方法2: 使用 laspy + open3d
    try:
        import open3d as o3d
        import laspy
        import numpy as np
        
        pcd = o3d.io.read_point_cloud(input_ply)
        points = np.asarray(pcd.points)
        
        las = laspy.create(point_format=0, file_version="1.2")
        las.x = points[:, 0]
        las.y = points[:, 1]
        las.z = points[:, 2]
        las.write(output_las)
        
        print(f"转换完成: {output_las}")
        return output_las
    except ImportError:
        print("需要安装 laspy: pip install laspy")
    
    # 方法3: 提示使用 CloudCompare
    print("""
无法自动转换格式。请使用 CloudCompare 手动转换：

1. 打开 CloudCompare
2. File > Open > 选择 PLY 文件
3. File > Save As > 选择 LAS 格式
""")
    return None


if __name__ == "__main__":
    # 检查安装状态
    treeiso_path = check_treeiso_installed()
    
    if treeiso_path:
        print(f"✅ Treeiso 已安装: {treeiso_path}")
        print("\n使用示例:")
        print("  from treeiso_wrapper import run_treeiso")
        print('  run_treeiso("path/to/pointcloud.las")')
    else:
        install_treeiso()
