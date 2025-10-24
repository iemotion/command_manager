# 命令管理工具

一个功能完整的图形化命令管理工具，帮助您组织、管理和快速执行常用的命令。

## ✨ 功能特性

### 📋 命令管理
- **命令分类管理** - 创建和管理命令分类，便于组织不同类型的命令
- **命令增删改查** - 完整的命令生命周期管理
- **命令收藏** - 标记常用命令，快速访问
- **搜索过滤** - 快速搜索和过滤命令

### 📝 笔记管理
- **分类笔记** - 按分类组织学习笔记
- **富文本编辑** - 支持多行文本内容
- **快速检索** - 搜索笔记内容

## 🚀 快速开始

### 方式一：直接运行源码
```bash
# 克隆或下载项目
git clone <repository-url>
cd command-manager-tool

# 运行启动器
python launcher.py
```

### 方式二：安装依赖后运行
```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python launcher.py
```

### 方式三：构建独立可执行文件
```bash
# 构建应用程序
python build_app.py

# 运行生成的可执行文件
./dist/CommandManager  # Linux/macOS
# 或
dist/CommandManager.exe  # Windows
```

## 📁 项目结构

```
command-manager-tool/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── main.py            # 主程序入口
│   ├── command_manager.py # 核心GUI程序
│   └── backup.py          # 数据库备份脚本
├── assets/                 # 资源文件
│   ├── icon.py           # 图标生成脚本
│   └── icon.png          # 应用图标
├── examples/               # 示例代码
│   └── example_usage.py   # 使用示例
├── data/                   # 数据目录（运行时创建）
│   └── command_manager.db # SQLite数据库
├── backups/               # 备份目录
├── launcher.py           # 启动器
├── build_app.py          # 构建脚本
├── setup.py              # 安装脚本
├── requirements.txt      # 依赖列表
└── README.md            # 项目说明
```

## 🛠️ 系统要求

- Python 3.6 或更高版本
- tkinter (Python内置GUI库)
- SQLite (Python内置)
- 操作系统：Windows / macOS / Linux

## 📖 使用指南

### 命令管理

1. **添加命令**
   - 点击"添加命令"按钮
   - 填写命令名称、命令内容、选择分类
   - 可选添加描述信息

2. **管理分类**
   - 点击"分类管理"进入分类管理界面
   - 添加、编辑或删除分类

3. **收藏命令**
   - 在命令列表中选择命令
   - 点击"收藏/取消收藏"按钮

### 笔记管理

1. **创建笔记**
   - 点击"添加笔记"
   - 填写标题、分类和内容

2. **组织笔记**
   - 使用分类对笔记进行分组
   - 使用搜索功能快速查找

## 🔧 数据管理

### 数据备份
```bash
# 备份数据库
python src/backup.py backup

# 列出备份文件
python src/backup.py list

# 恢复备份
python src/backup.py restore backups/backup_file.db
```

### 数据迁移
整个项目的数据库文件位于 `data/command_manager.db`，要迁移到其他设备，只需：
1. 复制整个项目文件夹
2. 或者只复制 `data/command_manager.db` 文件

## 🎨 界面截图

*(可以添加界面截图)*

## 🔌 开发

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd command-manager-tool

# 创建虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装开发依赖
pip install -r requirements.txt
pip install -e .

# 运行测试
python launcher.py
```

### 代码结构
- `src/main.py` - 应用程序入口点
- `src/command_manager.py` - 主要的GUI逻辑
- `src/backup.py` - 数据库备份功能
- `launcher.py` - 独立启动器
- `build_app.py` - 构建可执行文件的脚本

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 🆘 问题反馈

如果遇到问题：

1. 检查Python版本是否为3.6+
2. 确保tkinter可用
3. 检查文件权限
4. 查看错误信息
5. 提交Issue到项目仓库

## 📊 更新日志

### v1.0.0 (2025-01-01)
- ✨ 初始版本发布
- ✅ 实现命令管理功能
- ✅ 实现主机管理功能
- ✅ 实现命令生成器
- ✅ 实现笔记管理功能
- ✅ 支持数据持久化
- ✅ 支持独立可执行文件构建

## 🙏 致谢

感谢所有贡献者和用户的支持！