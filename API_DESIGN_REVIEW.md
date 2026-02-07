# API 接口设计评价与改进建议

> **日期**: 2026-01-30  
> **评价对象**: unifiles-mcp API 设计方案

## 总体评价：⭐⭐⭐⭐ (4/5)

这是一个**优秀的设计方案**，体现了对 LLM 使用场景的深入理解。设计简洁、实用，但仍有改进空间。

---

## ✅ 优点分析

### 1. 前缀命名清晰
- ✅ `excel_*`, `sqlite_*`, `pdf_*`, `word_*` 避免命名冲突
- ✅ 模块归属一目了然
- ✅ 符合 MCP 工具命名最佳实践

### 2. 优先使用 Info 函数（核心亮点）
- ✅ `excel_inspect_file` 作为核心工具非常明智
- ✅ 一次调用获取文件全貌，减少 LLM 的调用次数
- ✅ 降低 token 消耗和响应延迟

### 3. 精简 API 暴露
- ✅ 不暴露 `get_sheet_names` 和 `get_column_names` 是明智的
- ✅ 避免 LLM 的选择困难症
- ✅ 符合"最小接口"原则

### 4. 考虑 LLM 使用场景
- ✅ SQLite 的"先看表结构再查数据"流程设计合理
- ✅ PDF 的 `page_range` 参数考虑了大文件场景

---

## ⚠️ 需要改进的地方

### 1. SQLite 模块缺少 `get_database_info`

**问题**: 
- 原设计只有 `sqlite_list_tables`, `sqlite_get_schema`, `sqlite_query`
- 缺少与 Excel 的 `excel_inspect_file` 对应的"上帝视角"工具

**建议**:
```python
sqlite_inspect_database(
    db_path: str,
    include_preview: bool = False,
    preview_rows: int = 3
) -> dict[str, Any]
```
- 对应 `unifiles.get_database_info()`
- 一次调用获取数据库全貌（表数量、每个表的结构、行数等）
- 与 `excel_inspect_file` 保持设计一致性

### 2. Excel 模块缺少 `get_sheet_info`

**问题**:
- 只有 `excel_inspect_file`（整个文件）和 `excel_read_sheet`（完整数据）
- 缺少查看单个工作表详情的中间粒度工具

**建议**:
```python
excel_inspect_sheet(
    file_path: str,
    sheet_name: str | int | None = None,
    preview_rows: int = 5
) -> dict[str, Any]
```
- 对应 `unifiles.get_sheet_info()`
- 用于查看单个工作表的详细信息（不需要读取全部数据）
- 适合"先看结构，再决定是否读取全部"的场景

### 3. 命名一致性可以优化

**当前命名**:
- `excel_read_sheet` ✅
- `word_read_document` ✅
- `sqlite_list_tables` ✅
- `pdf_extract_text` ✅

**建议统一为**: `{module}_{action}_{object}` 格式
- 所有命名已符合此格式，无需修改 ✅

### 4. 参数设计需要明确

#### 4.1 `page_range` 参数格式
**问题**: 文档说 `"1-5"`，但 `unifiles` API 实际是 `tuple[int, int]`

**建议**:
```python
# 方案 A: 支持字符串和元组两种格式
page_range: str | tuple[int, int] | None = None
# 字符串格式: "1-5" 或 "1,5"
# 元组格式: (1, 5)

# 方案 B: 仅支持元组（更简单，类型安全）
page_range: tuple[int, int] | None = None
```

#### 4.2 `data` 参数结构
**问题**: `excel_write_data` 的 `data` 参数需要明确 JSON 结构

**建议**:
```python
# 单个工作表
data: list[dict[str, Any]]  # [{"col1": "val1", "col2": "val2"}, ...]

# 多个工作表
data: dict[str, list[dict[str, Any]]]  # {"Sheet1": [...], "Sheet2": [...]}
```

---

## 📋 改进后的完整 API 设计

### SQLite 模块

| MCP 工具名 | 对应 `unifiles` 函数 | 参数 | 优先级 |
|:---|:---|:---|:---|
| **`sqlite_inspect_database`** | `get_database_info()` | `db_path`, `include_preview=False`, `preview_rows=3` | ⭐⭐⭐ **核心** |
| `sqlite_list_tables` | `get_tables()` | `db_path` | ⭐⭐ |
| `sqlite_get_schema` | `get_schema()` | `db_path`, `table_name` | ⭐⭐⭐ **核心** |
| `sqlite_query` | `query()` | `db_path`, `sql`, `params=None` | ⭐⭐⭐ **核心** |

### Excel 模块

| MCP 工具名 | 对应 `unifiles` 函数 | 参数 | 优先级 |
|:---|:---|:---|:---|
| **`excel_inspect_file`** | `get_excel_info()` | `file_path`, `include_preview=False`, `preview_rows=3` | ⭐⭐⭐ **核心** |
| `excel_inspect_sheet` | `get_sheet_info()` | `file_path`, `sheet_name`, `preview_rows=5` | ⭐⭐ |
| `excel_read_sheet` | `read_excel()` | `file_path`, `sheet_name` | ⭐⭐⭐ **核心** |
| `excel_write_data` | `write_excel()` | `file_path`, `sheet_name`, `data` | ⭐⭐ |

### PDF 模块

| MCP 工具名 | 对应 `unifiles` 函数 | 参数 | 优先级 |
|:---|:---|:---|:---|
| `pdf_extract_text` | `extract_text()` | `file_path`, `page_range=None` | ⭐⭐⭐ **核心** |
| `pdf_extract_tables` | `extract_tables()` | `file_path`, `page_range=None` | ⭐⭐ |

### Word 模块

| MCP 工具名 | 对应 `unifiles` 函数 | 参数 | 优先级 |
|:---|:---|:---|:---|
| `word_read_document` | `read_docx()` | `file_path` | ⭐⭐⭐ **核心** |
| `word_write_document` | `write_docx()` | `file_path`, `content`, `title=None` | ⭐⭐ |

---

## 🎯 设计原则总结

### 1. 分层设计
- **Inspect 层**: 快速了解文件/数据库结构（`*_inspect_*`）
- **Read 层**: 读取完整数据（`*_read_*`, `*_extract_*`）
- **Write 层**: 写入数据（`*_write_*`）

### 2. 粒度选择
- **文件级**: `excel_inspect_file`, `sqlite_inspect_database`
- **对象级**: `excel_inspect_sheet`, `sqlite_get_schema`
- **数据级**: `excel_read_sheet`, `sqlite_query`

### 3. LLM 友好
- ✅ 减少工具数量，避免选择困难
- ✅ 优先提供"上帝视角"工具
- ✅ 参数设计简单明了
- ✅ 返回值结构清晰（JSON）

---

## 📊 对比：原设计 vs 改进设计

| 模块 | 原设计工具数 | 改进设计工具数 | 变化 |
|:---|:---:|:---:|:---|
| SQLite | 3 | 4 | +1 (`sqlite_inspect_database`) |
| Excel | 3 | 4 | +1 (`excel_inspect_sheet`) |
| PDF | 2 | 2 | 无变化 |
| Word | 2 | 2 | 无变化 |
| **总计** | **10** | **12** | **+2** |

**结论**: 增加 2 个工具，但设计更加完整和一致。

---

## ✅ 最终建议

1. **采用改进后的设计**（12 个工具）
2. **明确参数格式**（特别是 `page_range` 和 `data`）
3. **保持命名一致性**（已符合 `{module}_{action}_{object}` 格式）
4. **优先实现核心工具**（标记为 ⭐⭐⭐ 的工具）

---

**评价人**: AI Assistant  
**日期**: 2026-01-30
