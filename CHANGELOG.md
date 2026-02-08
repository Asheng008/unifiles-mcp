# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).




## [Unreleased]
- （在开发下一个版本时，将改动先记录在这里；发布时再移动到对应版本小节）

---

## [0.1.3] - 2026-02-07

### Added
- 命令行入口：`[project.scripts]` 配置 `unifiles-mcp = "unifiles_mcp.main:run"`，安装后可直接执行 `unifiles-mcp`
- 发布脚本：`publish_pypi.bat`，支持 `publish_pypi.bat test`（TestPyPI）与无参数（正式 PyPI）
- PyPI 发布清单：`docs/PYPI_RELEASE_CHECKLIST.md`，含已就绪项、必做步骤、可选改进与快速发布命令
- Cursor 命令：`publish-to-pypi.md`，指导打包与上传到 TestPyPI/正式 PyPI
- 根目录 `LICENSE` 文件（MIT，Copyright unifiles-mcp contributors）

### Changed
- **pyproject.toml**：补充作者（Asheng）、`license-files`、classifiers（Topic）、`[project.urls]`；`license` 改为字符串 `"MIT"`、`dependencies` 移回 `[project]` 下以通过 build；移除与 PEP 639 冲突的 License classifier
- **README.md**：安装方式与 unifiles 对齐（开发/仅运行/锁文件/PyPI）；作者与维护者小节、许可证链接；快速开始补充 CLI 启动方式及正确包导入（`from unifiles_mcp.main import mcp`）；项目结构增加 LICENSE、publish_pypi.bat、docs/PYPI_RELEASE_CHECKLIST.md；文档链接增加 PyPI 发布清单、移除不存在的 CODE_REVIEW_REPORT.md
- **write-cursor-command SKILL**：已有命令列表与 `.cursor/commands/` 同步，新增 explain、publish-to-pypi、update-changelog 说明，补充「新增命令后建议同步更新本列表」

---

## [0.1.2] - 2026-02-07

### Fixed
- 修复参数顺序错误：无默认值参数必须位于有默认值参数之前
  - `pdf_extract_text`: 将 `ctx` 移到 `page_range` 前
  - `sqlite_inspect_database`: 将 `ctx` 移到可选参数前
  - `sqlite_query`: 将 `ctx` 移到 `params` 前
- 修复 mypy 类型检查问题
  - 为 `unifiles` 模块添加 `ignore_missing_imports` 配置
  - 使用 `cast()` 修复 no-any-return 和类型不匹配问题
  - 修复 `sqlite_query` 中参数类型转换问题

### Removed
- 删除 `config.py` 配置模块
  - 服务器名称改为硬编码 `"unifiles-mcp"`
  - 移除路径白名单功能（`allowed_paths`）
  - 简化配置管理，减少依赖

### Changed
- 更新文档以反映当前实现状态
  - `TRD.md`: 更新项目结构（移除 config/resources/prompts）、参数设计说明、实现状态（7/12 工具）
  - `docs/API.md`: 版本更新至 v0.1.2，示例改为平铺参数调用，补充 `page_range` 支持 list
  - `README.md`: 版本号更新、项目结构移除 config.py、开发命令去掉 tests/
  - `.cursor/commands/explain.md`: 更新文档引用（TECH_REQUIREMENTS.md → TRD.md）
- 更新 Cursor 命令文件
  - `fix-and-verify.md`: 移除 pytest 测试步骤（MCP 服务器暂不包含自动化测试）
  - `lint-and-format.md`: Ruff 和 Black 命令去掉 `tests/` 路径（项目当前无 tests 目录）
- 代码质量改进
  - 添加 `# noqa: E402` 注释处理延迟导入
  - Black 格式化所有工具文件
  - 完善类型注解和类型转换

### Added
- 新增 Cursor 命令
  - `update-changelog.md`: 用于自动更新 CHANGELOG.md 的命令

---

## [0.1.0] - 2026-01-30

### Added

#### Excel 工具
- `excel_inspect_file` - 检查 Excel 文件结构（"上帝视角"工具）
  - 支持获取所有工作表名称、列名和数据预览
  - 支持控制是否包含预览数据
- `excel_read_sheet` - 读取 Excel 工作表内容
  - 支持读取单个工作表或多个工作表
  - 自动处理 NaN 值，转换为 None

#### PDF 工具
- `pdf_extract_text` - 提取 PDF 文本内容
  - 支持提取所有页面或指定页面范围
  - 页面之间用换行符分隔

#### Word 工具
- `word_read_document` - 读取 Word 文档内容
  - 支持读取 .docx 格式文档
  - 段落之间用换行符分隔

#### SQLite 工具
- `sqlite_inspect_database` - 检查 SQLite 数据库（"上帝视角"工具）
  - 支持获取所有表信息、表结构和数据预览
- `sqlite_get_schema` - 获取表结构
  - 返回字段名到类型的映射
- `sqlite_query` - 执行 SQL 查询
  - 支持参数化查询（dict 和 list 格式）
  - 仅允许 SELECT 查询，确保数据安全
  - 自动处理 NULL 值

#### 基础设施
- MCP Python 官方 SDK（`mcp.server.fastmcp`）服务器框架
- 异步包装工具（async_wrapper）
- 路径验证工具（validators）
- 配置管理系统（config）
- 完整的单元测试和集成测试
- 类型注解和 Pydantic 验证

### Security
- SQL 查询安全检查（仅允许 SELECT）
- 路径遍历攻击防护
- 参数化查询支持，防止 SQL 注入
