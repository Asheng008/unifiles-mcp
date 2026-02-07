---
name: code-quality-check
description: 运行代码质量检查工具，包括 ruff、black 和 mypy。格式化代码、检查代码风格、进行类型检查。当需要确保代码符合项目规范、修复格式问题或进行代码审查时使用。
---

# 代码质量检查

运行代码质量检查工具，确保代码符合项目规范。

## 快速执行

### 完整检查流程

```powershell
# 设置编码并激活环境
chcp 65001; [Console]::OutputEncoding = [System.Text.UTF8Encoding]::UTF8; .\.venv\Scripts\Activate.ps1

# 1. Black 格式化代码
black src/ tests/

# 2. Ruff 检查并自动修复
ruff check src/ tests/ --fix

# 3. Mypy 类型检查
mypy src/unifiles_mcp/
```

### 单独执行

#### Black 格式化

```powershell
.\.venv\Scripts\Activate.ps1; black src/ tests/
```

检查但不修改：

```powershell
.\.venv\Scripts\Activate.ps1; black src/ tests/ --check
```

#### Ruff 检查

```powershell
.\.venv\Scripts\Activate.ps1; ruff check src/ tests/
```

自动修复：

```powershell
.\.venv\Scripts\Activate.ps1; ruff check src/ tests/ --fix
```

#### Mypy 类型检查

```powershell
.\.venv\Scripts\Activate.ps1; mypy src/unifiles_mcp/
```

## 工具配置

### Black 配置

项目配置在 `pyproject.toml`：

```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
```

### Ruff 配置

项目配置在 `pyproject.toml`：

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501"]  # line too long (handled by black)
```

### Mypy 配置

项目配置在 `pyproject.toml`：

```toml
[tool.mypy]
python_version = "3.10"
warn_return_any = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

## 常见问题修复

### Ruff 错误

**E501 - 行太长**
- 通常由 Black 处理，如果出现，检查 Black 是否已运行

**F401 - 未使用的导入**
- 删除未使用的导入
- 或使用 `# noqa: F401` 注释（谨慎使用）

**I001 - 导入排序**
- Ruff 会自动修复，运行 `ruff check --fix`

### Mypy 错误

**缺少类型注解**
- 为函数参数和返回值添加类型注解
- 使用 `typing` 模块的类型提示

**类型不匹配**
- 检查变量类型声明
- 使用 `cast()` 或类型断言（谨慎使用）

**未定义的类型**
- 确保导入所有使用的类型
- 使用 `from __future__ import annotations` 延迟评估

## 代码规范要点

### 必须遵循

1. **类型注解**
   - 所有函数参数和返回值必须有类型注解
   - 使用 Pydantic 模型定义复杂参数

2. **异步优先**
   - 使用 `async def` 定义异步函数
   - 避免阻塞 I/O 操作

3. **异常处理**
   - 捕获具体异常类型
   - 避免裸露的 `except Exception`

4. **导入顺序**
   - 标准库
   - 第三方库
   - 本地模块

### 代码风格

- 行长度：100 字符
- 使用 4 个空格缩进
- 使用双引号字符串
- 函数和类之间空两行

## 检查清单

代码质量检查完成后，确认：

- [ ] 已激活虚拟环境
- [ ] Black 已格式化代码（无格式问题）
- [ ] Ruff 无报错或已修复所有问题
- [ ] Mypy 通过或仅剩预期忽略项
- [ ] 所有类型注解完整
- [ ] 无未使用的导入
- [ ] 代码符合项目规范

## 集成到工作流

### 提交前检查

```powershell
chcp 65001; .\.venv\Scripts\Activate.ps1; black src/ tests/; ruff check src/ tests/ --fix; mypy src/unifiles_mcp/
```

### 持续集成

在 CI/CD 流程中：

```yaml
- name: Code Quality Check
  run: |
    black --check src/ tests/
    ruff check src/ tests/
    mypy src/unifiles_mcp/
```
