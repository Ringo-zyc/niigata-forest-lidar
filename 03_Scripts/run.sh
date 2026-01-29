#!/bin/bash
# 🌲 LiDAR Tree Detection Unified Runner 🌲
# Usage: ./run.sh [command]
# Commands:
#   gui       - Launch GUI (default)
#   detect    - Run CLI detection
#   visualize - Run visualization
#   help      - Show help

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# --- 1. Environment Setup ---
# Check for .venv or conda

PYTHON_CMD=""

# Try .venv first
if [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/.venv/bin/python"
elif [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON_CMD="$PROJECT_DIR/venv/bin/python"
# Try conda
elif command -v conda &> /dev/null; then
    # Helper to check if env exists
    if conda env list | grep -q "tree_detection"; then
         # We can't easily activate conda in script without init, 
         # so specific python path is safer or using 'conda run'
         # Trying to find python path for conda env
         CONDA_ENV_PATH=$(conda env list | grep "tree_detection" | awk '{print $NF}')
         if [ -n "$CONDA_ENV_PATH" ] && [ -f "$CONDA_ENV_PATH/bin/python" ]; then
             PYTHON_CMD="$CONDA_ENV_PATH/bin/python"
         fi
    fi
fi

# Fallback to system python if it has requirements (simple check)
if [ -z "$PYTHON_CMD" ]; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        PYTHON_CMD="python"
    fi
fi

echo "🔧 Using Python: $PYTHON_CMD"

# --- 2. Dependencies Check (Simple) ---
# We assume if environment is found, dependencies are likely there.
# You could add a 'install' command here.

# --- 3. Command Handling ---
MODE="${1:-gui}"

case "$MODE" in
    gui)
        echo "🚀 Starting GUI..."
        "$PYTHON_CMD" "$SCRIPT_DIR/gui_app.py"
        ;;
    detect)
        echo "🔍 Starting CLI Detection..."
        "$PYTHON_CMD" "$SCRIPT_DIR/detect_cylinders_v2.py" "$2"
        ;;
    visualize)
        echo "📊 Starting Visualization..."
        "$PYTHON_CMD" "$SCRIPT_DIR/visualize_forest.py" "$2"
        ;;
    help|--help|-h)
        echo "Usage: ./run.sh [command]"
        echo ""
        echo "Commands:"
        echo "  gui       : Launch the GUI application (default)"
        echo "  detect    : Run the command-line detection script"
        echo "  visualize : Run the visualization script"
        echo "  help      : Show this help message"
        ;;
    *)
        echo "❌ Unknown command: $MODE"
        echo "Run './run.sh help' for usage."
        exit 1
        ;;
esac
