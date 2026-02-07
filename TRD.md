# unifiles-mcp 技术需求文档 (Technical Requirements Document)

> **版本**: v2.1  
> **日期**: 2026-02-07  
> **状态**: 部分实现 (7/12 工具已实现)  
> **更新**: 与当前代码同步（平铺参数、无 config、无 Resources/Prompts）

## 1. 项目概述 (Project Overview)

### 1.1 项目背景
`unifiles-mcp` 是基于已发布到 PyPI 的 `unifiles` 库（版本 0.3.1，作者 Asheng008）构建的 **Model Context Protocol (MCP)** 服务器。该项目旨在通过 MCP 协议，为 AI 助手（如 Claude、GPT-4 等）提供统一的文件操作能力，支持 Excel、PDF、Word、SQLite 等多种文件格式的读取、写入、查询和管理。

**注意**: 
- PyPI 包名：`unifiles`
- GitHub 仓库：https://github.com/Asheng008/unifiles
- 当前版本：0.3.1

**当前实现状态（v0.1.2）**：已实现 7 个核心工具（Excel 2、PDF 1、Word 1、SQLite 3），工具采用平铺参数 + `Annotated`/`Field`，无独立配置模块、无 Resources/Prompts、暂不包含自动化测试目录。

### 1.2 项目目标
- **核心目标**: 将 `unifiles` 的文件操作能力封装为 MCP Tools，使 AI 助手能够通过标准化接口进行文件操作
- **技术目标**: 
  - 构建高性能、类型安全、生产就绪的 MCP 服务器
  - 遵循 MCP Python 官方 SDK 最佳实践
  - **将同步的 `unifiles` API 包装为异步接口**（重要：`unifiles` 库本身是同步的）
  - 提供完整的异步文件操作能力
  - 支持多种文件格式的统一处理

### 1.3 目标用户
- AI 助手开发者（集成 MCP 服务器）
- 需要文件操作能力的 AI 应用
- 自动化脚本和工具链

## 2. 功能需求 (Functional Requirements)

### 2.1 设计原则

1. **保留原生能力**：`unifiles` 已经封装得很好了，MCP 层应尽量直接映射，不做过多业务逻辑。
2. **前缀命名**：使用 `excel_*`, `sqlite_*`, `pdf_*`, `word_*` 作为工具名前缀，防止命名冲突。
3. **优先使用 Info 函数**：充分利用 `get_excel_info`、`get_database_info` 等"上帝视角"工具，减少 LLM 调用次数。
4. **精简 API 暴露**：不暴露冗余函数（如 `get_sheet_names`、`get_column_names`），避免 LLM 选择困难。

### 2.2 核心功能模块

#### 2.2.1 Excel 文件操作

##### 2.2.1.1 检查 Excel 文件 (`excel_inspect_file`) ⭐⭐⭐ 核心
- **功能**: 获取整个 Excel 文件的完整信息（"上帝视角"工具）
- **底层 API**: `unifiles.get_excel_info(file_path, include_preview=False, preview_rows=3) -> dict[str, Any]`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: Excel 文件路径（字符串）
  - `include_preview`: 是否包含数据预览（可选，默认 False）
  - `preview_rows`: 预览行数（可选，默认 3）
- **输出**: 包含文件信息的字典（文件大小、工作表数量、所有工作表信息）
- **设计理由**: 一次调用就能知道有哪些 Sheet，以及每张表长什么样。这比单独调 `get_sheet_names` 高效得多。

##### 2.2.1.2 检查 Excel 工作表 (`excel_inspect_sheet`) ⭐⭐
- **功能**: 获取单个 Excel 工作表的详细信息
- **底层 API**: `unifiles.get_sheet_info(file_path, sheet_name=None, preview_rows=5) -> dict[str, Any]`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: Excel 文件路径
  - `sheet_name`: 工作表名称或索引（可选，None 表示第一个工作表）
  - `preview_rows`: 预览行数（可选，默认 5）
- **输出**: 包含工作表信息的字典（行数、列数、列名、预览数据）
- **设计理由**: 用于查看单个工作表的详细信息（不需要读取全部数据），适合"先看结构，再决定是否读取全部"的场景。

##### 2.2.1.3 读取 Excel 工作表 (`excel_read_sheet`) ⭐⭐⭐ 核心
- **功能**: 读取 Excel 文件内容为 DataFrame
- **底层 API**: `unifiles.read_excel(file_path, sheet_name=None) -> pd.DataFrame`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: Excel 文件路径（字符串）
  - `sheet_name`: 工作表名称或索引（可选，None 表示读取第一个工作表）
- **输出**: JSON 格式的 DataFrame 数据（字典列表）
- **设计理由**: 用于读取完整数据。注意：如果数据量大，需要在 MCP 层做截断保护。

##### 2.2.1.4 写入 Excel 数据 (`excel_write_data`) ⭐⭐
- **功能**: 将数据写入 Excel 文件
- **底层 API**: `unifiles.write_excel(data, file_path, sheet_name="Sheet1") -> None`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: 输出 Excel 文件路径
  - `sheet_name`: 工作表名称（可选，当 data 为单个工作表时使用，默认 "Sheet1"）
  - `data`: 要写入的数据
    - **单个工作表**: `list[dict[str, Any]]` - 例如 `[{"col1": "val1", "col2": "val2"}, ...]`
    - **多个工作表**: `dict[str, list[dict[str, Any]]]` - 例如 `{"Sheet1": [...], "Sheet2": [...]}`
- **输出**: 操作结果（成功/失败信息）
- **注意**: 会覆盖整个目标文件
- **设计理由**: 用于让 LLM 修改文件。`data` 需要定义为 JSON 列表结构。

#### 2.2.2 PDF 文件操作

##### 2.2.2.1 提取 PDF 文本 (`pdf_extract_text`) ⭐⭐⭐ 核心
- **功能**: 从 PDF 文件中提取文本内容
- **底层 API**: `unifiles.extract_text(file_path, page_range=None) -> str`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: PDF 文件路径
  - `page_range`: 页码范围（可选）
    - **格式**: `tuple[int, int] | None` - 例如 `(1, 5)` 表示第 1 到第 5 页
    - **说明**: 1-based（从 1 开始），None 表示提取所有页面
- **输出**: 提取的文本内容（字符串，页面之间用换行符分隔）
- **设计理由**: 通用读取工具。`page_range` 是关键，允许 LLM 按需读取，避免处理大文件时性能问题。

##### 2.2.2.2 提取 PDF 表格 (`pdf_extract_tables`) ⭐⭐
- **功能**: 从 PDF 文件中提取表格数据
- **底层 API**: `unifiles.extract_tables(file_path, page_range=None) -> list[pd.DataFrame]`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: PDF 文件路径
  - `page_range`: 页码范围（可选）
    - **格式**: `tuple[int, int] | None` - 例如 `(1, 5)` 表示第 1 到第 5 页
    - **说明**: 1-based（从 1 开始），None 表示提取所有页面
- **输出**: 表格列表（每个表格为 JSON 格式的 DataFrame）
- **限制**: MVP 版本仅支持基础表格，复杂布局可能识别不准
- **设计理由**: 专用读取工具。当 LLM 发现 PDF 里有数据表时，引导它用这个工具，而不是用 OCR 或文本解析。

#### 2.2.3 Word 文件操作

##### 2.2.3.1 读取 Word 文档 (`word_read_document`) ⭐⭐⭐ 核心
- **功能**: 读取 Word 文档内容
- **底层 API**: `unifiles.read_docx(file_path) -> str`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: Word 文档路径（字符串）
- **输出**: 文档的文本内容（字符串，段落之间用换行符分隔）
- **设计理由**: 简单直接，用于读取 Word 文档的全部文本内容。

##### 2.2.3.2 写入 Word 文档 (`word_write_document`) ⭐⭐
- **功能**: 将内容写入 Word 文档
- **底层 API**: `unifiles.write_docx(content, file_path, title=None) -> None`
- **MCP 组件**: Tool
- **输入参数**:
  - `file_path`: 输出 Word 文档路径
  - `content`: 要写入的文本内容（字符串）
  - `title`: 可选的文档标题（字符串，默认 None）
- **输出**: 操作结果（成功/失败信息）
- **设计理由**: 用于生成报告或文档。相对简单，通常作为纯文本处理。

#### 2.2.4 SQLite 数据库操作

SQLite 的交互逻辑是：先看表结构，再查数据。

##### 2.2.4.1 检查 SQLite 数据库 (`sqlite_inspect_database`) ⭐⭐⭐ 核心
- **功能**: 获取 SQLite 数据库的完整信息（"上帝视角"工具）
- **底层 API**: `unifiles.get_database_info(db_path, include_preview=False, preview_rows=3) -> dict[str, Any]`
- **MCP 组件**: Tool
- **输入参数**:
  - `db_path`: SQLite 数据库文件路径
  - `include_preview`: 是否包含数据预览（可选，默认 False）
  - `preview_rows`: 预览行数（可选，默认 3）
- **输出**: 包含数据库信息的字典（文件大小、表数量、所有表信息）
- **设计理由**: 一次调用获取数据库全貌（表数量、每个表的结构、行数等），与 `excel_inspect_file` 保持设计一致性。

##### 2.2.4.2 列出 SQLite 表 (`sqlite_list_tables`) ⭐⭐
- **功能**: 获取数据库中所有表名列表
- **底层 API**: `unifiles.get_tables(db_path) -> list[str]`
- **MCP 组件**: Tool
- **输入参数**:
  - `db_path`: SQLite 数据库文件路径
- **输出**: 表名列表（JSON 数组，排除系统表）
- **设计理由**: 入口工具，快速了解数据库概貌。如果已使用 `sqlite_inspect_database`，此工具可省略。

##### 2.2.4.3 获取 SQLite 表结构 (`sqlite_get_schema`) ⭐⭐⭐ 核心
- **功能**: 获取表结构（字段名到字段类型的映射）
- **底层 API**: `unifiles.get_schema(db_path, table_name) -> dict[str, str]`
- **MCP 组件**: Tool
- **输入参数**:
  - `db_path`: SQLite 数据库文件路径
  - `table_name`: 表名（字符串）
- **输出**: 字段名到字段类型的字典映射
- **设计理由**: **核心工具**。LLM 写 SQL 前必须看 Schema。

##### 2.2.4.4 执行 SQLite 查询 (`sqlite_query`) ⭐⭐⭐ 核心
- **功能**: 执行 SQL 查询并返回 DataFrame
- **底层 API**: `unifiles.query(db_path, sql, params=None) -> pd.DataFrame`
- **MCP 组件**: Tool
- **输入参数**:
  - `db_path`: SQLite 数据库文件路径
  - `sql`: SQL 查询语句（字符串）
  - `params`: 查询参数（可选）
    - **格式**: `tuple | dict | None`
    - **说明**: tuple 用于 `?` 占位符（如 `(18,)`），dict 用于 `:name` 占位符（如 `{"age": 18}`）
- **输出**: 查询结果（JSON 格式的 DataFrame）
- **设计理由**: **执行工具**。注意：MCP 层可以将 `params` 设为可选，或者让 LLM 直接把参数拼在 SQL 里（如果是只读查询，风险可控）。

### 2.2 Resources（资源）

#### 2.2.1 文件内容资源 (File Content Resource)
- **URI 模式**: `unifile://{file_path}`
- **功能**: 以资源形式暴露文件内容
- **参数**: `file_path`（路径参数）
- **返回**: 文件内容（根据文件类型自动选择读取方式）
- **支持格式**: Excel, PDF, Word, SQLite

#### 2.2.2 Excel 工作表资源 (Excel Sheet Resource)
- **URI 模式**: `unifile://excel/{file_path}/{sheet_name}`
- **功能**: 以资源形式暴露 Excel 工作表内容
- **参数**: 
  - `file_path`: Excel 文件路径
  - `sheet_name`: 工作表名称
- **返回**: 工作表数据（JSON 格式）

#### 2.2.3 SQLite 表资源 (SQLite Table Resource)
- **URI 模式**: `unifile://sqlite/{db_path}/{table_name}`
- **功能**: 以资源形式暴露 SQLite 表内容
- **参数**:
  - `db_path`: 数据库文件路径
  - `table_name`: 表名
- **返回**: 表数据（JSON 格式）

### 2.3 Prompts（提示模板）

#### 2.3.1 文件操作提示模板
- **名称**: `file_operation_guide`
- **功能**: 提供文件操作的最佳实践和示例
- **内容**: 包含常见文件操作场景的提示模板

## 3. 技术架构 (Technical Architecture)

### 3.1 技术栈
- **语言**: Python 3.10+
- **MCP 框架**: MCP Python 官方 SDK（`mcp.server.fastmcp`）
- **类型系统**: Pydantic V2
- **异步库**: `asyncio`（用于异步包装）
- **依赖库**: 
  - `unifiles>=0.3.1` (PyPI) - 核心文件操作库
  - `pandas` - 数据处理（unifiles 依赖）
  - `openpyxl` - Excel 处理（unifiles 依赖）
  - `pypdf` - PDF 处理（unifiles 依赖）
  - `python-docx` - Word 处理（unifiles 依赖）
- **测试框架**: `pytest`, `pytest-asyncio`

### 3.1.1 异步包装策略
由于 `unifiles` 库是同步的，需要将其包装为异步函数：
- 使用 `asyncio.to_thread()` 在线程池中执行同步操作
- 确保所有 MCP Tool 函数都是 `async def`
- 对于 I/O 密集型操作（文件读取/写入），异步包装可以避免阻塞事件循环

### 3.2 项目结构（当前实现）

```
unifiles-mcp/
├── src/
│   └── unifiles_mcp/
│       ├── __init__.py
│       ├── main.py              # MCP 服务器入口（服务名硬编码 "unifiles-mcp"）
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── excel.py         # excel_inspect_file, excel_read_sheet
│       │   ├── pdf.py           # pdf_extract_text
│       │   ├── word.py          # word_read_document
│       │   └── sqlite.py        # sqlite_inspect_database, sqlite_get_schema, sqlite_query
│       └── utils/
│           ├── __init__.py
│           ├── async_wrapper.py # 异步包装（to_async）
│           └── validators.py    # 路径与页码校验
├── docs/
│   ├── API.md
│   └── README.md
├── .cursor/                     # Cursor 命令、规则、技能
├── .venv/                       # 虚拟环境（gitignore）
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── AGENTS.md
├── TRD.md                       # 本文档
└── README.md
```

**未实现 / 已移除**：`config.py`（已删除，改为硬编码）、`resources/`、`prompts/`、`tests/`（当前暂不包含）。

### 3.3 架构设计原则
- **分层架构**: 入口层 → 功能层 → 共享层 → 测试层
- **依赖注入**: 使用 MCP Python 官方 SDK 的 `Context` 进行依赖注入
- **类型安全**: 所有函数参数必须有类型提示
- **异步优先**: 所有 I/O 操作使用异步方式
- **错误处理**: 统一的异常处理和日志记录机制

## 4. API 设计规范 (API Design Specification)

### 4.1 Tool 命名规范
- **格式**: `{module}_{action}_{object}`（小写，下划线分隔）
- **前缀命名**: 使用 `excel_*`, `sqlite_*`, `pdf_*`, `word_*` 作为工具名前缀，防止命名冲突
- **Excel 示例**: 
  - `excel_inspect_file` ⭐⭐⭐ 核心
  - `excel_inspect_sheet` ⭐⭐
  - `excel_read_sheet` ⭐⭐⭐ 核心
  - `excel_write_data` ⭐⭐
- **PDF 示例**:
  - `pdf_extract_text` ⭐⭐⭐ 核心
  - `pdf_extract_tables` ⭐⭐
- **Word 示例**:
  - `word_read_document` ⭐⭐⭐ 核心
  - `word_write_document` ⭐⭐
- **SQLite 示例**:
  - `sqlite_inspect_database` ⭐⭐⭐ 核心
  - `sqlite_list_tables` ⭐⭐
  - `sqlite_get_schema` ⭐⭐⭐ 核心
  - `sqlite_query` ⭐⭐⭐ 核心

### 4.2 参数设计规范
- **当前实现**：采用**平铺参数**，不使用 Pydantic BaseModel；每个参数使用 `Annotated[T, Field(description=...)]`，校验在函数内部通过 `validators` 完成（参见 .cursor/rules/code_style.mdc）。
- **类型注解**: 所有参数必须有完整的类型提示
- **字段描述**: 使用 `Annotated` 和 `Field` 提供详细的参数描述（MCP 据此生成 schema）
- **默认值**: 合理设置默认值；注意无默认值参数必须排在带默认值参数之前（如 `ctx: Context` 在可选参数前）

### 4.3 返回值设计
- **成功**: 返回操作结果（字符串或结构化数据）
- **失败**: 返回友好的错误信息，通过 `ctx.error()` 记录详细日志
- **格式**: 优先返回结构化数据（JSON），便于 AI 助手解析
- **DataFrame 转换**: 所有 pandas DataFrame 需要转换为 JSON 格式（字典列表）

### 4.4 示例 API 定义

```python
from mcp.server.fastmcp import FastMCP, Context
from typing import Annotated
from pydantic import BaseModel, Field
import asyncio
import unifiles
import json

class ExcelInspectFileParams(BaseModel):
    """Excel 文件检查参数"""
    file_path: Annotated[str, Field(description="要检查的 Excel 文件路径")]
    include_preview: Annotated[bool, Field(description="是否包含数据预览", default=False)] = False
    preview_rows: Annotated[int, Field(description="预览行数", default=3)] = 3

@mcp.tool
async def excel_inspect_file(
    params: ExcelInspectFileParams,
    ctx: Context,
) -> dict:
    """
    检查 Excel 文件结构。
    
    返回包含所有 Sheet 名称、列头和前几行数据预览的摘要信息。
    在决定读取哪个 Sheet 之前，请先使用此工具。
    """
    await ctx.info(f"开始检查 Excel 文件: {params.file_path}")
    
    try:
        # 将同步函数包装为异步
        info = await asyncio.to_thread(
            unifiles.get_excel_info,
            params.file_path,
            params.include_preview,
            params.preview_rows
        )
        
        await ctx.info(f"成功检查文件: {params.file_path}")
        return info
    except FileNotFoundError:
        await ctx.error(f"文件不存在: {params.file_path}")
        raise ValueError(f"文件不存在: {params.file_path}")
    except Exception as e:
        await ctx.error(f"检查文件时出错: {e}")
        raise ValueError(f"检查文件失败: {str(e)}")

class ExcelReadSheetParams(BaseModel):
    """Excel 工作表读取参数"""
    file_path: Annotated[str, Field(description="要读取的 Excel 文件路径")]
    sheet_name: Annotated[str | int | None, Field(description="工作表名称或索引，None 表示读取第一个工作表", default=None)] = None

@mcp.tool
async def excel_read_sheet(
    params: ExcelReadSheetParams,
    ctx: Context,
) -> str:
    """
    读取 Excel 工作表内容并返回 JSON 格式的数据。
    
    支持读取单个工作表。如果数据量大，返回结果可能被截断。
    """
    await ctx.info(f"开始读取 Excel 工作表: {params.file_path}, sheet: {params.sheet_name}")
    
    try:
        # 将同步函数包装为异步
        df = await asyncio.to_thread(
            unifiles.read_excel,
            params.file_path,
            params.sheet_name
        )
        
        # 将 DataFrame 转换为 JSON 格式
        # 处理 NaN 值，转换为 None
        df_filled = df.fillna(value=None)
        result = df_filled.to_dict("records")
        
        await ctx.info(f"成功读取工作表: {params.file_path}, 行数: {len(result)}")
        return json.dumps(result, ensure_ascii=False, indent=2)
    except FileNotFoundError:
        await ctx.error(f"文件不存在: {params.file_path}")
        raise ValueError(f"文件不存在: {params.file_path}")
    except Exception as e:
        await ctx.error(f"读取文件时出错: {e}")
        raise ValueError(f"读取文件失败: {str(e)}")
```

### 4.5 unifiles API 映射表

| MCP Tool | unifiles 函数 | 优先级 | 说明 |
|----------|--------------|:---:|------|
| **Excel 模块** ||||
| `excel_inspect_file` | `get_excel_info()` | ⭐⭐⭐ | 检查 Excel 文件（上帝视角） |
| `excel_inspect_sheet` | `get_sheet_info()` | ⭐⭐ | 检查 Excel 工作表 |
| `excel_read_sheet` | `read_excel()` | ⭐⭐⭐ | 读取 Excel 工作表 |
| `excel_write_data` | `write_excel()` | ⭐⭐ | 写入 Excel 数据 |
| **PDF 模块** ||||
| `pdf_extract_text` | `extract_text()` | ⭐⭐⭐ | 提取 PDF 文本 |
| `pdf_extract_tables` | `extract_tables()` | ⭐⭐ | 提取 PDF 表格 |
| **Word 模块** ||||
| `word_read_document` | `read_docx()` | ⭐⭐⭐ | 读取 Word 文档 |
| `word_write_document` | `write_docx()` | ⭐⭐ | 写入 Word 文档 |
| **SQLite 模块** ||||
| `sqlite_inspect_database` | `get_database_info()` | ⭐⭐⭐ | 检查 SQLite 数据库（上帝视角） |
| `sqlite_list_tables` | `get_tables()` | ⭐⭐ | 列出 SQLite 表 |
| `sqlite_get_schema` | `get_schema()` | ⭐⭐⭐ | 获取 SQLite 表结构 |
| `sqlite_query` | `query()` | ⭐⭐⭐ | 执行 SQLite 查询 |

**总计**: 12 个工具（8 个核心 ⭐⭐⭐，4 个辅助 ⭐⭐）。**当前已实现 7 个**：`excel_inspect_file`、`excel_read_sheet`、`pdf_extract_text`、`word_read_document`、`sqlite_inspect_database`、`sqlite_get_schema`、`sqlite_query`；未实现：`excel_inspect_sheet`、`excel_write_data`、`pdf_extract_tables`、`word_write_document`、`sqlite_list_tables`。

## 5. 实现计划 (Implementation Plan)

> **详细开发计划**: 请参考 [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md)

### 5.1 开发阶段概览

#### 阶段 1: 项目初始化（1-2 天）
- 创建项目结构
- 配置开发环境（虚拟环境、依赖管理）
- 安装并测试 `unifiles` 库的基本功能
- 创建 `main.py` 基础框架
- 配置测试环境

#### 阶段 2: Excel 核心工具（2-3 天）
- 实现 `excel_inspect_file` 工具（核心 ⭐⭐⭐）
- 实现 `excel_read_sheet` 工具（核心 ⭐⭐⭐）
- 编写单元测试

#### 阶段 3: PDF 核心工具（1-2 天）
- 实现 `pdf_extract_text` 工具（核心 ⭐⭐⭐）
- 编写单元测试

#### 阶段 4: Word 核心工具（1 天）
- 实现 `word_read_document` 工具（核心 ⭐⭐⭐）
- 编写单元测试

#### 阶段 5: SQLite 核心工具（2-3 天）
- 实现 `sqlite_inspect_database` 工具（核心 ⭐⭐⭐）
- 实现 `sqlite_get_schema` 工具（核心 ⭐⭐⭐）
- 实现 `sqlite_query` 工具（核心 ⭐⭐⭐）
- 编写单元测试

#### 阶段 6: 集成测试与文档（1-2 天）
- 编写端到端测试
- 编写用户文档和 API 文档
- 代码审查和重构
- 发布准备

### 5.2 里程碑
- **M1**: 项目框架搭建完成（阶段 1 结束，第 2 天）
- **M2**: Excel 核心工具完成（阶段 2 结束，第 5 天）
- **M3**: PDF 和 Word 核心工具完成（阶段 3-4 结束，第 8 天）
- **M4**: SQLite 核心工具完成（阶段 5 结束，第 11 天）
- **M5**: v0.1.0 发布就绪（阶段 6 结束，第 13 天）

### 5.3 优先级说明
- **⭐⭐⭐ 核心工具**（8 个）：优先实现，覆盖主要使用场景
  - Excel: `excel_inspect_file`, `excel_read_sheet`
  - PDF: `pdf_extract_text`
  - Word: `word_read_document`
  - SQLite: `sqlite_inspect_database`, `sqlite_get_schema`, `sqlite_query`
- **⭐⭐ 辅助工具**（4 个）：v0.2.0 实现，提供更细粒度的控制
  - Excel: `excel_inspect_sheet`, `excel_write_data`
  - PDF: `pdf_extract_tables`
  - Word: `word_write_document`
  - SQLite: `sqlite_list_tables`

### 5.4 时间线总览

| 阶段 | 任务 | 预计时间 | 累计时间 |
|:---|:---|:---:|:---:|
| 阶段 1 | 项目初始化 | 1-2 天 | 2 天 |
| 阶段 2 | Excel 核心工具 | 2-3 天 | 5 天 |
| 阶段 3 | PDF 核心工具 | 1-2 天 | 7 天 |
| 阶段 4 | Word 核心工具 | 1 天 | 8 天 |
| 阶段 5 | SQLite 核心工具 | 2-3 天 | 11 天 |
| 阶段 6 | 集成测试与文档 | 1-2 天 | 13 天 |
| **总计** | **8 个核心工具** | **8-13 天** | **13 天** |

## 6. 测试策略 (Testing Strategy)

### 6.1 测试类型
- **单元测试**: 测试每个工具函数的独立功能
- **集成测试**: 测试工具与 `unifiles` 库的集成
- **端到端测试**: 测试完整的 MCP 服务器流程

### 6.2 测试覆盖范围
- **功能测试**: 所有工具的基本功能
- **边界测试**: 异常路径、无效输入、文件不存在等
- **性能测试**: 大文件处理、批量操作性能
- **兼容性测试**: 不同文件格式、不同操作系统路径
- **DataFrame 转换测试**: 确保 DataFrame 正确转换为 JSON

### 6.3 测试工具
- `pytest`: 测试框架
- `pytest-asyncio`: 异步测试支持
- `pytest-cov`: 代码覆盖率
- `tempfile`: 临时文件创建（测试用）

## 7. 依赖管理 (Dependencies)

### 7.1 核心依赖
```txt
unifiles>=0.3.1
pydantic>=2.0.0
mcp[cli]>=1.26.0,<2.0.0
```

**注意**: 使用 MCP Python 官方 SDK（`mcp` 包），通过 `from mcp.server.fastmcp import FastMCP, Context` 使用 FastMCP 高级接口。

**注意**: `unifiles` 会自动安装以下依赖：
- `pandas` - 数据处理
- `openpyxl` - Excel 处理
- `pypdf` - PDF 处理
- `python-docx` - Word 处理

### 7.2 开发依赖
```txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
ruff>=0.1.0
mypy>=1.0.0
```

## 8. 配置管理 (Configuration)

### 8.1 服务器配置（当前实现）
- **服务器名称**: `unifiles-mcp`（在 `main.py` 中硬编码）
- **版本**: 见 `pyproject.toml` 与 `__init__.py`
- **配置模块**: 已移除 `config.py`，无运行时配置加载

### 8.2 文件操作配置
- **默认编码**: UTF-8
- **路径处理**: 支持相对路径和绝对路径；`validators.validate_file_path` 做存在性与路径遍历检查（禁止 `..`）
- **安全限制**: 仅路径遍历防护，无路径白名单（原 `allowed_paths` 已随 config 移除）
- **DataFrame 转换**: NaN 值处理为 None

## 9. 错误处理 (Error Handling)

### 9.1 错误类型
- **文件不存在**: `FileNotFoundError` → 转换为友好的错误信息
- **权限不足**: `PermissionError` → 转换为友好的错误信息
- **格式不支持**: `FileFormatError` → 转换为友好的错误信息
- **读取错误**: `FileReadError` → 转换为友好的错误信息
- **写入错误**: `FileWriteError` → 转换为友好的错误信息
- **SQL 错误**: `sqlite3.Error` → 转换为友好的错误信息

### 9.2 错误处理策略
- **捕获异常**: 使用 `try/except` 捕获所有可能的异常
- **日志记录**: 通过 `ctx.error()` 记录详细错误信息
- **友好提示**: 返回人类可读的错误信息给 AI 助手
- **异常转换**: 将 `unifiles` 的异常转换为友好的错误消息

## 10. 性能要求 (Performance Requirements)

### 10.1 响应时间
- **小文件（<1MB）**: <200ms
- **中等文件（1-10MB）**: <1s
- **大文件（>10MB）**: <5s（或提供流式处理）

### 10.2 并发处理
- 支持异步并发处理多个文件操作请求
- 使用 `asyncio.to_thread()` 实现非阻塞 I/O

### 10.3 资源限制
- 内存使用：合理控制大文件的内存占用
- 文件大小限制：可配置的最大文件大小限制
- DataFrame 大小：大 DataFrame 的 JSON 序列化优化

## 11. 安全考虑 (Security Considerations)

### 11.1 路径安全
- **路径验证**: 防止路径遍历攻击（`../` 等）
- **权限检查**: 验证文件访问权限
- **沙箱模式**: 可选的路径限制（仅允许特定目录）

### 11.2 数据安全
- **敏感信息**: 避免在日志中记录敏感文件内容
- **SQL 注入**: SQLite 查询使用参数化查询
- **临时文件**: 安全清理临时文件

## 12. 文档要求 (Documentation Requirements)

### 12.1 用户文档
- **README.md**: 项目介绍、安装说明、快速开始
- **使用示例**: 常见使用场景的代码示例
- **API 文档**: 所有工具、资源、提示的详细说明

### 12.2 开发文档
- **AGENTS.md**: AI Agent 开发规范（已存在）
- **TRD.md**: 技术需求文档（本文档）
- **架构文档**: 系统架构和设计决策说明

## 13. 发布计划 (Release Plan)

### 13.1 版本规划
- **v0.1.0**: 核心工具（8 个 ⭐⭐⭐）
  - Excel: `excel_inspect_file`, `excel_read_sheet`
  - PDF: `pdf_extract_text`
  - Word: `word_read_document`
  - SQLite: `sqlite_inspect_database`, `sqlite_get_schema`, `sqlite_query`
- **v0.2.0**: 辅助工具（4 个 ⭐⭐）
  - Excel: `excel_inspect_sheet`, `excel_write_data`
  - PDF: `pdf_extract_tables`
  - Word: `word_write_document`
  - SQLite: `sqlite_list_tables`
- **v0.3.0**: Resources 和 Prompts
- **v1.0.0**: 正式发布（功能完整、测试充分）

### 13.2 发布检查清单
- [ ] 所有测试通过
- [ ] 代码覆盖率 >80%
- [ ] 文档完整
- [ ] 版本号更新
- [ ] CHANGELOG 更新
- [ ] PyPI 发布准备

## 14. 后续扩展 (Future Enhancements)

### 14.1 功能扩展
- 支持更多文件格式（CSV、JSON、YAML 等）
- 文件搜索和过滤功能
- 文件内容验证和校验
- 文件操作历史记录
- 批量操作优化

### 14.2 性能优化
- 大文件流式处理
- 缓存机制
- 并行处理优化
- DataFrame 序列化优化

## 15. 风险评估 (Risk Assessment)

### 15.1 技术风险
- **风险**: `unifiles` 库的 API 可能发生变化
- **缓解**: 锁定依赖版本，编写兼容性测试

### 15.2 性能风险
- **风险**: 大文件处理可能导致内存溢出
- **缓解**: 实现流式处理，设置文件大小限制

### 15.3 安全风险
- **风险**: 路径遍历攻击、SQL 注入
- **缓解**: 严格的路径验证和参数化查询

### 15.4 数据转换风险
- **风险**: DataFrame 转 JSON 时可能丢失精度或类型信息
- **缓解**: 完善的类型转换和 NaN 值处理

## 16. 附录 (Appendix)

### 16.1 参考资源
- [MCP Python SDK 官方文档](https://pypi.org/project/mcp/)
- [MCP Python SDK API 参考](https://modelcontextprotocol.github.io/python-sdk/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [unifiles GitHub 仓库](https://github.com/Asheng008/unifiles)
- [unifiles PyPI 页面](https://pypi.org/project/unifiles/)
- [Pydantic V2 文档](https://docs.pydantic.dev/)

### 16.2 术语表
- **MCP**: Model Context Protocol，模型上下文协议
- **Tool**: MCP 中的工具，可被 AI 助手调用的函数
- **Resource**: MCP 中的资源，可被 AI 助手访问的数据源
- **Prompt**: MCP 中的提示模板，用于指导 AI 助手的行为

### 16.3 unifiles 库限制说明
- **同步 API**: `unifiles` 库的所有函数都是同步的，需要在异步环境中使用 `asyncio.to_thread()` 包装
- **文件覆盖**: `write_excel` 和 `write_docx` 会覆盖整个目标文件
- **错误处理**: `unifiles` 库有完善的异常体系，需要在 MCP 层进行友好转换
- **PDF 限制**: PDF 表格提取仅支持基础表格，复杂布局可能识别不准
- **DataFrame 转换**: 所有 DataFrame 需要转换为 JSON 格式，注意 NaN 值处理
- **API 精简**: 不暴露 `get_sheet_names` 和 `get_column_names`，因为 `get_excel_info` 已涵盖其功能

### 16.4 unifiles 实际 API 详细说明

#### 16.4.1 Excel 模块

```python
# 获取 Excel 文件信息（核心工具）
unifiles.get_excel_info(
    file_path: str,
    include_preview: bool = False,
    preview_rows: int = 3
) -> dict[str, Any]
# MCP 映射: excel_inspect_file ⭐⭐⭐

# 获取工作表信息
unifiles.get_sheet_info(
    file_path: str,
    sheet_name: str | int | None = None,
    preview_rows: int = 5
) -> dict[str, Any]
# MCP 映射: excel_inspect_sheet ⭐⭐

# 读取 Excel
unifiles.read_excel(file_path: str, sheet_name: str | int | None = None) -> pd.DataFrame
# MCP 映射: excel_read_sheet ⭐⭐⭐

# 写入 Excel
unifiles.write_excel(
    data: pd.DataFrame | dict[str, pd.DataFrame], 
    file_path: str, 
    sheet_name: str = "Sheet1"
) -> None
# MCP 映射: excel_write_data ⭐⭐

# 注意：以下函数不暴露为 MCP 工具（功能已由 get_excel_info 涵盖）
# unifiles.get_sheet_names(file_path: str) -> list[str]
# unifiles.get_column_names(...) -> list[str] | dict[int, list[str]]
```

#### 16.4.2 PDF 模块

```python
# 提取文本（核心工具）
unifiles.extract_text(
    file_path: str, 
    page_range: tuple[int, int] | None = None
) -> str
# MCP 映射: pdf_extract_text ⭐⭐⭐
# page_range: (start, end) 元组，1-based，例如 (1, 5) 表示第 1 到第 5 页

# 提取表格
unifiles.extract_tables(
    file_path: str, 
    page_range: tuple[int, int] | None = None
) -> list[pd.DataFrame]
# MCP 映射: pdf_extract_tables ⭐⭐
# page_range: (start, end) 元组，1-based
```

#### 16.4.3 Word 模块

```python
# 读取 Word（核心工具）
unifiles.read_docx(file_path: str) -> str
# MCP 映射: word_read_document ⭐⭐⭐

# 写入 Word
unifiles.write_docx(
    content: str, 
    file_path: str, 
    title: str | None = None
) -> None
# MCP 映射: word_write_document ⭐⭐
```

#### 16.4.4 SQLite 模块

```python
# 获取数据库信息（核心工具）
unifiles.get_database_info(
    db_path: str,
    include_preview: bool = False,
    preview_rows: int = 3
) -> dict[str, Any]
# MCP 映射: sqlite_inspect_database ⭐⭐⭐

# 获取表名列表
unifiles.get_tables(db_path: str) -> list[str]
# MCP 映射: sqlite_list_tables ⭐⭐

# 获取表结构（核心工具）
unifiles.get_schema(db_path: str, table_name: str) -> dict[str, str]
# MCP 映射: sqlite_get_schema ⭐⭐⭐

# 执行查询（核心工具）
unifiles.query(
    db_path: str, 
    sql: str, 
    params: tuple | dict | None = None
) -> pd.DataFrame
# MCP 映射: sqlite_query ⭐⭐⭐
# params: tuple 用于 ? 占位符，dict 用于 :name 占位符
```

#### 16.4.5 异常类

```python
unifiles.UnifilesError          # 基础异常
unifiles.FileFormatError         # 文件格式错误
unifiles.FileReadError           # 文件读取错误
unifiles.FileWriteError          # 文件写入错误
```

#### 16.4.6 支持的文件格式

| 格式 | 扩展名 | 读取 | 写入 | 说明 |
|------|--------|------|------|------|
| Excel | .xlsx, .xls | ✅ | ✅ | 支持多工作表 |
| PDF | .pdf | ✅ | ❌ | 文本和表格提取 |
| Word | .docx | ✅ | ✅ | 仅支持 .docx |
| SQLite | .db, .sqlite | ✅ | ✅ | 数据库查询 |

---

**文档维护**: 本文档应随项目进展持续更新，重大变更需记录版本历史。

**最后更新**: 2026-02-07 - 与当前代码同步：项目结构（无 config/resources/prompts/tests）、平铺参数、已实现 7 工具、配置为硬编码
