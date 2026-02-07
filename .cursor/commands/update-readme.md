# 更新 README 文档 (Update README)

## Overview
根据项目当前状态自动更新 README.md 文档。包括版本号、工具列表、功能特性、项目结构等信息的同步更新。

## 更新内容

### 1. 版本信息
- 从 `pyproject.toml` 读取当前版本号
- 更新 README 中的版本引用（如 "核心工具（v0.1.0）"）

### 2. 工具列表
- 扫描 `src/unifiles_mcp/tools/` 目录下的所有 `@mcp.tool` 装饰器
- 更新 "核心工具" 部分，确保所有工具都已列出
- 工具按模块分组（Excel、PDF、Word、SQLite）

### 3. 功能特性
- 检查项目依赖和配置
- 确保功能特性描述准确

### 4. 项目结构
- 检查实际目录结构
- 更新项目结构树，确保与实际一致

### 5. 文档链接
- 检查文档文件是否存在
- 更新文档链接部分

## 执行步骤

1. **读取项目信息**
   - 读取 `pyproject.toml` 获取版本号
   - 扫描 `src/unifiles_mcp/tools/` 获取所有工具
   - 检查项目目录结构

2. **分析当前 README**
   - 读取现有 `README.md`
   - 识别需要更新的部分

3. **更新内容**
   - 更新版本号引用
   - 更新工具列表（确保所有工具都包含）
   - 更新项目结构（如需要）
   - 更新文档链接（如需要）

4. **保持格式**
   - 保持 Markdown 格式正确
   - 保持代码块格式
   - 保持中文注释和说明

## 工具列表模板

根据扫描结果，更新工具列表部分：

```markdown
## 核心工具（v{version}）

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
```

## 注意事项

1. **保持现有格式**
   - 不要改变 README 的整体结构
   - 保持中文说明和注释
   - 保持代码示例格式

2. **版本号同步**
   - 确保版本号与 `pyproject.toml` 一致
   - 更新所有版本引用

3. **工具完整性**
   - 确保所有已实现的工具都列出
   - 工具描述要准确

4. **文档链接**
   - 检查链接文件是否存在
   - 更新不存在的链接

## 执行命令

执行此命令时，AI 助手将：

1. 读取 `pyproject.toml` 获取版本号
2. 扫描 `src/unifiles_mcp/tools/` 目录获取所有工具
3. 读取当前 `README.md`
4. 更新版本号、工具列表等信息
5. 保存更新后的 `README.md`

## Checklist

更新完成后，确认：

- [ ] 版本号已更新（与 pyproject.toml 一致）
- [ ] 所有工具都已列出
- [ ] 工具描述准确
- [ ] 项目结构正确
- [ ] 文档链接有效
- [ ] Markdown 格式正确
- [ ] 中文说明完整
