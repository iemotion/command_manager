#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库备份脚本
用于备份命令管理工具的数据
"""

import sqlite3
import os
import shutil
from datetime import datetime
import json

def backup_database():
    """备份数据库"""
    db_file = "command_manager.db"

    if not os.path.exists(db_file):
        print("数据库文件不存在，无需备份")
        return False

    # 创建备份目录
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # 生成备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/command_manager_backup_{timestamp}.db"

    try:
        # 复制数据库文件
        shutil.copy2(db_file, backup_file)
        print(f"数据库已备份到: {backup_file}")

        # 创建备份信息文件
        backup_info = {
            "backup_time": timestamp,
            "original_file": db_file,
            "backup_file": backup_file,
            "file_size": os.path.getsize(backup_file)
        }

        info_file = f"{backup_dir}/backup_info_{timestamp}.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(backup_info, f, indent=2, ensure_ascii=False)

        print(f"备份信息已保存到: {info_file}")
        return True

    except Exception as e:
        print(f"备份失败: {e}")
        return False

def list_backups():
    """列出所有备份文件"""
    backup_dir = "backups"

    if not os.path.exists(backup_dir):
        print("没有找到备份目录")
        return

    backups = []
    for file in os.listdir(backup_dir):
        if file.startswith("command_manager_backup_") and file.endswith(".db"):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backups.append((file, file_time, file_size))

    if not backups:
        print("没有找到备份文件")
        return

    print("现有的备份文件:")
    print("-" * 80)
    print(f"{'文件名':<40} {'备份时间':<20} {'文件大小':<15}")
    print("-" * 80)

    backups.sort(key=lambda x: x[1], reverse=True)
    for file, time, size in backups:
        size_str = f"{size/1024:.1f} KB"
        print(f"{file:<40} {time.strftime('%Y-%m-%d %H:%M:%S'):<20} {size_str:<15}")

def restore_from_backup(backup_file):
    """从备份恢复数据库"""
    if not os.path.exists(backup_file):
        print(f"备份文件不存在: {backup_file}")
        return False

    db_file = "command_manager.db"

    # 备份当前数据库
    if os.path.exists(db_file):
        current_backup = f"{db_file}.auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_file, current_backup)
        print(f"当前数据库已备份为: {current_backup}")

    try:
        shutil.copy2(backup_file, db_file)
        print(f"数据库已从备份恢复: {backup_file}")
        return True
    except Exception as e:
        print(f"恢复失败: {e}")
        return False

def main():
    """主函数"""
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python backup.py backup     # 备份数据库")
        print("  python backup.py list       # 列出备份文件")
        print("  python backup.py restore <备份文件>  # 从备份恢复")
        return

    command = sys.argv[1]

    if command == "backup":
        backup_database()
    elif command == "list":
        list_backups()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("请指定备份文件")
            return
        restore_from_backup(sys.argv[2])
    else:
        print("未知命令")

if __name__ == "__main__":
    main()