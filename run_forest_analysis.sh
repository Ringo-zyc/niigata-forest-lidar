#!/bin/bash
# 森林数据清洗和分析主脚本

PROJECT_DIR="/Users/zyc/Downloads/Niigata_Research_Prep"
ENV_NAME="tree_detection"

cd "$PROJECT_DIR"

echo "=================================================="
echo "    森林数据清洗与林业分析"
echo "    Forest Data Cleaning & Analysis"
echo "=================================================="
echo ""

# 初始化 conda
eval "$(conda shell.bash hook)"

# 激活环境
conda activate "$ENV_NAME"

# 安装 matplotlib 和 pandas（如果还没安装）
echo "正在检查依赖..."
pip install -q matplotlib pandas 2>/dev/null || echo "依赖已安装"

# 运行分析
echo ""
python "$PROJECT_DIR/03_Scripts/analyze_forest_data.py"

# 停用环境
conda deactivate

echo ""
echo "=================================================="
echo "分析完成！请查看 04_Results/ 目录"
echo "=================================================="
