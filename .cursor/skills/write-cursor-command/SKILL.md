---
name: write-cursor-command
description: 根据用户需求编写 Cursor 的 slash command。遵循 Cursor 官方 command 格式（纯 Markdown、.cursor/commands/、kebab-case 文件名），产出可复用的工作流指令。当用户要求“写一个 command”“创建一个 /xxx 命令”或“根据 xxx 写 cursor command”时使用。
---

# 编写 Cursor Command

根据用户描述的需求，编写符合 Cursor 官方格式的 slash command，并保存到 `.cursor/commands/`。

## Cursor Command 官方格式（必须遵守）

- **文件格式**：**纯 Markdown**，禁止 YAML frontmatter（与 Rules/Skills 不同）。
- **存放位置**：
  - 项目命令：`.cursor/commands/`（项目根目录下）
  - 全局命令：`~/.cursor/commands/`（用户主目录）
- **文件名**：使用 **kebab-case**，即小写字母与连字符，扩展名 `.md`。文件名即命令名，输入 `/文件名` 触发（如 `update-readme.md` → `/update-readme`）。
- **内容**：用 Markdown 描述「当用户执行该命令时，AI 应该做什么」。用户输入 `/命令名 后面的文字` 会一并作为上下文传给模型。

参考：[Cursor Docs - Commands](https://cursor.com/docs/context/commands)

## 编写流程

### 1. 理解需求

- 用户希望执行 `/xxx` 时完成什么？（例如：更新某文档、跑测试、生成某类代码）
- 有无环境约束？（如 Windows/PowerShell、虚拟环境、编码）
- 有无项目规范要引用？（如 AGENTS.md、.cursor/rules）

### 2. 确定命令名与路径

- 根据用途起一个简短的 kebab-case 名称（如 `update-readme`、`run-tests`、`add-mcp-tool`）。
- 默认写入项目：`.cursor/commands/<命令名>.md`。若用户明确要全局命令，则使用 `~/.cursor/commands/<命令名>.md`。

### 3. 撰写 Markdown 内容

按下面结构组织（可依需求增删小节）：

1. **标题（可选）**  
   一行 `# 中文名 (English Name)`，便于识别。

2. **Overview**  
   2～3 句话说明：该命令做什么、在什么场景下用。

3. **执行步骤 / Steps**  
   分步骤写清「AI 执行此命令时应做的具体动作」。  
   - 若有先后顺序，用 1、2、3…  
   - 若有子项，用缩进列表或 **加粗** 小标题。

4. **环境约束（若需要）**  
   如 Shell（PowerShell）、编码（UTF-8）、Python 虚拟环境路径等。

5. **注意事项 / 模板（若需要）**  
   固定格式、代码块模板、不要改动的部分等。

6. **Checklist**  
   用 `- [ ]` 列出执行完命令后应自检的项，便于用户或 AI 核对。

### 4. 保存与确认

- 保存到 `.cursor/commands/<命令名>.md`。
- 确认：无 frontmatter、文件名 kebab-case、内容为纯 Markdown。

## 内容模板（可直接套用）

```markdown
# 命令中文名 (Command Name)

## Overview
简要说明该命令的用途和适用场景（2～3 句）。

## 执行步骤

1. **第一步**
   - 子步骤或说明

2. **第二步**
   - 子步骤或说明

3. **第三步**
   - 子步骤或说明

## 注意事项（可选）
- 需要遵守的约定或不要改动的部分

## Checklist
- [ ] 检查项 1
- [ ] 检查项 2
```

## 本项目中已有命令可作参考

- `update-readme.md`：按项目状态更新 README（版本、工具列表、结构、文档链接）。
- `update-history.md`：将当前对话中的用户指令追加到 `history.md`。
- `fix-and-verify.md`：修复问题后做静态检查与测试验证。
- `run-tests.md`：在 Windows 下运行测试。
- `lint-and-format.md`：代码检查与格式化。

写作时可参考其「Overview + 步骤 + 约束 + Checklist」的写法，保持风格一致。

## 注意事项

- **不要**在 command 文件顶部加 `---` YAML frontmatter；Commands 仅支持纯 Markdown。
- **不要**用空格或下划线命名文件，统一用 kebab-case（如 `update-readme.md`）。
- 步骤要**可执行**：写清「读什么、改什么、运行什么命令」，方便 AI 按步骤执行。
- 若项目有 AGENTS.md 或 .cursor/rules，可在命令中注明「遵循 xxx」，便于 AI 加载规范。

## Checklist（写完 command 后自检）

- [ ] 文件位于 `.cursor/commands/`，文件名为 kebab-case 且以 `.md` 结尾
- [ ] 内容为纯 Markdown，无 YAML frontmatter
- [ ] 含 Overview 与明确的执行步骤
- [ ] 必要时含环境约束与 Checklist
- [ ] 步骤描述清晰，AI 可按其执行
