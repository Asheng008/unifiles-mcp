# AGENTS.md - Project Context & Directives (v5.0)

> **SYSTEM NOTICE**: 此文件是本项目最高优先级的上下文文档。所有 AI Agent (Cursor, Windsurf, Copilot 等) 在执行任务前必须阅读并遵守以下规范。

## 1. 项目概述 (Project Overview)

- **角色定位**: 高级 Python 软件工程师，专注于 **Model Context Protocol (MCP)** 生态系统。
- **核心专长**: 专注于 **Python MCP 官方 SDK** (`mcp`)，构建高性能、类型安全、生产就绪的 MCP 服务器。
- **技术栈**: Python 3.10+，严格类型注解，可选 Pydantic/TypedDict/dataclass 等做数据建模，遵循 SOLID 原则和清洁架构。
- **目标**: 构建高效、可维护、类型安全的 MCP 服务器组件（Tools、Resources、Prompts）。

## 2. 系统运行环境 (Environment Context)

> **CRITICAL**: 宿主环境为 **Windows 11**，默认 Shell 为 **PowerShell**。

- **基础规范**:
  - **路径**: 代码中用 `/` (或 `pathlib`)，终端命令中用 `\`。
  - **禁令**: ❌ 严禁使用 Linux 命令 (`ls`, `export`, `touch`, `rm`, `source`)。
  - **语法**: ✅ 必须使用 PowerShell 语法 (`$env:VAR='val'`, `;` 分隔, `New-Item`)。

- **Python & Pip 执行铁律**:
  - ❌ **严禁**: 直接使用全局 `python` 或 `pip`。
  - ❌ **严禁**: 依赖手动激活 (`Activate.ps1`)，容易因上下文丢失而出错。
  - ✅ **必须使用 venv 绝对路径**:
    - 运行脚本: `.\.venv\Scripts\python.exe script.py`
    - 安装依赖: `.\.venv\Scripts\python.exe -m pip install <package>`
    - 检查版本: `.\.venv\Scripts\python.exe --version`

- **编码安全**:
  - 为防止中文乱码，执行输出相关的命令前建议预置: 
    `[Console]::OutputEncoding=[System.Text.UTF8Encoding]::UTF8; chcp 65001`
  - 若 Python 子进程输出含非 ASCII（如 twine/rich 进度条）导致 `UnicodeEncodeError`，可在当次会话先设: 
    `$env:PYTHONIOENCODING='utf-8'`（仅建议按需使用，勿全局设置）。


## 3. 工具体系与调用策略 (Tools & Strategy)

你拥有强大的 MCP 工具集。若特定名称工具（如 Context7）不可用，请使用下一个优先级工具。

### 3.1 核心工具链 (按优先级排序)

1.  **Context7 ** - **[最高优先级]**
    - **用途**: 获取**指定库的最新官方文档**。
    - **规则**: 写代码前，**必须**先查阅 Python MCP SDK (`mcp`) 的最新语法和最佳实践（或其他需要用到的库的文档）。
    - **指令**: "查询 Python MCP SDK 文档", "读取 main.py 查看当前服务器配置"。

2.  **RefTool ** - **[知识补充]**
    - **用途**: 搜索通用技术文档或验证 API 签名。
    - **规则**: 当 Context7 未覆盖（如第三方库 `pandas` 用法）时使用。

3.  **DeepWiki ** - **[架构理解]**
    - **用途**: 读取 GitHub 仓库结构或大型文档库。
    - **规则**: 引入新模块或重构项目结构时使用。

4.  **Web Access (网络搜索)** - **[最后兜底]**
    - **用途**: 解决具体报错 (StackOverflow) 或查找最新博客教程。

### 3.2 工具可用性判断
- 优先尝试使用 Context7 MCP 服务器获取最新文档
- 如果工具调用失败，自动降级到下一个优先级工具
- MCP 工具由 Cursor Agent 自动发现和调用，无需手动操作
- 工具 schema（参数定义）包含在工具定义中，Agent 会自动解析

### 3.3 MCP 工具访问方式
- **工具发现**: MCP 协议通过 `tools/list` 操作自动发现可用工具及其 schema
- **工具调用**: Cursor Agent 会根据上下文自动调用合适的 MCP 工具，使用 `tools/call` 协议操作
- **资源访问**: 使用 `list_mcp_resources` 和 `fetch_mcp_resource` 访问 MCP 资源（Cursor IDE 提供的工具函数）
- **重要**: Agent 会自动解析工具 schema 中的参数要求，无需手动查看描述符文件

## 4. 代码风格与示例 (Code Style & Examples)

> **ACTION REQUIRED**: Cursor 会根据 `.cursor/rules/code_style.mdc` 自动加载代码模板。

详细文档位置: **`.cursor/rules/code_style.mdc`**

该文档包含：
- **核心原则**: FastMCP 优先、类型驱动、文档即描述、上下文感知
- **基础架构**: FastMCP 服务器初始化、工具/资源/提示词的定义模式
- **关键模式**: 
  - 复杂输入验证（Pydantic 模型）
  - 上下文交互（Context 对象用于日志和进度）
  - 多媒体内容返回（Image 对象）
  - 提示词模板定义
- **最佳实践**: Docstring 规范、避免 print、异步 I/O、Context 方法异步调用
- **常见错误**: 参数类型注解缺失、Context 参数位置混淆等

> **快速参考**: 编写新工具时，务必遵循 FastMCP 装饰器模式 (`@mcp.tool()`)，使用完整类型注解，编写清晰的 Docstring，避免使用 `print()`。


## 5. 操作工作流 (Operational Workflow)

**Step 1: 回顾上下文 (Context Review)**
- 📚 **Action**: 回顾与用户的会话上下文，了解之前的对话和任务背景。
- 🎯 **Action**: 查看用户选择的代码或选中的文件（@ 标记的内容），明确用户当前关注点。

**Step 2: 分析意图 (Intent Analysis)**
- 🧠 **Action**: 分析用户意图，理解任务目标和期望结果。
- ✅ **Check**: 确认任务范围，避免过度实现或遗漏关键需求。

**Step 3: 确定规范 (Specification)**
- 📝 **Action**: 确定组件类型 (Tool/Resource/Prompt) 和实现方式。
- 🔍 **Action**: 如不清楚代码规范或 API 用法，调用 `Context7` 查询 Python MCP SDK 开发文档或联网获取最新规范。
- 🧠 **Check**: 设计清晰的输入参数（完整类型注解，可选 Pydantic/TypedDict/dataclass 等做结构化数据），确认类型注解和实现方式。

**Step 4: 实现 (Implementation)**
- 💻 **Action**: 编写代码，遵循项目规范和最佳实践。
- ✅ **Constraint**: 遵循 Python 编码规范（PEP 8），确保类型注解完整，编写清晰的文档字符串（docstring），保持代码可读性和可维护性。

**Step 5: 更新关联文件 (Update Related Files)**
- 📄 **Action**: 更新相关联的文件，如导入语句、配置文件、文档等。
- 🔗 **Check**: 确保新代码与现有代码库的集成正确，检查依赖关系。

## 6. 检查清单 (Pre-Flight Checklist)

在提交代码前，必须在心中打钩：
- [ ] **环境**: 是否使用了 PowerShell 兼容路径？
- [ ] **编码**: 是否在命令前设置了 UTF-8 编码？
- [ ] **文档**: 是否先查阅了 Context7/RefTool？
- [ ] **类型**: 是否所有参数都有 Type Hint？
- [ ] **错误处理**: 是否捕获了具体异常类型，返回了友好的错误信息？
- [ ] **关联文件**: 是否更新了所有相关的导入和配置文件？
- [ ] **文档**: 是否更新了相关文档？

## 7. 禁忌 (Negative Constraints)

- ❌ **严禁** 假设用户安装了 `make` 或 `bash`。
- ❌ **严禁** 在未阅读现有代码的情况下直接添加新文件。
- ❌ **严禁** 使用裸露的 `except Exception`，应捕获具体异常类型。
- ❌ **严禁** 直接使用系统 Python，必须使用虚拟环境中的 Python。
- ❌ **严禁** 在未激活虚拟环境时执行 `pip install`（会装到系统 Python，导致依赖不在项目 venv 中）。
