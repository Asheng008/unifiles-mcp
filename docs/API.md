# API 文档

> **版本**: v0.1.2  
> **日期**: 2026-02-07

本文档详细说明 unifiles-mcp 提供的所有 MCP 工具。所有工具均使用**平铺参数**（每个参数独立传入），由 MCP 客户端按参数名传参。

---

## 目录

- [工具列表](#工具列表)
  - [Excel 工具](#excel-工具)
    - [`excel_inspect_file`](#excel_inspect_file)
    - [`excel_read_sheet`](#excel_read_sheet)
  - [PDF 工具](#pdf-工具)
    - [`pdf_extract_text`](#pdf_extract_text)
  - [Word 工具](#word-工具)
    - [`word_read_document`](#word_read_document)
  - [SQLite 工具](#sqlite-工具)
    - [`sqlite_inspect_database`](#sqlite_inspect_database)
    - [`sqlite_get_schema`](#sqlite_get_schema)
    - [`sqlite_query`](#sqlite_query)
- [通用工具](#通用工具)
  - [`ping`](#ping)
- [错误处理](#错误处理)
- [数据类型说明](#数据类型说明)
- [最佳实践](#最佳实践)

---

## 工具列表

### Excel 工具

#### `excel_inspect_file`

检查 Excel 文件结构（"上帝视角"工具）。一次调用就能知道有哪些 Sheet，以及每张表长什么样。

**参数**:
- `file_path` (str): Excel 文件路径（支持相对路径和绝对路径）
- `include_preview` (bool, 可选): 是否包含数据预览（默认 False）
- `preview_rows` (int, 可选): 如果 include_preview=True，每个工作表预览的行数（默认 3）

**返回**: `dict[str, Any]`
```json
{
  "file_path": "data.xlsx",
  "file_size": 12345,
  "sheet_count": 2,
  "sheet_names": ["Sheet1", "Sheet2"],
  "sheets": [
    {
      "sheet_name": "Sheet1",
      "row_count": 100,
      "column_count": 5,
      "column_names": ["姓名", "年龄", "城市"],
      "preview": [...]  // 仅当 include_preview=True 时包含
    }
  ]
}
```

**示例**:
```python
result = await excel_inspect_file(
    file_path="data.xlsx",
    include_preview=True,
    preview_rows=5,
)
```

---

#### `excel_read_sheet`

读取 Excel 工作表内容并返回 JSON 格式的数据。

**参数**:
- `file_path` (str): Excel 文件路径
- `sheet_name` (str | int | None, 可选): 工作表名称或索引，None 表示读取第一个工作表

**返回**: `str` (JSON 格式)
```json
[
  {"姓名": "张三", "年龄": 25, "城市": "北京"},
  {"姓名": "李四", "年龄": 30, "城市": "上海"}
]
```

**示例**:
```python
# 读取指定工作表
result = await excel_read_sheet(
    file_path="data.xlsx",
    sheet_name="Sheet1",
)

# 读取第一个工作表
result = await excel_read_sheet(
    file_path="data.xlsx",
    sheet_name=None,
)
```

---

### PDF 工具

#### `pdf_extract_text`

从 PDF 文件中提取文本内容。

**参数**:
- `file_path` (str): PDF 文件路径
- `page_range` (tuple[int, int] | list[int] | None, 可选): 页码范围 (start, end)，1-based（从 1 开始），None 表示提取所有页面；JSON 可能传 `[1, 5]`，内部会转为 tuple

**返回**: `str` (提取的文本内容，页面之间用换行符分隔)

**示例**:
```python
# 提取所有页面
result = await pdf_extract_text(file_path="document.pdf")

# 提取第 1 到第 5 页
result = await pdf_extract_text(
    file_path="document.pdf",
    page_range=(1, 5),
)
```

---

### Word 工具

#### `word_read_document`

读取 Word 文档内容。

**参数**:
- `file_path` (str): Word 文档路径（仅支持 .docx 格式）

**返回**: `str` (文档的文本内容，段落之间用换行符分隔)

**示例**:
```python
result = await word_read_document(file_path="document.docx")
```

---

### SQLite 工具

#### `sqlite_inspect_database`

检查 SQLite 数据库（"上帝视角"工具）。一次调用获取数据库全貌。

**参数**:
- `db_path` (str): SQLite 数据库文件路径
- `include_preview` (bool, 可选): 是否包含数据预览（默认 False）
- `preview_rows` (int, 可选): 如果 include_preview=True，每个表预览的行数（默认 3）

**返回**: `dict[str, Any]`
```json
{
  "db_path": "database.db",
  "file_size": 12345,
  "table_count": 2,
  "table_names": ["users", "products"],
  "tables": [
    {
      "table_name": "users",
      "row_count": 100,
      "column_count": 3,
      "column_names": ["id", "name", "age"],
      "column_types": {"id": "INTEGER", "name": "TEXT", "age": "INTEGER"},
      "preview": [...]  // 仅当 include_preview=True 时包含
    }
  ]
}
```

**示例**:
```python
result = await sqlite_inspect_database(
    db_path="database.db",
    include_preview=True,
)
```

---

#### `sqlite_get_schema`

获取表结构（字段名到字段类型的映射）。LLM 写 SQL 前必须看 Schema。

**参数**:
- `db_path` (str): SQLite 数据库文件路径
- `table_name` (str): 表名

**返回**: `dict[str, str]` (字段名到类型的映射)
```json
{
  "id": "INTEGER",
  "name": "TEXT",
  "age": "INTEGER"
}
```

**示例**:
```python
result = await sqlite_get_schema(
    db_path="database.db",
    table_name="users",
)
```

---

#### `sqlite_query`

执行 SQL 查询并返回 JSON 格式的数据。仅支持 SELECT 查询。

**参数**:
- `db_path` (str): SQLite 数据库文件路径
- `sql` (str): SQL 查询语句（仅支持 SELECT）
- `params` (dict | list | None, 可选): 查询参数
  - dict: 用于 `:name` 占位符，例如 `{"age": 18}`
  - list: 用于 `?` 占位符，例如 `[18]`

**返回**: `str` (JSON 格式的查询结果)
```json
[
  {"id": 1, "name": "张三", "age": 25},
  {"id": 2, "name": "李四", "age": 30}
]
```

**示例**:
```python
# 简单查询
result = await sqlite_query(
    db_path="database.db",
    sql="SELECT * FROM users",
)

# 使用 dict 参数化查询
result = await sqlite_query(
    db_path="database.db",
    sql="SELECT * FROM users WHERE age > :age",
    params={"age": 18},
)

# 使用 list 参数化查询
result = await sqlite_query(
    db_path="database.db",
    sql="SELECT * FROM users WHERE age > ?",
    params=[18],
)
```

**安全说明**:
- 仅允许 SELECT 查询，不允许 INSERT、UPDATE、DELETE 等修改操作
- 支持参数化查询，防止 SQL 注入

---

## 通用工具

#### `ping`

健康检查端点。返回 'pong' 如果服务器正在运行。

**参数**: 无

**返回**: `str` ("pong")

**示例**:
```python
result = await ping()
# 返回: "pong"
```

---

## 错误处理

所有工具在遇到错误时会抛出 `ValueError` 异常，并包含友好的错误消息：

- **文件不存在**: `ValueError("文件不存在: <file_path>")`
- **数据库不存在**: `ValueError("数据库文件不存在: <db_path>")`
- **表不存在**: `ValueError("获取表结构失败: 表不存在: <table_name>")`
- **SQL 错误**: `ValueError("查询失败: <error_message>")`
- **SQL 安全检查失败**: `ValueError("仅支持 SELECT 查询，不允许修改数据")`

---

## 数据类型说明

### JSON 格式

所有返回 JSON 的工具都遵循以下规范：
- DataFrame 转换为字典列表（`to_dict("records")`）
- NaN/NULL 值转换为 `null`（Python 中的 `None`）
- 使用 UTF-8 编码，支持中文

### 页面范围

PDF 工具的 `page_range` 参数：
- 格式: `tuple[int, int]` 或 `list[int]`（JSON 传入时多为 list，内部会转换）
- 1-based（从 1 开始，不是 0）
- 例如: `(1, 5)` 或 `[1, 5]` 表示第 1 到第 5 页
- `None` 表示所有页面

### 工作表名称

Excel 工具的 `sheet_name` 参数：
- `str`: 工作表名称，例如 `"Sheet1"`
- `int`: 工作表索引（0-based），例如 `0` 表示第一个工作表
- `None`: 读取第一个工作表

---

## 最佳实践

1. **先检查，再读取**: 使用 `excel_inspect_file` 或 `sqlite_inspect_database` 了解文件/数据库结构，再决定读取哪些数据
2. **使用预览**: 对于大文件，先使用预览功能查看数据，避免一次性读取过多数据
3. **参数化查询**: 使用参数化查询防止 SQL 注入
4. **错误处理**: 所有工具都可能抛出异常，请妥善处理

---

**最后更新**: 2026-02-07 - 版本 v0.1.2，示例改为平铺参数调用
