#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图形化命令管理工具
功能：
1. 命令分类管理
2. 命令增删改查
3. 命令收藏
4. IP和端口管理
5. 命令生成
6. 笔记管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime
import sqlite3
import re

class ColumnWidthManager:
    """列宽度管理器"""
    def __init__(self, config_file="column_widths.json"):
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', config_file)
        self.widths = {}
        self.load_widths()

    def load_widths(self):
        """加载列宽度配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.widths = json.load(f)
        except Exception as e:
            print(f"加载列宽度配置失败: {e}")
            self.widths = {}

    def save_widths(self):
        """保存列宽度配置"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.widths, f, indent=2)
        except Exception as e:
            print(f"保存列宽度配置失败: {e}")

    def get_width(self, tree_id, column, default_width):
        """获取列宽度"""
        key = f"{tree_id}_{column}"
        return self.widths.get(key, default_width)

    def set_width(self, tree_id, column, width):
        """设置列宽度"""
        key = f"{tree_id}_{column}"
        self.widths[key] = width
        self.save_widths()

class CommandManager:
    def __init__(self, root):
        self.root = root
        self.root.title("命令管理工具")
        self.root.geometry("1200x800")

        # 居中显示窗口
        self.center_window()

        # 初始化列宽度管理器
        self.column_manager = ColumnWidthManager()

        # 数据库初始化
        self.init_database()

        # 创建主界面
        self.create_main_interface()

        # 加载数据
        self.load_data()

    def center_window(self):
        """将窗口居中显示"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建左侧面板
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        # 功能选择按钮
        ttk.Label(left_frame, text="功能模块", font=("Arial", 12, "bold")).pack(pady=10)

        ttk.Button(left_frame, text="命令管理", command=self.show_command_management, width=20).pack(pady=5)
        ttk.Button(left_frame, text="分类管理", command=self.show_category_management, width=20).pack(pady=5)
        ttk.Button(left_frame, text="笔记管理", command=self.show_note_management, width=20).pack(pady=5)
      
        # 分隔线
        ttk.Separator(left_frame, orient='horizontal').pack(fill=tk.X, pady=20)

        # 快速搜索
        ttk.Label(left_frame, text="快速搜索", font=("Arial", 10, "bold")).pack(pady=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.quick_search)
        search_entry = ttk.Entry(left_frame, textvariable=self.search_var, width=25)
        search_entry.pack(pady=5)

        # 创建右侧内容区域
        right_container = ttk.Frame(main_frame)
        right_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建顶部栏（包含作者图标）
        top_bar = ttk.Frame(right_container)
        top_bar.pack(fill=tk.X, pady=(0, 10))

        # 左侧标题
        title_label = ttk.Label(top_bar, text="命令管理工具", font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=10, pady=5)

        # 右侧作者图标
        author_button = ttk.Button(top_bar, text="ℹ️", width=3,
                                  command=self.show_author_info)
        author_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # 创建内容区域
        self.content_frame = ttk.Frame(right_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # 默认显示命令管理界面
        self.show_command_management()

    def load_data(self):
        """加载数据"""
        self.load_categories()
        self.load_commands()
        self.load_notes()

    def init_database(self):
        """初始化数据库"""
        # 数据库文件路径
        db_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)

        db_path = os.path.join(db_dir, 'command_manager.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

        # 创建分类表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 创建命令表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                command TEXT NOT NULL,
                category_id INTEGER,
                description TEXT,
                is_favorite INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')

        
        # 创建笔记表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

        # 插入默认分类
        default_categories = [
            ('系统命令', '系统管理相关命令'),
            ('网络命令', '网络诊断和配置命令'),
            ('开发工具', '开发和编译相关命令'),
            ('数据库', '数据库操作命令'),
            ('其他', '其他类别命令')
        ]

        for cat in default_categories:
            self.cursor.execute('INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)', cat)

        self.conn.commit()

    def show_command_management(self):
        """显示命令管理界面"""
        self.clear_content_frame()

        # 创建命令管理界面
        cmd_frame = ttk.Frame(self.content_frame)
        cmd_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部工具栏
        toolbar = ttk.Frame(cmd_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="添加命令", command=self.add_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑命令", command=self.edit_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除命令", command=self.delete_command).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="收藏/取消收藏", command=self.toggle_favorite).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="复制命令", command=self.copy_command).pack(side=tk.LEFT, padx=5)

        # 分类过滤
        ttk.Label(toolbar, text="分类:").pack(side=tk.LEFT, padx=(20, 5))
        self.category_filter = ttk.Combobox(toolbar, width=15, state="readonly")
        self.category_filter.pack(side=tk.LEFT, padx=5)
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_commands)
        self.update_category_filter()

        # 收藏过滤
        self.favorite_only = tk.BooleanVar()
        ttk.Checkbutton(toolbar, text="仅显示收藏", variable=self.favorite_only,
                       command=self.filter_commands).pack(side=tk.LEFT, padx=10)

        # 命令列表
        list_frame = ttk.Frame(cmd_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview
        columns = ('名称', '命令', '分类', '收藏')
        self.command_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        for col in columns:
            self.command_tree.heading(col, text=col)
            # 从配置中获取保存的列宽度，使用默认值作为后备
            if col == '命令':
                width = self.column_manager.get_width('command_tree', col, 400)
                self.command_tree.column(col, width=width, minwidth=200)
            elif col == '名称':
                width = self.column_manager.get_width('command_tree', col, 150)
                self.command_tree.column(col, width=width, minwidth=100)
            elif col == '分类':
                width = self.column_manager.get_width('command_tree', col, 120)
                self.command_tree.column(col, width=width, minwidth=80)
            else:  # 收藏
                width = self.column_manager.get_width('command_tree', col, 60)
                self.command_tree.column(col, width=width, minwidth=50)

        # 绑定列宽度变化事件
        self.command_tree.bind('<Configure>', self.on_column_resize)

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.command_tree.yview)
        self.command_tree.configure(yscrollcommand=scrollbar.set)

        self.command_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 双击执行命令
        self.command_tree.bind('<Double-1>', self.execute_command)

        # 刷新命令列表
        self.refresh_command_list()

    def on_column_resize(self, event):
        """处理列宽度变化事件"""
        # 获取当前列宽度并保存
        try:
            for col in self.command_tree['columns']:
                width = self.command_tree.column(col, 'width')
                self.column_manager.set_width('command_tree', col, width)
        except Exception as e:
            print(f"保存列宽度失败: {e}")

    def show_category_management(self):
        """显示分类管理界面"""
        self.clear_content_frame()

        cat_frame = ttk.Frame(self.content_frame)
        cat_frame.pack(fill=tk.BOTH, expand=True)

        # 工具栏
        toolbar = ttk.Frame(cat_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="添加分类", command=self.add_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="编辑分类", command=self.edit_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除分类", command=self.delete_category).pack(side=tk.LEFT, padx=5)

        # 分类列表
        list_frame = ttk.Frame(cat_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('分类名称', '描述', '创建时间')
        self.category_tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        for col in columns:
            self.category_tree.heading(col, text=col)
            self.category_tree.column(col, width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.category_tree.yview)
        self.category_tree.configure(yscrollcommand=scrollbar.set)

        self.category_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_category_list()

    def show_note_management(self):
        """显示笔记管理界面"""
        self.clear_content_frame()

        note_frame = ttk.Frame(self.content_frame)
        note_frame.pack(fill=tk.BOTH, expand=True)

        # 工具栏
        toolbar = ttk.Frame(note_frame)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(toolbar, text="添加笔记", command=self.add_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="修改笔记", command=self.edit_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="删除笔记", command=self.delete_note).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="复制笔记", command=self.copy_note).pack(side=tk.LEFT, padx=5)

        # 分类过滤
        ttk.Label(toolbar, text="分类:").pack(side=tk.LEFT, padx=(20, 5))
        self.note_category_filter = ttk.Entry(toolbar, width=15)
        self.note_category_filter.pack(side=tk.LEFT, padx=5)
        self.note_category_filter.bind('<KeyRelease>', self.filter_notes)

        # 分割面板
        paned = ttk.PanedWindow(note_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # 左侧笔记列表
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)

        columns = ('标题', '分类', '创建时间')
        self.note_tree = ttk.Treeview(left_frame, columns=columns, show='headings')

        for col in columns:
            self.note_tree.heading(col, text=col)
            if col == '标题':
                self.note_tree.column(col, width=200)
            else:
                self.note_tree.column(col, width=100)

        note_scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.note_tree.yview)
        self.note_tree.configure(yscrollcommand=note_scrollbar.set)

        self.note_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        note_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧笔记内容
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)

        ttk.Label(right_frame, text="笔记内容:").pack(anchor=tk.W, padx=5, pady=5)
        self.note_content = tk.Text(right_frame, wrap=tk.WORD, state=tk.DISABLED)  # 设置为只读模式
        content_scrollbar = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.note_content.yview)
        self.note_content.configure(yscrollcommand=content_scrollbar.set)

        self.note_content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定选择事件
        self.note_tree.bind('<<TreeviewSelect>>', self.on_note_select)

        self.refresh_note_list()

    def show_author_info(self):
        """显示作者信息对话框"""
        try:
            # 读取作者信息
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'author_info.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    author_info = json.load(f)
            else:
                # 默认信息
                author_info = {
                    "name": "命令管理工具",
                    "version": "1.1.1",
                    "author": "开发者",
                    "github_url": "https://github.com/yourusername/command-manager",
                    "description": "一个功能完整的图形化命令管理工具",
                    "build_date": "2024-10-24"
                }
        except Exception as e:
            print(f"读取作者信息失败: {e}")
            author_info = {"author": "开发者", "github_url": "#"}

        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("关于")
        dialog.geometry("400x300")
        dialog.resizable(False, False)

        # 使对话框居中
        dialog.transient(self.root)
        dialog.grab_set()

        # 内容框架
        content_frame = ttk.Frame(dialog, padding="20")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # 应用图标和名称
        title_frame = ttk.Frame(content_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))

        app_label = ttk.Label(title_frame, text="📱", font=("Arial", 24))
        app_label.pack(side=tk.LEFT, padx=(0, 10))

        name_label = ttk.Label(title_frame, text=author_info.get("name", "命令管理工具"),
                               font=("Arial", 16, "bold"))
        name_label.pack(side=tk.LEFT, padx=(0, 10))

        version_label = ttk.Label(title_frame, text=f"v{author_info.get('version', '1.0.0')}",
                                 font=("Arial", 12))
        version_label.pack(side=tk.LEFT)

        # 描述
        desc_text = author_info.get("description", "一个功能完整的图形化命令管理工具")
        desc_label = ttk.Label(content_frame, text=desc_text, font=("Arial", 10))
        desc_label.pack(anchor=tk.W, pady=(0, 15))

        # 分隔线
        ttk.Separator(content_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        # 作者信息
        info_frame = ttk.Frame(content_frame)
        info_frame.pack(fill=tk.X, pady=10)

        author_label = ttk.Label(info_frame, text=f"作者: {author_info.get('author', '开发者')}",
                                 font=("Arial", 11))
        author_label.pack(anchor=tk.W, pady=2)

        build_label = ttk.Label(info_frame, text=f"构建日期: {author_info.get('build_date', '2024-10-24')}",
                               font=("Arial", 10))
        build_label.pack(anchor=tk.W, pady=2)

        # GitHub链接
        github_url = author_info.get("github_url", "#")
        if github_url != "#":
            github_frame = ttk.Frame(content_frame)
            github_frame.pack(fill=tk.X, pady=10)

            github_label = ttk.Label(github_frame, text="GitHub:", font=("Arial", 10, "bold"))
            github_label.pack(side=tk.LEFT, padx=(0, 5))

            github_link = ttk.Label(github_frame, text=github_url,
                                    font=("Arial", 10), foreground="blue", cursor="hand2")
            github_link.pack(side=tk.LEFT)
            github_link.bind("<Button-1>", lambda e: self.open_url(github_url))

        # 按钮
        button_frame = ttk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        close_btn = ttk.Button(button_frame, text="关闭", command=dialog.destroy)
        close_btn.pack(side=tk.RIGHT)

    def open_url(self, url):
        """打开URL"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            print(f"无法打开链接: {e}")

    # 命令管理相关方法
    def add_command(self):
        """添加命令"""
        dialog = CommandDialog(self.root, "添加命令", self.get_categories())
        if dialog.result:
            name, command, category_id, description = dialog.result
            self.cursor.execute('''
                INSERT INTO commands (name, command, category_id, description)
                VALUES (?, ?, ?, ?)
            ''', (name, command, category_id, description))
            self.conn.commit()
            self.refresh_command_list()

    def edit_command(self):
        """编辑命令"""
        selection = self.command_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的命令")
            return

        item = self.command_tree.item(selection[0])
        values = item['values']

        # 获取命令ID
        command_id = self.get_command_id_by_name(values[0])
        if not command_id:
            return

        # 获取原始数据
        self.cursor.execute('SELECT * FROM commands WHERE id = ?', (command_id,))
        cmd_data = self.cursor.fetchone()

        dialog = CommandDialog(self.root, "编辑命令", self.get_categories(), cmd_data)
        if dialog.result:
            name, command, category_id, description = dialog.result
            self.cursor.execute('''
                UPDATE commands SET name = ?, command = ?, category_id = ?,
                description = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (name, command, category_id, description, command_id))
            self.conn.commit()
            self.refresh_command_list()

    def delete_command(self):
        """删除命令"""
        selection = self.command_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的命令")
            return

        if messagebox.askyesno("确认", "确定要删除选中的命令吗？"):
            item = self.command_tree.item(selection[0])
            values = item['values']
            command_id = self.get_command_id_by_name(values[0])

            if command_id:
                self.cursor.execute('DELETE FROM commands WHERE id = ?', (command_id,))
                self.conn.commit()
                self.refresh_command_list()

    def toggle_favorite(self):
        """切换收藏状态"""
        selection = self.command_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要操作的命令")
            return

        item = self.command_tree.item(selection[0])
        values = item['values']
        command_id = self.get_command_id_by_name(values[0])

        if command_id:
            # 获取当前收藏状态
            self.cursor.execute('SELECT is_favorite FROM commands WHERE id = ?', (command_id,))
            current_favorite = self.cursor.fetchone()[0]
            new_favorite = 1 if current_favorite == 0 else 0

            self.cursor.execute('UPDATE commands SET is_favorite = ? WHERE id = ?',
                              (new_favorite, command_id))
            self.conn.commit()
            self.refresh_command_list()

    def copy_command(self):
        """复制命令到剪贴板"""
        selection = self.command_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要复制的命令")
            return

        item = self.command_tree.item(selection[0])
        values = item['values']
        command_name = values[0]

        # 从数据库获取完整的命令内容
        self.cursor.execute('SELECT command FROM commands WHERE name = ?', (command_name,))
        result = self.cursor.fetchone()

        if result and result[0]:  # 完整的命令内容
            self.root.clipboard_clear()
            self.root.clipboard_append(result[0])
            self.status_var.set("命令已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "选中的命令没有内容")

    def copy_full_command(self, command_text):
        """复制完整命令到剪贴板"""
        self.root.clipboard_clear()
        self.root.clipboard_append(command_text)
        self.status_var.set("完整命令已复制到剪贴板")

    def execute_command(self, event):
        """执行命令（显示完整命令详情）"""
        selection = self.command_tree.selection()
        if not selection:
            return

        item = self.command_tree.item(selection[0])
        values = item['values']
        command_name = values[0]

        # 从数据库获取完整的命令内容
        self.cursor.execute('SELECT command, description FROM commands WHERE name = ?', (command_name,))
        result = self.cursor.fetchone()

        if result:
            full_command = result[0] or "无命令内容"
            description = result[1] or "无描述"
            category = values[2]

            # 显示完整命令详情
            command_info = f"命令名称: {command_name}\n分类: {category}\n描述: {description}\n\n完整命令:\n{full_command}"

            # 创建一个可复制的文本框显示命令
            dialog = tk.Toplevel(self.root)
            dialog.title("命令详情")
            dialog.geometry("600x400")
            dialog.resizable(True, True)

            # 使对话框居中
            dialog.transient(self.root)
            dialog.grab_set()

            # 创建文本框
            text_frame = ttk.Frame(dialog, padding="10")
            text_frame.pack(fill=tk.BOTH, expand=True)

            text_widget = tk.Text(text_frame, wrap=tk.WORD, height=15)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)

            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            text_widget.insert(tk.END, command_info)
            text_widget.config(state=tk.DISABLED)

            # 复制按钮
            copy_btn = ttk.Button(dialog, text="复制完整命令",
                                command=lambda: self.copy_full_command(full_command))
            copy_btn.pack(pady=5)

            # 关闭按钮
            close_btn = ttk.Button(dialog, text="关闭", command=dialog.destroy)
            close_btn.pack(pady=5)

    # 分类管理相关方法
    def add_category(self):
        """添加分类"""
        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加分类")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = {}

        # 创建表单
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 分类名称
        ttk.Label(frame, text="分类名称:").grid(row=0, column=0, sticky=tk.W, pady=8)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=8, padx=(10, 0))
        name_entry.focus_set()

        # 分类描述
        ttk.Label(frame, text="分类描述:").grid(row=1, column=0, sticky=tk.W, pady=8)
        desc_entry = ttk.Entry(frame, width=30)
        desc_entry.grid(row=1, column=1, sticky=tk.EW, pady=8, padx=(10, 0))

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        def ok_clicked():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("错误", "分类名称不能为空", parent=dialog)
                return

            result['name'] = name
            result['description'] = desc_entry.get().strip()
            dialog.destroy()

        def cancel_clicked():
            result.clear()
            dialog.destroy()

        ttk.Button(button_frame, text="确定", command=ok_clicked, width=12).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="取消", command=cancel_clicked, width=12).pack(side=tk.LEFT, padx=8)

        frame.columnconfigure(1, weight=1)

        # 绑定回车键
        dialog.bind('<Return>', lambda event: ok_clicked())
        dialog.bind('<Escape>', lambda event: cancel_clicked())

        # 等待对话框关闭
        dialog.wait_window()

        # 处理结果
        if result and 'name' in result:
            try:
                self.cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)',
                                  (result['name'], result['description']))
                self.conn.commit()
                self.refresh_category_list()
                self.update_category_filter()
                messagebox.showinfo("成功", f"分类 '{result['name']}' 添加成功")
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "分类名称已存在")

    def edit_category(self):
        """编辑分类"""
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的分类")
            return

        item = self.category_tree.item(selection[0])
        values = item['values']

        # 创建自定义对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("编辑分类")
        dialog.geometry("400x250")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        result = {}

        # 创建表单
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 分类名称
        ttk.Label(frame, text="分类名称:").grid(row=0, column=0, sticky=tk.W, pady=8)
        name_entry = ttk.Entry(frame, width=30)
        name_entry.grid(row=0, column=1, sticky=tk.EW, pady=8, padx=(10, 0))
        name_entry.insert(0, values[0])
        name_entry.focus_set()

        # 分类描述
        ttk.Label(frame, text="分类描述:").grid(row=1, column=0, sticky=tk.W, pady=8)
        desc_entry = ttk.Entry(frame, width=30)
        desc_entry.grid(row=1, column=1, sticky=tk.EW, pady=8, padx=(10, 0))
        if values[1]:
            desc_entry.insert(0, values[1])

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)

        def ok_clicked():
            new_name = name_entry.get().strip()
            if not new_name:
                messagebox.showerror("错误", "分类名称不能为空", parent=dialog)
                return

            result['name'] = new_name
            result['description'] = desc_entry.get().strip()
            dialog.destroy()

        def cancel_clicked():
            result.clear()
            dialog.destroy()

        ttk.Button(button_frame, text="确定", command=ok_clicked, width=12).pack(side=tk.LEFT, padx=8)
        ttk.Button(button_frame, text="取消", command=cancel_clicked, width=12).pack(side=tk.LEFT, padx=8)

        frame.columnconfigure(1, weight=1)

        # 绑定回车键
        dialog.bind('<Return>', lambda event: ok_clicked())
        dialog.bind('<Escape>', lambda event: cancel_clicked())

        # 等待对话框关闭
        dialog.wait_window()

        # 处理结果
        if result and 'name' in result:
            try:
                self.cursor.execute('UPDATE categories SET name = ?, description = ? WHERE name = ?',
                                  (result['name'], result['description'], values[0]))
                self.conn.commit()
                self.refresh_category_list()
                self.update_category_filter()
                messagebox.showinfo("成功", f"分类 '{result['name']}' 更新成功")
            except sqlite3.IntegrityError:
                messagebox.showerror("错误", "分类名称已存在")

    def delete_category(self):
        """删除分类"""
        selection = self.category_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的分类")
            return

        item = self.category_tree.item(selection[0])
        category_name = item['values'][0]

        # 检查是否有命令使用此分类
        self.cursor.execute('SELECT COUNT(*) FROM commands WHERE category_id = '
                          '(SELECT id FROM categories WHERE name = ?)', (category_name,))
        count = self.cursor.fetchone()[0]

        if count > 0:
            messagebox.showerror("错误", f"此分类下还有 {count} 个命令，无法删除")
            return

        if messagebox.askyesno("确认", f"确定要删除分类 '{category_name}' 吗？"):
            self.cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
            self.conn.commit()
            self.refresh_category_list()
            self.update_category_filter()
            messagebox.showinfo("成功", f"分类 '{category_name}' 删除成功")

    def add_note(self):
        """添加笔记"""
        dialog = NoteDialog(self.root, "添加笔记")
        if dialog.result:
            title, content, category = dialog.result
            self.cursor.execute('''
                INSERT INTO notes (title, content, category)
                VALUES (?, ?, ?)
            ''', (title, content, category))
            self.conn.commit()
            self.refresh_note_list()
            messagebox.showinfo("成功", f"笔记 '{title}' 添加成功")

    def edit_note(self):
        """编辑笔记"""
        selection = self.note_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要编辑的笔记")
            return

        item = self.note_tree.item(selection[0])
        title = item['values'][0]

        # 获取笔记数据
        self.cursor.execute('SELECT * FROM notes WHERE title = ?', (title,))
        note_data = self.cursor.fetchone()

        if note_data:
            dialog = NoteDialog(self.root, "编辑笔记", note_data)
            if dialog.result:
                title, content, category = dialog.result
                self.cursor.execute('''
                    UPDATE notes SET title = ?, content = ?, category = ?,
                    updated_at = CURRENT_TIMESTAMP WHERE id = ?
                ''', (title, content, category, note_data[0]))
                self.conn.commit()
                self.refresh_note_list()

    def delete_note(self):
        """删除笔记"""
        selection = self.note_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要删除的笔记")
            return

        if messagebox.askyesno("确认", "确定要删除选中的笔记吗？"):
            item = self.note_tree.item(selection[0])
            title = item['values'][0]

            self.cursor.execute('DELETE FROM notes WHERE title = ?', (title,))
            self.conn.commit()
            self.refresh_note_list()

    def on_note_select(self, event):
        """选择笔记时显示内容"""
        selection = self.note_tree.selection()
        if selection:
            item = self.note_tree.item(selection[0])
            title = item['values'][0]

            self.cursor.execute('SELECT content FROM notes WHERE title = ?', (title,))
            result = self.cursor.fetchone()

            if result:
                # 临时启用编辑模式以更新内容
                self.note_content.config(state=tk.NORMAL)
                self.note_content.delete(1.0, tk.END)
                self.note_content.insert(1.0, result[0])
                # 重新设置为只读模式
                self.note_content.config(state=tk.DISABLED)

    def copy_note(self):
        """复制笔记到剪贴板"""
        selection = self.note_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请选择要复制的笔记")
            return

        item = self.note_tree.item(selection[0])
        title = item['values'][0]

        self.cursor.execute('SELECT content FROM notes WHERE title = ?', (title,))
        result = self.cursor.fetchone()

        if result and result[0]:
            content = result[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", f"笔记 '{title}' 已复制到剪贴板")
        else:
            messagebox.showwarning("警告", "选中的笔记没有内容")

    # 辅助方法
    def clear_content_frame(self):
        """清空内容框架"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def load_categories(self):
        """加载分类数据"""
        self.cursor.execute('SELECT id, name FROM categories ORDER BY name')
        self.categories = dict(self.cursor.fetchall())

    def load_commands(self):
        """加载命令数据"""
        pass

    def load_notes(self):
        """加载笔记数据"""
        pass

    def get_categories(self):
        """获取分类列表"""
        self.cursor.execute('SELECT id, name FROM categories ORDER BY name')
        return self.cursor.fetchall()

    def get_command_id_by_name(self, name):
        """根据命令名获取ID"""
        self.cursor.execute('SELECT id FROM commands WHERE name = ?', (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def refresh_command_list(self):
        """刷新命令列表"""
        # 清空现有数据
        for item in self.command_tree.get_children():
            self.command_tree.delete(item)

        # 构建查询
        query = '''
            SELECT c.name, c.command, cat.name, c.description, c.is_favorite
            FROM commands c
            LEFT JOIN categories cat ON c.category_id = cat.id
        '''
        params = []

        conditions = []
        if self.favorite_only.get():
            conditions.append('c.is_favorite = 1')

        if hasattr(self, 'category_filter') and self.category_filter.get():
            category_name = self.category_filter.get()
            if category_name != '全部':
                conditions.append('cat.name = ?')
                params.append(category_name)

        if conditions:
            query += ' WHERE ' + ' AND '.join(conditions)

        query += ' ORDER BY c.is_favorite DESC, c.name'

        # 执行查询
        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            favorite = "是" if row[4] else "否"
            # 格式化命令为单行显示（处理换行符和过长命令）
            command_text = row[1]
            # 将多行命令替换为单行显示
            command_text = command_text.replace('\n', ' ').replace('\r', ' ')
            # 移除多余空格
            command_text = ' '.join(command_text.split())
            # 截断过长的命令
            if len(command_text) > 80:
                command_text = command_text[:77] + "..."
            self.command_tree.insert('', tk.END, values=(row[0], command_text, row[2] or "未分类", favorite))

    def refresh_category_list(self):
        """刷新分类列表"""
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)

        self.cursor.execute('SELECT name, description, created_at FROM categories ORDER BY name')
        for row in self.cursor.fetchall():
            self.category_tree.insert('', tk.END, values=row)

    def refresh_host_list(self):
        """刷新主机列表"""
        for item in self.host_tree.get_children():
            self.host_tree.delete(item)

        self.cursor.execute('SELECT name, ip, port, username, description FROM hosts ORDER BY name')
        for row in self.cursor.fetchall():
            self.host_tree.insert('', tk.END, values=row)

    def refresh_note_list(self):
        """刷新笔记列表"""
        for item in self.note_tree.get_children():
            self.note_tree.delete(item)

        query = 'SELECT title, category, created_at FROM notes'
        params = []

        if hasattr(self, 'note_category_filter'):
            filter_text = self.note_category_filter.get().strip()
            if filter_text:
                query += ' WHERE category LIKE ?'
                params.append(f'%{filter_text}%')

        query += ' ORDER BY created_at DESC'

        self.cursor.execute(query, params)
        for row in self.cursor.fetchall():
            self.note_tree.insert('', tk.END, values=row)

    def update_category_filter(self):
        """更新分类过滤器"""
        if hasattr(self, 'category_filter'):
            categories = ['全部'] + [name for _, name in self.get_categories()]
            self.category_filter['values'] = categories
            self.category_filter.set('全部')

    def update_host_combo(self):
        """更新主机下拉框"""
        if hasattr(self, 'host_combo'):
            hosts = []
            self.cursor.execute('SELECT ip, port, username FROM hosts ORDER BY name')
            for row in self.cursor.fetchall():
                host_str = f"{row[0]} - {row[1]}"
                if row[2]:
                    host_str += f" - {row[2]}"
                hosts.append(host_str)
            self.host_combo['values'] = hosts
            if hosts:
                self.host_combo.current(0)

    def filter_commands(self, event=None):
        """过滤命令"""
        self.refresh_command_list()

    def filter_notes(self, event=None):
        """过滤笔记"""
        self.refresh_note_list()

    def quick_search(self, *args):
        """快速搜索"""
        search_term = self.search_var.get().strip()

        # 清空现有数据
        for item in self.command_tree.get_children():
            self.command_tree.delete(item)

        if not search_term:
            # 如果搜索为空，恢复正常显示
            self.refresh_command_list()
            return

        # 搜索命令
        self.cursor.execute('''
            SELECT c.name, c.command, cat.name, c.is_favorite
            FROM commands c
            LEFT JOIN categories cat ON c.category_id = cat.id
            WHERE c.name LIKE ? OR c.command LIKE ? OR c.description LIKE ?
            ORDER BY c.is_favorite DESC, c.name
        ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

        results = self.cursor.fetchall()
        if results:
            for row in results:
                favorite = "是" if row[3] else "否"
                # 格式化命令为单行显示（处理换行符和过长命令）
                command_text = row[1]
                # 将多行命令替换为单行显示
                command_text = command_text.replace('\n', ' ').replace('\r', ' ')
                # 移除多余空格
                command_text = ' '.join(command_text.split())
                # 截断过长的命令
                if len(command_text) > 80:
                    command_text = command_text[:77] + "..."
                self.command_tree.insert('', tk.END, values=(row[0], command_text, row[2] or "未分类", favorite))
        else:
            # 显示无结果提示
            self.command_tree.insert('', tk.END, values=("无搜索结果", "请尝试其他关键词", "", ""))

    # show_search_results方法已删除，改为原地显示搜索结果

    def __del__(self):
        """析构函数，关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()


class CommandDialog:
    """命令编辑对话框"""
    def __init__(self, parent, title, categories, default_data=None):
        self.result = None
        self.categories = categories  # 保存分类数据

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x450")  # 增加窗口大小
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)  # 允许调整大小

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # 创建表单
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 命令名称
        ttk.Label(frame, text="命令名称:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.name_entry = ttk.Entry(frame, width=50)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=8, padx=(10, 0))

        # 命令内容
        ttk.Label(frame, text="命令内容:").grid(row=1, column=0, sticky=tk.NW, pady=8)
        command_frame = ttk.Frame(frame)
        command_frame.grid(row=1, column=1, sticky=tk.EW, pady=8, padx=(10, 0))

        self.command_text = tk.Text(command_frame, width=50, height=10, wrap=tk.WORD)
        command_scrollbar = ttk.Scrollbar(command_frame, orient="vertical", command=self.command_text.yview)
        self.command_text.configure(yscrollcommand=command_scrollbar.set)

        self.command_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        command_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 分类
        ttk.Label(frame, text="分类:").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.category_combo = ttk.Combobox(frame, width=47, state="readonly")
        self.category_combo['values'] = [''] + [cat[1] for cat in categories]
        self.category_combo.grid(row=2, column=1, sticky=tk.EW, pady=8, padx=(10, 0))

        # 描述
        ttk.Label(frame, text="描述:").grid(row=3, column=0, sticky=tk.NW, pady=8)
        desc_frame = ttk.Frame(frame)
        desc_frame.grid(row=3, column=1, sticky=tk.EW, pady=8, padx=(10, 0))

        self.desc_text = tk.Text(desc_frame, width=50, height=6, wrap=tk.WORD)
        desc_scrollbar = ttk.Scrollbar(desc_frame, orient="vertical", command=self.desc_text.yview)
        self.desc_text.configure(yscrollcommand=desc_scrollbar.set)

        self.desc_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=25)

        ttk.Button(button_frame, text="确定", command=self.ok_clicked, width=15).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked, width=15).pack(side=tk.LEFT, padx=10)

        frame.columnconfigure(1, weight=1)

        # 设置默认值
        if default_data:
            self.name_entry.insert(0, default_data[1] or '')
            self.command_text.insert(1.0, default_data[2] or '')
            self.desc_text.insert(1.0, default_data[4] or '')
            # 设置分类
            for i, cat in enumerate(categories):
                if cat[0] == default_data[3]:
                    self.category_combo.current(i + 1)  # +1 因为加了空选项
                    break

        # 焦点到第一个输入框
        self.name_entry.focus_set()

        # 绑定键盘快捷键
        self.dialog.bind('<Return>', lambda event: self.ok_clicked())
        self.dialog.bind('<Escape>', lambda event: self.cancel_clicked())

        self.dialog.wait_window()

    def ok_clicked(self):
        name = self.name_entry.get().strip()
        command = self.command_text.get(1.0, tk.END).strip()
        category = self.category_combo.get()
        description = self.desc_text.get(1.0, tk.END).strip()

        if not name or not command:
            messagebox.showerror("错误", "命令名称和命令内容不能为空")
            return

        # 获取分类ID
        category_id = None
        if category:
            # 查找分类ID
            for cat_id, cat_name in self.categories:
                if cat_name == category:
                    category_id = cat_id
                    break

        self.result = (name, command, category_id, description)
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()


class HostDialog:
    """主机编辑对话框"""
    def __init__(self, parent, title, default_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 主机名称
        ttk.Label(frame, text="主机名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = ttk.Entry(frame, width=30)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # IP地址
        ttk.Label(frame, text="IP地址:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ip_entry = ttk.Entry(frame, width=30)
        self.ip_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # 端口
        ttk.Label(frame, text="端口:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.port_entry = ttk.Entry(frame, width=30)
        self.port_entry.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.port_entry.insert(0, "22")

        # 用户名
        ttk.Label(frame, text="用户名:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.username_entry = ttk.Entry(frame, width=30)
        self.username_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)

        # 描述
        ttk.Label(frame, text="描述:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.desc_entry = ttk.Entry(frame, width=30)
        self.desc_entry.grid(row=4, column=1, sticky=tk.EW, pady=5)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)

        frame.columnconfigure(1, weight=1)

        # 设置默认值
        if default_data:
            self.name_entry.insert(0, default_data[1] or '')
            self.ip_entry.insert(0, default_data[2] or '')
            self.port_entry.insert(0, str(default_data[3]) if default_data[3] else '22')
            self.username_entry.insert(0, default_data[4] or '')
            self.desc_entry.insert(0, default_data[5] or '')

        self.dialog.wait_window()

    def ok_clicked(self):
        name = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        username = self.username_entry.get().strip()
        description = self.desc_entry.get().strip()

        if not name or not ip:
            messagebox.showerror("错误", "主机名称和IP地址不能为空")
            return

        try:
            port = int(port_str)
            if port < 1 or port > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("错误", "端口必须是1-65535之间的数字")
            return

        self.result = (name, ip, port, username, description)
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()


class NoteDialog:
    """笔记编辑对话框"""
    def __init__(self, parent, title, default_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        # 标题
        ttk.Label(frame, text="标题:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=50)
        self.title_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

        # 分类
        ttk.Label(frame, text="分类:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.category_entry = ttk.Entry(frame, width=50)
        self.category_entry.grid(row=1, column=1, sticky=tk.EW, pady=5)

        # 内容
        ttk.Label(frame, text="内容:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        self.content_text = tk.Text(frame, width=50, height=20)
        self.content_text.grid(row=2, column=1, sticky=tk.NSEW, pady=5)

        # 滚动条
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=2, sticky=tk.NS, pady=5)

        # 按钮
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="确定", command=self.ok_clicked).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=self.cancel_clicked).pack(side=tk.LEFT, padx=5)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)

        # 设置默认值
        if default_data:
            self.title_entry.insert(0, default_data[1] or '')
            self.category_entry.insert(0, default_data[3] or '')
            self.content_text.insert(1.0, default_data[2] or '')

        self.dialog.wait_window()

    def ok_clicked(self):
        title = self.title_entry.get().strip()
        category = self.category_entry.get().strip()
        content = self.content_text.get(1.0, tk.END).strip()

        if not title:
            messagebox.showerror("错误", "标题不能为空")
            return

        self.result = (title, content, category)
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = CommandManager(root)
    root.mainloop()