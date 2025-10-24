#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建独立应用程序脚本
不依赖PyInstaller，创建可独立运行的脚本包
包含Windows bat文件支持
"""

import os
import shutil
import zipfile
import sys
from pathlib import Path

def create_portable_package():
    """创建便携式应用程序包"""
    print("正在创建便携式应用程序包...")

    # 创建输出目录
    output_dir = Path("CommandManager_Portable")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()

    # 复制必要文件
    files_to_copy = [
        "launcher.py",
        "src/",
        "assets/",
        "docs/",
        "requirements.txt",
        "README.md",
    ]

    # 添加bat文件（如果存在）
    bat_files = ["启动命令管理工具.bat", "快速启动.bat"]
    for bat_file in bat_files:
        if Path(bat_file).exists():
            files_to_copy.append(bat_file)

    # 添加sh文件（如果存在）
    sh_files = ["start.sh", "quick_start.sh"]
    for sh_file in sh_files:
        if Path(sh_file).exists():
            files_to_copy.append(sh_file)

    for item in files_to_copy:
        src = Path(item)
        dst = output_dir / item

        if src.is_file():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"复制文件: {src} -> {dst}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"复制目录: {src} -> {dst}")

    # 创建启动脚本
    if sys.platform == "win32":
        # Windows环境下创建额外的bat文件（如果原文件不存在）
        if not Path("启动命令管理工具.bat").exists():
            start_script = output_dir / "启动命令管理工具.bat"
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write('''@echo off
chcp 65001 >nul
title 命令管理工具

echo ===================================
echo     命令管理工具 v1.0.0
echo ===================================
echo.

echo 正在检查Python环境...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.6或更高版本
    echo.
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [✓] Python已安装

REM 检查tkinter是否可用
echo 正在检查tkinter模块...
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [错误] tkinter模块不可用
    echo.
    pause
    exit /b 1
)

echo [✓] tkinter模块可用
echo.
echo 正在启动命令管理工具...
echo.

REM 启动程序
python launcher.py

if errorlevel 1 (
    echo.
    echo [错误] 程序启动失败
    pause
    exit /b 1
)
''')
            print(f"创建Windows启动脚本: {start_script}")

        if not Path("快速启动.bat").exists():
            quick_script = output_dir / "快速启动.bat"
            with open(quick_script, 'w', encoding='utf-8') as f:
                f.write('''@echo off
python launcher.py
pause
''')
            print(f"创建Windows快速启动脚本: {quick_script}")

    else:
        # Unix/Linux/macOS shell脚本
        start_script = output_dir / "start.sh"
        with open(start_script, 'w', encoding='utf-8') as f:
            f.write('''#!/bin/bash

echo "正在启动命令管理工具..."

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "错误: 未找到Python，请先安装Python 3.6或更高版本"
    echo "下载地址: https://www.python.org/downloads/"
    read -p "按回车键退出..."
    exit 1
fi

# 确定Python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

# 检查tkinter是否可用
$PYTHON_CMD -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "错误: tkinter模块不可用，请确保Python安装了tkinter支持"
    read -p "按回车键退出..."
    exit 1
fi

# 启动程序
$PYTHON_CMD launcher.py

if [ $? -ne 0 ]; then
    echo "程序启动失败，请检查错误信息"
    read -p "按回车键退出..."
fi
''')
        start_script.chmod(0o755)
        print(f"创建Unix启动脚本: {start_script}")

    # 创建安装说明
    install_guide = output_dir / "安装使用说明.txt"
    with open(install_guide, 'w', encoding='utf-8') as f:
        f.write('''命令管理工具 - 便携版
===================

系统要求：
- Python 3.6 或更高版本
- tkinter支持（通常Python自带）
- 操作系统：Windows / macOS / Linux

使用方法：

Windows用户：
1. 双击 "启动命令管理工具.bat" 运行程序（推荐）
2. 或双击 "快速启动.bat" 快速启动
3. 或者在命令行中运行：python launcher.py

macOS/Linux用户：
1. 在终端中运行：./start.sh
2. 或者直接运行：python3 launcher.py
3. 如果没有执行权限，先运行：chmod +x start.sh

注意事项：
1. 首次运行会自动创建data目录和数据库文件
2. 所有数据都保存在data目录中
3. 可以通过 "python src/backup.py backup" 备份数据
4. 详细文档请查看 docs/README.md

如果遇到问题：
1. 确认Python版本：python --version 或 python3 --version
2. 确认tkinter可用：python -c "import tkinter"
3. 查看错误信息并按照提示操作

祝您使用愉快！
''')
    print(f"创建安装说明: {install_guide}")

    # 创建版本信息
    version_info = output_dir / "version.txt"
    with open(version_info, 'w', encoding='utf-8') as f:
        f.write(f'''命令管理工具 v1.0.0
构建时间: {os.popen("date").read().strip()}
Python版本: {sys.version}
平台: {sys.platform}
''')
    print(f"创建版本信息: {version_info}")

    print(f"\n✅ 便携式应用程序包创建完成！")
    print(f"📁 输出目录: {output_dir.absolute()}")
    print(f"🚀 运行方法:")
    if sys.platform == "win32":
        print(f"   Windows: 双击 '启动命令管理工具.bat'")
        print(f"   Windows快速: 双击 '快速启动.bat'")
    else:
        print(f"   Unix/macOS: 运行 './start.sh'")
    print(f"   通用: python launcher.py")

    return output_dir

def create_zip_package():
    """创建ZIP压缩包"""
    print("正在创建ZIP压缩包...")

    portable_dir = create_portable_package()

    zip_name = "CommandManager_v1.0.0_Portable.zip"
    zip_path = Path(zip_name)

    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in portable_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(portable_dir.parent)
                zipf.write(file_path, arcname)

    print(f"✅ ZIP压缩包创建完成: {zip_path}")
    print(f"📦 大小: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")

    return zip_path

def main():
    """主函数"""
    print("命令管理工具 - 便携版打包工具")
    print("=" * 40)

    if len(sys.argv) > 1 and sys.argv[1] == "zip":
        # 创建ZIP压缩包
        create_zip_package()
    else:
        # 只创建便携式目录
        create_portable_package()

    print("\n打包完成！您可以：")
    print("1. 直接使用便携式目录")
    print("2. 运行 'python make_standalone_fixed.py zip' 创建ZIP压缩包")
    print("3. 将整个目录复制到其他设备使用")

if __name__ == "__main__":
    main()