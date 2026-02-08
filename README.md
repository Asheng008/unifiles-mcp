# unifiles-mcp

MCP server for [unifiles](https://github.com/Asheng008/unifiles) - unified file operations library.

## 简介

`unifiles-mcp` 是一个基于 [MCP Python SDK](https://pypi.org/project/mcp/) 官方 SDK 构建的 Model Context Protocol (MCP) 服务器，为 AI 助手提供统一的文件操作能力。它使用官方的 `FastMCP` 高级接口，封装了 `unifiles` 库的功能，支持 Excel、PDF、Word、SQLite 等多种文件格式的读取、写入、查询和管理。

## 功能特性

- ✅ **统一接口**: 通过 MCP 协议提供标准化的文件操作接口
- ✅ **多格式支持**: Excel (.xlsx, .xls), PDF (.pdf), Word (.docx), SQLite (.db, .sqlite)
- ✅ **类型安全**: 完整的类型注解，基于 Pydantic V2
- ✅ **异步优先**: 所有操作使用异步方式，提高性能
- ✅ **LLM 友好**: 优化的工具设计，减少调用次数

## 环境要求

- **Python**: 3.10+
- **操作系统**: Windows 10+, Linux, macOS 10.14+

## 安装

从源码安装（开发模式，含测试与类型检查等依赖）：

```powershell
git clone https://github.com/Asheng008/unifiles-mcp.git
cd unifiles-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

仅安装运行依赖：

```powershell
pip install -e .
```

使用依赖锁文件安装（推荐用于生产环境）：

```powershell
pip install -r requirements.txt
```

若已发布到 PyPI：

```bash
pip install unifiles-mcp
```

## 快速开始

### 启动服务器

安装后可在终端直接运行：

```bash
unifiles-mcp
```

或从代码启动：

```python
from unifiles_mcp.main import mcp

if __name__ == "__main__":
    mcp.run()
```

### 使用 MCP 客户端连接

服务器启动后，可以通过 MCP 客户端（如 Claude Desktop）连接使用。

### 使用示例

#### Excel 文件操作

```python
# 1. 检查 Excel 文件结构
result = await excel_inspect_file({
    "file_path": "data.xlsx",
    "include_preview": True,
    "preview_rows": 3
})
# 返回：文件信息，包括所有工作表名称、列名和预览数据

# 2. 读取工作表内容
result = await excel_read_sheet({
    "file_path": "data.xlsx",
    "sheet_name": "Sheet1"
})
# 返回：JSON 格式的工作表数据
```

#### SQLite 数据库操作

```python
# 1. 检查数据库结构
result = await sqlite_inspect_database({
    "db_path": "database.db",
    "include_preview": True
})
# 返回：数据库信息，包括所有表的结构和数据预览

# 2. 获取表结构
result = await sqlite_get_schema({
    "db_path": "database.db",
    "table_name": "users"
})
# 返回：字段名到类型的映射

# 3. 执行查询
result = await sqlite_query({
    "db_path": "database.db",
    "sql": "SELECT * FROM users WHERE age > :age",
    "params": {"age": 18}
})
# 返回：JSON 格式的查询结果
```

#### PDF 文本提取

```python
# 提取所有页面
result = await pdf_extract_text({
    "file_path": "document.pdf"
})

# 提取指定页面范围
result = await pdf_extract_text({
    "file_path": "document.pdf",
    "page_range": (1, 5)  # 第 1 到第 5 页
})
```

#### Word 文档读取

```python
result = await word_read_document({
    "file_path": "document.docx"
})
# 返回：文档的文本内容
```

## 核心工具（v0.1.2）

### Excel 工具
- `excel_inspect_file` - 检查 Excel 文件结构（"上帝视角"）
- `excel_read_sheet` - 读取 Excel 工作表内容

### PDF 工具
- `pdf_extract_text` - 提取 PDF 文本内容

### Word 工具
- `word_read_document` - 读取 Word 文档内容

### SQLite 工具
- `sqlite_inspect_database` - 检查 SQLite 数据库（"上帝视角"）
- `sqlite_get_schema` - 获取表结构
- `sqlite_query` - 执行 SQL 查询

### 通用工具
- `ping` - 健康检查，返回 `pong` 表示服务运行中

## 开发

### 代码格式化与静态检查

```powershell
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 使用 black 格式化代码
black src/

# 使用 ruff 检查代码
ruff check src/
```

### 类型检查

```powershell
# 使用 mypy 进行类型检查
mypy src/unifiles_mcp/
```

## 项目结构

```
unifiles-mcp/
├── src/
│   └── unifiles_mcp/
│       ├── __init__.py
│       ├── main.py              # MCP 服务器入口
│       ├── tools/               # MCP 工具
│       │   ├── __init__.py
│       │   ├── excel.py
│       │   ├── pdf.py
│       │   ├── word.py
│       │   └── sqlite.py
│       └── utils/               # 工具函数
│           ├── __init__.py
│           ├── async_wrapper.py
│           └── validators.py
├── docs/                       # 文档
│   ├── API.md                  # API 文档
│   ├── PYPI_RELEASE_CHECKLIST.md
│   └── README.md
├── .cursor/                    # Cursor IDE 配置
│   ├── commands/               # Cursor 命令
│   ├── rules/                  # 项目规则
│   ├── skills/                 # Cursor Skills
│   └── mcp.json                # MCP 配置
├── LICENSE                     # MIT 许可证
├── publish_pypi.bat           # 一键发布到 PyPI 脚本
├── requirements.txt            # 生产依赖
├── requirements-dev.txt        # 开发依赖（可选）
├── pyproject.toml              # 项目配置
├── CHANGELOG.md                # 更新日志
├── HISTORY.md                  # 对话与变更历史
├── AGENTS.md                   # AI Agent 开发规范
└── README.md                   # 本文档
```

## 文档

- [API 文档](./docs/API.md) - 详细的工具 API 说明和使用示例
- [PyPI 发布清单](./docs/PYPI_RELEASE_CHECKLIST.md) - 发布到 PyPI 前的检查与步骤
- [技术需求文档](./TRD.md) - 项目技术需求
- [API 设计文档](./API_DESIGN.md) - API 设计方案
- [API 设计评审](./API_DESIGN_REVIEW.md) - API 设计评审文档
- [开发规范](./AGENTS.md) - AI Agent 开发规范
- [更新日志](./CHANGELOG.md) - 版本变更记录
- [历史记录](./HISTORY.md) - 对话与变更历史

## 作者与维护者

- **作者**：Asheng (`w62745@qq.com`)
- **仓库**：[https://github.com/Asheng008/unifiles-mcp](https://github.com/Asheng008/unifiles-mcp)
- 欢迎通过 Issues 或 Pull Request 参与贡献。

## 许可证

本项目采用 [MIT License](./LICENSE)。

## 相关项目

- [unifiles](https://github.com/Asheng008/unifiles) - 统一的文件操作库
- [MCP Python SDK](https://pypi.org/project/mcp/) - Model Context Protocol 官方 Python SDK
- [MCP 官方文档](https://modelcontextprotocol.github.io/python-sdk/) - MCP Python SDK 完整文档
