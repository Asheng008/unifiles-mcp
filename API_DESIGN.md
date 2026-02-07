这是一个非常典型的**“库封装”**场景。你已经有了一个功能完善的底层库 `unifiles`，现在的任务是为它穿上一层“MCP 外衣”，让 LLM 能够舒服地使用它。

基于 `unifiles` 现有的函数签名，我建议采用 **“前缀分类法”** 来命名工具，并充分利用你现有的 `get_..._info` 类函数作为“探索工具”。

以下是针对 `unifiles` 项目结构的 MCP 工具设计方案：

### 设计原则
1.  **保留原生能力**：`unifiles` 已经封装得很好了，MCP 层应尽量直接映射，不做过多业务逻辑。
2.  **前缀命名**：使用 `excel_*`, `sqlite_*`, `pdf_*` 作为工具名前缀，防止命名冲突（例如 `read_excel` 和 `read_docx` 区分清晰）。
3.  **优先使用 Info 函数**：你代码里的 `get_excel_info` 是 LLM 的神器，应该作为核心工具暴露。

---

### 1. SQLite 模块 (`sqlite.py`)

SQLite 的交互逻辑是：先看表结构，再查数据。

| MCP 工具名 | 对应 `unifiles` 函数 | 推荐参数设计 | 设计理由 |
| :--- | :--- | :--- | :--- |
| **`sqlite_list_tables`** | `get_tables(db_path)` | `db_path` | 入口工具，快速了解数据库概貌。 |
| **`sqlite_get_schema`** | `get_schema(db_path, table_name)` | `db_path`, `table_name` | **核心工具**。LLM 写 SQL 前必须看 Schema。 |
| **`sqlite_query`** | `query(db_path, sql, params)` | `db_path`, `sql` | **执行工具**。注意：MCP 层可以将 `params` 设为可选，或者让 LLM 直接把参数拼在 SQL 里（如果是只读查询，风险可控）。 |

### 2. Excel 模块 (`excel.py`)

Excel 的难点在于文件可能很大。你代码里的 `get_excel_info` 非常棒，它聚合了 Sheet 名和预览，这正是 MCP 最需要的。

| MCP 工具名 | 对应 `unifiles` 函数 | 推荐参数设计 | 设计理由 |
| :--- | :--- | :--- | :--- |
| **`excel_inspect_file`** | `get_excel_info(...)` | `file_path`, `preview_rows=3` | **上帝视角工具**。一次调用就能知道有哪些 Sheet，以及每张表长什么样。这比单独调 `get_sheet_names` 高效得多。 |
| **`excel_read_sheet`** | `read_excel(...)` | `file_path`, `sheet_name` | **读取工具**。用于读取完整数据。注意：如果数据量大，需要在 MCP 层做截断保护。 |
| **`excel_write_data`** | `write_excel(...)` | `file_path`, `sheet_name`, `data` | **写入工具**。*（可选）* 如果你需要让 LLM 修改文件，暴露此接口。`data` 需要定义为 JSON 列表结构。 |

*注：`get_sheet_names` 和 `get_column_names` 可以不暴露，因为 `get_excel_info` 已经涵盖了它们的功能，减少 LLM 的选择困难。*

### 3. PDF 模块 (`pdf.py`)

PDF 通常是只读的，且分为文本和表格两种形态。

| MCP 工具名 | 对应 `unifiles` 函数 | 推荐参数设计 | 设计理由 |
| :--- | :--- | :--- | :--- |
| **`pdf_extract_text`** | `extract_text(...)` | `file_path`, `page_range` | **通用读取**。`page_range` 是关键，允许 LLM 按需读取（如 "1-5"）。 |
| **`pdf_extract_tables`** | `extract_tables(...)` | `file_path`, `page_range` | **专用读取**。当 LLM 发现 PDF 里有数据表时，引导它用这个工具，而不是用 OCR 或文本解析。 |

### 4. Word 模块 (`word.py`)

Word 相对简单，通常作为纯文本处理。

| MCP 工具名 | 对应 `unifiles` 函数 | 推荐参数设计 | 设计理由 |
| :--- | :--- | :--- | :--- |
| **`word_read_document`** | `read_docx(...)` | `file_path` | 简单直接。 |
| **`word_write_document`** | `write_docx(...)` | `file_path`, `content`, `title` | *（可选）* 用于生成报告或文档。 |

---

### MCP Python 官方 SDK 实现代码示例

假设你已经安装了 `unifiles` 和 `mcp[cli]` 包，以下是如何编写 `server.py` 的示例（使用 MCP Python 官方 SDK 的 FastMCP 高级接口）：

```python
from mcp.server.fastmcp import FastMCP
from unifiles import excel, sqlite, pdf, word
# 假设 unifiles 抛出的异常都在 exceptions 模块中
from unifiles.exceptions import UnifilesError 

mcp = FastMCP("Unifiles Server")

# --- SQLite Tools ---

@mcp.tool()
def sqlite_list_tables(db_path: str) -> list[str]:
    """列出 SQLite 数据库中的所有表名。"""
    return sqlite.get_tables(db_path)

@mcp.tool()
def sqlite_get_schema(db_path: str, table_name: str) -> str:
    """获取指定表的 CREATE TABLE 语句（Schema）。"""
    return sqlite.get_schema(db_path, table_name)

@mcp.tool()
def sqlite_query(db_path: str, sql: str) -> list[dict]:
    """
    执行 SQL 查询。
    注意：仅允许执行 SELECT 查询。
    """
    # 简单的安全过滤
    if "select" not in sql.lower():
        raise ValueError("仅支持 SELECT 查询")
    
    # 假设 query 返回的是 list[dict] 或类似结构
    return sqlite.query(db_path, sql, params=None)

# --- Excel Tools ---

@mcp.tool()
def excel_inspect_file(file_path: str) -> dict:
    """
    检查 Excel 文件结构。
    返回包含所有 Sheet 名称、列头和前几行数据预览的摘要信息。
    在决定读取哪个 Sheet 之前，请先使用此工具。
    """
    # 直接利用你现有的强大函数
    return excel.get_excel_info(file_path, include_preview=True, preview_rows=3)

@mcp.tool()
def excel_read_sheet(file_path: str, sheet_name: str) -> list[dict]:
    """读取指定 Sheet 的全部数据。"""
    try:
        return excel.read_excel(file_path, sheet_name)
    except UnifilesError as e:
        return f"读取失败: {str(e)}"

# --- PDF Tools ---

@mcp.tool()
def pdf_read_text(file_path: str, page_range: str = "all") -> str:
    """
    提取 PDF 文本。
    Args:
        page_range: 页码范围，例如 "1", "1-5", "all"。
    """
    return pdf.extract_text(file_path, page_range)

# --- Word Tools ---

@mcp.tool()
def word_read_document(file_path: str) -> str:
    """读取 Word (.docx) 文档的全部文本内容。"""
    return word.read_docx(file_path)

if __name__ == "__main__":
    mcp.run()
```

### 关键点总结

1.  **利用现有资产**：你的 `get_excel_info` 是一个非常符合 MCP 理念（Context-Aware）的函数，直接映射它比拆分成多个小函数更好。
2.  **错误处理**：虽然代码里没细写，但建议在工具内部捕获 `unifiles.exceptions.UnifilesError`，并返回友好的字符串错误信息，而不是让服务器崩溃。
3.  **参数简化**：例如 `sqlite.query` 原本有 `params`，但在 MCP 中，让 LLM 自己拼接 SQL 字符串通常更稳定（除非你有严格的防注入需求，但在本地工具场景下，灵活性优先）。
