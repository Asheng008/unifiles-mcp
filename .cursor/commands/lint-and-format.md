# 代码检查与格式化 (Lint & Format)

## Overview
按项目规范运行静态检查与格式化：ruff 检查、black 格式化、mypy 类型检查。在 Windows PowerShell 下执行，使用项目虚拟环境。

## 环境约束
- **Shell**: PowerShell
- **编码**: 命令前建议 `chcp 65001; [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8`
- **Python**: 使用 `.\.venv\Scripts\`

## Steps
1. **安装/确认开发依赖**
   - `chcp 65001; .\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"`
   - 或 `pip install -r requirements-dev.txt`（若项目提供）
2. **Ruff 检查**
   - `.\.venv\Scripts\Activate.ps1; ruff check src/`
   - 自动修复可加：`ruff check src/ --fix`
3. **Black 格式化**
   - `.\.venv\Scripts\Activate.ps1; black src/`
4. **Mypy 类型检查**
   - `.\.venv\Scripts\Activate.ps1; mypy src/unifiles_mcp/`
5. **按需修复**
   - 根据上述输出修改代码，然后重新运行直到通过

## Checklist
- [ ] 已激活虚拟环境
- [ ] ruff 无报错或已修复
- [ ] black 已格式化目标目录
- [ ] mypy 通过或仅剩预期忽略项
