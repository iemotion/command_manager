#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命令管理工具启动器
脱离命令框运行的独立应用程序
"""

import sys
import os
import subprocess
import platform

def get_script_path():
    """获取脚本路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的可执行文件
        return os.path.dirname(sys.executable)
    else:
        # 如果是源码运行
        return os.path.dirname(os.path.abspath(__file__))

def main():
    """主函数"""
    try:
        # 设置工作目录
        script_dir = get_script_path()
        os.chdir(script_dir)

        # 添加src目录到Python路径
        src_dir = os.path.join(script_dir, 'src')
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        # 导入并运行主程序
        from command_manager import CommandManager
        import tkinter as tk

        root = tk.Tk()
        app = CommandManager(root)
        root.mainloop()

    except Exception as e:
        # 错误处理
        if platform.system() == 'Windows':
            # Windows下使用消息框显示错误
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, f"程序启动失败：\n{str(e)}", "错误", 0)
        else:
            # 其他系统使用控制台输出
            print(f"程序启动失败：{e}")
            input("按回车键退出...")

if __name__ == "__main__":
    main()