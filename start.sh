#!/bin/bash

# 命令管理工具启动脚本 (macOS/Linux)

echo "======================================"
echo "     命令管理工具 v1.0.1"
echo "======================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.6或更高版本"
    echo
    echo "安装方法："
    echo "macOS: brew install python3"
    echo "Ubuntu: sudo apt-get install python3"
    echo "CentOS: sudo yum install python3"
    echo "或访问: https://www.python.org/downloads/"
    echo
    read -p "按回车键退出..."
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PYTHON_VERSION=$(python3 --version 2>&1)
else
    PYTHON_CMD="python"
    PYTHON_VERSION=$(python --version 2>&1)
fi

echo "[✓] Python已安装: $PYTHON_VERSION"

# 检查tkinter是否可用
echo "正在检查tkinter模块..."
$PYTHON_CMD -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[错误] tkinter模块不可用"
    echo
    echo "解决方案："
    echo "Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "CentOS/RHEL: sudo yum install tkinter"
    echo "macOS: 通常已包含，如需重新安装: brew install python-tk"
    echo
    read -p "按回车键退出..."
    exit 1
fi

echo "[✓] tkinter模块可用"

# 检查主程序文件是否存在
if [ ! -f "launcher.py" ]; then
    echo "[错误] 未找到launcher.py文件"
    echo "请确保在正确的目录中运行此脚本"
    echo
    read -p "按回车键退出..."
    exit 1
fi

echo "[✓] 程序文件检查完成"
echo
echo "正在启动命令管理工具..."
echo

# 启动程序
$PYTHON_CMD launcher.py

# 检查程序退出状态
if [ $? -ne 0 ]; then
    echo
    echo "[错误] 程序启动失败或异常退出"
    echo "请检查上面的错误信息"
    echo
    read -p "按回车键退出..."
    exit 1
else
    echo
    echo "程序已正常退出"
fi