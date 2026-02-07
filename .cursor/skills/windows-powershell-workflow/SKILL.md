---
name: windows-powershell-workflow
description: 在 Windows PowerShell 环境下执行命令和操作的工作流指南。包括编码设置、虚拟环境管理、路径处理、文件操作等 Windows 特定操作。当需要在 Windows 环境下执行命令、处理路径或解决 Windows 特定问题时使用。
---

# Windows PowerShell 工作流

在 Windows PowerShell 环境下执行命令和操作的工作流指南。

## 核心原则

### 环境约束

- **OS**: Windows 11
- **Shell**: PowerShell 5.1 / 7+
- **Python**: 必须使用项目虚拟环境 `.\.venv\Scripts\`

### 路径规范

- **代码中 (Python)**: 始终使用正斜杠 `/` 或 `pathlib.Path`
- **终端命令中**: 注意反斜杠 `\` 的兼容性

## 编码设置

### 必须设置 UTF-8

执行任何可能输出中文的命令前，**必须**设置 UTF-8 编码：

```powershell
chcp 65001; [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8
```

### 完整命令模板

```powershell
chcp 65001; [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8; <your-command>
```

## 虚拟环境管理

### 激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
```

### 检查 Python 版本

```powershell
.\.venv\Scripts\python.exe --version
```

### 安装依赖

```powershell
.\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

开发依赖：

```powershell
.\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"
```

## 命令执行

### 链式命令

使用分号 `;` 分隔多个命令：

```powershell
chcp 65001; .\.venv\Scripts\Activate.ps1; python script.py
```

### 设置环境变量

```powershell
$env:VAR_NAME = "value"
```

### 检查命令是否存在

```powershell
Get-Command python -ErrorAction SilentlyContinue
```

## 文件操作

### 创建目录

```powershell
New-Item -ItemType Directory -Path "path/to/dir"
```

创建多级目录：

```powershell
New-Item -ItemType Directory -Path "path/to/dir" -Force
```

### 读取文件

```powershell
Get-Content file.txt
```

或使用别名：

```powershell
cat file.txt
```

### 写入文件

```powershell
"content" | Out-File -FilePath "file.txt" -Encoding UTF8
```

### 检查文件/目录是否存在

```powershell
Test-Path "path/to/file"
```

### 删除文件

```powershell
Remove-Item "path/to/file"
```

### 删除目录（递归）

```powershell
Remove-Item "path/to/dir" -Recurse -Force
```

## 禁止使用的命令

### ❌ 严禁使用 Linux 专属命令

- `export` → 使用 `$env:VAR = "value"`
- `ls -la` → 使用 `Get-ChildItem` 或 `ls`
- `touch` → 使用 `New-Item -ItemType File`
- `rm -rf` → 使用 `Remove-Item -Recurse -Force`
- `source` → 使用 `.` 或 `&`
- `make` → 使用 PowerShell 脚本或直接命令

## Python 命令执行

### 执行 Python 脚本

```powershell
.\.venv\Scripts\Activate.ps1; python script.py
```

或使用完整路径：

```powershell
.\.venv\Scripts\python.exe script.py
```

### 运行模块

```powershell
.\.venv\Scripts\Activate.ps1; python -m module_name
```

### 执行 pip 命令

```powershell
.\.venv\Scripts\Activate.ps1; pip install package
```

## 常见问题

### 问题：执行策略限制

如果遇到 "无法加载文件，因为在此系统上禁止运行脚本"：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 问题：路径包含空格

使用引号包裹路径：

```powershell
& "C:\Program Files\Python\python.exe" script.py
```

### 问题：中文乱码

确保命令前包含编码设置：

```powershell
chcp 65001; [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8; <command>
```

## 项目特定命令

### 运行测试

```powershell
chcp 65001; .\.venv\Scripts\Activate.ps1; pytest tests/ -v
```

### 代码格式化

```powershell
.\.venv\Scripts\Activate.ps1; black src/ tests/
```

### 启动 MCP 服务器

```powershell
chcp 65001; .\.venv\Scripts\Activate.ps1; python -m unifiles_mcp
```

## 检查清单

执行命令前，确认：

- [ ] 已设置 UTF-8 编码（如需要中文输出）
- [ ] 已激活虚拟环境（如执行 Python 命令）
- [ ] 未使用 Linux 专属命令
- [ ] 路径处理正确（使用正斜杠或 pathlib）
- [ ] 使用项目虚拟环境中的 Python
