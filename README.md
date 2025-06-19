# 🚨 自动化警信人员预警系统

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![DrissionPage](https://img.shields.io/badge/DrissionPage-4.1.0+-green.svg)](https://github.com/g1879/DrissionPage)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> 🎯 基于DrissionPage的智能化警信人员预警自动化系统，实现重点人员情报信息的自动采集、处理和分发。

## 📋 项目简介

本系统是一个专业的自动化警务辅助工具，旨在提高警务人员的工作效率。系统能够自动登录重点人员信息系统，获取最新的情报信息，并将相关文件自动上传到警信群聊中，实现情报信息的快速流转和共享。

### 🎯 核心价值

- **🔄 全自动化流程**：无需人工干预，系统自动完成整个信息流转过程
- **⏰ 定时执行**：支持自定义时间间隔，确保信息及时更新
- **🔐 多账号支持**：支持多个重点人网站账号，提高信息覆盖面
- **📊 智能监控**：实时监控系统运行状态，提供详细的执行日志
- **🎨 友好界面**：直观的GUI界面，操作简单，易于上手

## ✨ 功能特性

### 🌟 核心功能

| 功能模块 | 描述 | 状态 |
|---------|------|------|
| 🔐 **自动登录** | 支持重点人网站和警信网站的自动登录 | ✅ |
| 📊 **情报检索** | 自动检查和下载新的情报信息 | ✅ |
| 📁 **文件管理** | 智能文件下载、重命名和组织 | ✅ |
| 📤 **自动上传** | 自动将文件上传到指定警信群聊 | ✅ |
| 🔄 **循环执行** | 支持自定义间隔的定时自动执行 | ✅ |
| 📝 **日志记录** | 详细的操作日志和错误追踪 | ✅ |

### 🛠️ 高级特性

- **🖥️ 多运行模式**：
  - 新浏览器模式：每次启动全新浏览器实例
  - 连接模式：连接已有浏览器，节省资源
  - 无头模式：后台运行，不占用桌面空间

- **📊 智能监控**：
  - 实时状态显示
  - 循环次数统计
  - 下次执行时间预告
  - 彩色日志分级显示

- **⚙️ 配置管理**：
  - 导入/导出配置文件
  - 多账号管理
  - 自定义下载目录
  - 日志级别调整

## 🚀 快速开始

### 📋 系统要求

- **操作系统**：Windows 10/11
- **Python版本**：3.6 或更高版本
- **浏览器**：Chrome 或 Microsoft Edge
- **网络环境**：稳定的互联网连接

### 📦 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/auto-police-alert-system.git
cd auto-police-alert-system
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行程序**
```bash
python main.py
```

### 🎮 快速配置

1. **启动程序**后，在GUI界面中配置以下信息：

   **重点人网站配置**：
   - 账号1用户名/密码（必填）
   - 账号2用户名/密码（可选，用于多账号支持）

   **警信网站配置**：
   - 身份证号
   - 登录密码
   - 群聊名称（默认："情指值班通知"）

2. **选择运行模式**和**设置循环间隔**

3. **点击"启动"**开始自动化流程

## 📖 详细使用指南

### 🔧 配置说明

#### 重点人网站配置
- **多账号支持**：系统支持配置两个重点人网站账号，提高信息采集的覆盖面
- **自动轮换**：系统会依次使用配置的账号进行信息采集

#### 警信网站配置
- **群聊定位**：系统会自动定位到指定名称的群聊
- **文件上传**：自动将下载的情报文件上传到群聊中

#### 运行模式选择
- **新浏览器**：适合首次使用或需要完全独立运行
- **连接已有浏览器**：适合调试或需要手动干预的场景
- **无头模式**：适合服务器部署或后台运行

### 🎛️ 系统控制

系统提供完整的状态控制功能：

```
[未运行] --启动--> [运行中] --暂停--> [已暂停]
    ↑                 ↓              ↓
    +-------停止-------+------恢复------+
```

- **启动**：开始自动化流程
- **暂停**：临时停止，保持状态
- **恢复**：从暂停状态继续运行
- **停止**：完全停止并清理资源
- **立即执行**：手动触发一次完整流程

### 📊 监控与日志

#### 实时状态监控
- 当前运行状态
- 已执行循环次数
- 下次执行时间预告

#### 日志系统
- **DEBUG**：详细的调试信息
- **INFO**：一般操作信息
- **WARNING**：警告信息
- **ERROR**：错误信息
- **CRITICAL**：严重错误

## 🏗️ 技术架构

### 📁 项目结构

```
auto-police-alert-system/
├── 📄 main.py                 # 程序入口
├── 🖥️ gui.py                  # GUI界面模块
├── 🌐 website_handler.py      # 网站操作核心模块
├── ⚙️ config.py              # 配置管理模块
├── 📝 logger.py              # 日志系统模块
├── 📋 requirements.txt       # 依赖包列表
├── 📊 default_config.json    # 默认配置文件
├── 📂 logs/                  # 日志文件目录
├── 📂 downloads/             # 下载文件目录
├── 📂 code/                  # 备用代码目录
└── 📄 README.md              # 项目说明文档
```

### 🔧 核心模块

#### WebsiteHandler（网站操作处理器）
- **重点人网站处理**：自动登录、导航、文件下载
- **警信网站处理**：自动登录、群聊定位、文件上传
- **浏览器管理**：多模式浏览器控制
- **错误处理**：智能重试和异常恢复

#### ConfigManager（配置管理器）
- **配置文件管理**：导入/导出JSON格式配置
- **参数验证**：确保配置的完整性和正确性
- **动态更新**：支持运行时配置修改

#### Logger（日志系统）
- **多级别日志**：支持DEBUG、INFO、WARNING、ERROR、CRITICAL
- **文件日志**：自动按日期分割日志文件
- **彩色显示**：GUI界面中的彩色日志显示

### 🛠️ 技术栈

- **核心框架**：[DrissionPage](https://github.com/g1879/DrissionPage) - 强大的网页自动化框架
- **GUI框架**：Tkinter - Python内置GUI库
- **自动化工具**：PyAutoGUI - 桌面自动化辅助
- **打包工具**：PyInstaller - 生成独立可执行文件

## 🔧 高级功能

### 📦 打包部署

生成独立的可执行文件：

```bash
# 安装打包工具
pip install pyinstaller

# 生成单文件版本
pyinstaller --onefile --windowed main.py

# 生成目录版本（推荐）
pyinstaller --windowed main.py
```

### 🔍 故障排查

#### 常见问题解决

1. **浏览器启动失败**
   - 检查Chrome/Edge是否正确安装
   - 确认浏览器版本兼容性

2. **登录失败**
   - 验证账号密码正确性
   - 检查网络连接状态
   - 查看详细日志信息

3. **文件上传失败**
   - 确认群聊名称正确
   - 检查文件格式和大小
   - 验证网络连接稳定性

#### 日志分析

系统提供详细的日志信息，位于 `logs/` 目录下：
- 按日期自动分割
- 包含完整的操作轨迹
- 错误信息详细记录

## 🤝 贡献指南

我们欢迎各种形式的贡献！

### 📝 如何贡献

1. **Fork** 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 **Pull Request**

### 🐛 问题反馈

如果您发现任何问题，请通过以下方式反馈：

- 在 [Issues](https://github.com/your-username/auto-police-alert-system/issues) 页面提交问题
- 提供详细的错误信息和日志
- 描述重现问题的步骤

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [DrissionPage](https://github.com/g1879/DrissionPage) - 提供强大的网页自动化能力
- Python 社区 - 提供丰富的开源库支持
- 所有贡献者 - 感谢您们的支持和建议

## 📞 联系方式

- 项目主页：[GitHub Repository](https://github.com/your-username/auto-police-alert-system)
- 问题反馈：[Issues](https://github.com/your-username/auto-police-alert-system/issues)
- 邮箱：your-email@example.com

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个Star！**

Made with ❤️ by [Your Name]

</div> 