# 更新 CHANGELOG.md 文档

根据当前对话中的变更，更新 `CHANGELOG.md` 文件，记录版本变更。

## 目标

- 更新 `CHANGELOG.md` 文件，记录当前版本的变更
- 遵循 [Keep a Changelog](https://keepachangelog.com/) 格式
- 使用 [Semantic Versioning](https://semver.org/) 版本号
- 将变更归类到合适的类别（Added, Changed, Deprecated, Removed, Fixed, Security）

## 必做步骤

0. **若 CHANGELOG.md 不存在则创建**
   - 若项目根目录下不存在 `CHANGELOG.md`，则先创建该文件
   - 写入标准格式：标题、说明、`[Unreleased]` 部分（位于最前面，所有版本之前）
   - 创建完成后，再执行下面的步骤

1. **读取当前 CHANGELOG.md 和版本信息**
   - 读取 `CHANGELOG.md` 查看现有格式和最新版本
   - 读取 `pyproject.toml` 获取当前版本号（`version` 字段）
   - 读取 `src/unifiles_mcp/__init__.py` 确认版本号（如有）

2. **分析当前对话的变更**
   - 回顾整个对话历史，识别所有变更：
     - **Added**: 新增功能、工具、文件
     - **Changed**: 修改现有功能、API 变更、重构
     - **Deprecated**: 标记为废弃的功能
     - **Removed**: 删除的功能、文件
     - **Fixed**: Bug 修复
     - **Security**: 安全相关改进
   - 按类别组织变更项

3. **确定版本号**
   - 如果当前版本在 CHANGELOG 中已存在，更新该版本条目
   - 如果当前版本不存在，创建新版本条目
   - 版本号格式：`## [版本号] - YYYY-MM-DD`
   - 日期使用当前日期（格式：YYYY-MM-DD）

4. **更新 CHANGELOG**
   - 如果当前版本已存在，在该版本下添加/更新变更项
   - 如果当前版本不存在：
     - 在 `[Unreleased]` **之后**插入新版本条目（`[Unreleased]` 应位于所有版本之前）
     - 保持 `[Unreleased]` 在最前面（标题和说明之后，所有版本之前）
   - 每个变更项使用列表项（`-`），按模块或功能分组
   - 变更描述要清晰、具体，说明做了什么

5. **更新 [Unreleased] 部分（如需要）**
   - 如果对话中有计划但未实现的功能，更新 `[Unreleased]` 的 `Planned` 部分
   - 移除已实现的功能

## 格式要求

- **版本标题**: `## [版本号] - YYYY-MM-DD`
- **分类标题**: `### Added`, `### Changed`, `### Fixed` 等（三级标题）
- **变更项**: 使用列表项 `-`，可以嵌套子项（用 2 个空格缩进）
- **工具描述**: 按模块分组（Excel 工具、PDF 工具、Word 工具、SQLite 工具、基础设施等）
- **变更描述**: 简洁明了，说明具体做了什么

## 变更分类指南

- **Added**: 新增功能、新工具、新文件、新依赖
- **Changed**: API 变更、参数格式变更、重构、配置变更
- **Removed**: 删除的功能、删除的文件、移除的依赖
- **Fixed**: Bug 修复、错误处理改进
- **Security**: 安全加固、漏洞修复、权限控制

## 示例格式

```markdown
## [0.1.2] - 2026-02-07

### Changed
- 工具参数改为平铺参数，不再使用 Pydantic BaseModel
  - 所有工具使用 `Annotated[T, Field(description=...)]` 定义参数
  - 校验在函数内部通过 `validators` 完成

### Removed
- 删除 `config.py` 配置模块
  - 服务器名称改为硬编码 `"unifiles-mcp"`
  - 移除路径白名单功能（`allowed_paths`）

### Fixed
- 修复参数顺序错误：无默认值参数必须位于有默认值参数之前
  - `pdf_extract_text`: 将 `ctx` 移到 `page_range` 前
  - `sqlite_inspect_database`: 将 `ctx` 移到可选参数前
  - `sqlite_query`: 将 `ctx` 移到 `params` 前

### Changed
- 更新文档以反映当前实现状态
  - `TRD.md`: 更新项目结构、参数设计、实现状态
  - `docs/API.md`: 示例改为平铺参数调用
  - `README.md`: 版本号、项目结构、开发命令更新
```

## 输出

- 直接修改并保存 `CHANGELOG.md`
- 新版本条目插入在 `[Unreleased]` **之后**（`[Unreleased]` 位于最前面，所有版本之前）
- 保持 `[Unreleased]` 在最前面（标题和说明之后，第一个版本之前）
- 确保格式与现有内容一致
- 变更项按模块分组，描述清晰具体

## 注意事项

- 版本号必须与 `pyproject.toml` 中的 `version` 一致
- 日期使用当前日期（YYYY-MM-DD 格式）
- 变更描述要具体，避免过于笼统
- 如果变更涉及多个类别，可以同时出现在多个分类下
- 保持中文描述，与项目文档风格一致
