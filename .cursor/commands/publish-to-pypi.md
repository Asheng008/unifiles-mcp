# 发布 Python 包到 PyPI

将当前项目（unifiles-mcp）打包并发布到 PyPI（Python Package Index）。

## 目标

- 清理旧的构建产物
- 构建新的分发包（sdist + wheel）
- 上传到 TestPyPI（测试）或正式 PyPI（生产）

## 使用方式

用户可以通过以下方式触发：
- `/publish-to-pypi test` - 发布到 TestPyPI（测试）
- `/publish-to-pypi` 或 `/publish-to-pypi prod` - 发布到正式 PyPI（生产）

**替代方式**：也可在项目根目录直接运行脚本 `publish_pypi.bat test` 或 `publish_pypi.bat`，效果相同。

## 必做步骤

### 1. 检查前置条件

在执行发布前，检查以下内容：
- [ ] 确认 `pyproject.toml` 中的 `version` 已更新（不能与已发布版本重复）
- [ ] 确认 `pyproject.toml` 中的 `name` 在 PyPI 上可用（TestPyPI 可重复，正式 PyPI 必须唯一）
- [ ] 确认已创建 `LICENSE` 文件（本项目使用 MIT 许可证）
- [ ] 确认 `README.md` 内容完整（会显示在 PyPI 项目页面）
- [ ] 确认 `src/unifiles_mcp/__init__.py` 中 `__version__` 与 `pyproject.toml` 的 `version` 一致

### 2. 执行发布流程

根据用户选择的目标（test 或 prod），执行以下步骤：

#### 步骤 1：激活虚拟环境
```powershell
.\.venv\Scripts\Activate.ps1
```

如果虚拟环境不存在，提示用户先创建：
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

#### 步骤 2：安装/升级构建工具
```powershell
pip install --upgrade build twine
```

#### 步骤 3：清理旧构建并构建新分发包
```powershell
chcp 65001
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
```

**说明**：
- `chcp 65001` 设置 UTF-8 编码，避免中文输出乱码
- `Remove-Item` 清理旧的 `dist/` 目录
- `python -m build` 生成新的分发包（sdist + wheel）

#### 步骤 4：验证构建产物
检查 `dist/` 目录是否包含：
- `unifiles_mcp-*.tar.gz` 文件（源码分发包）
- `unifiles_mcp-*-py3-none-any.whl` 文件（wheel 分发包）

如果构建失败，停止流程并报告错误。

#### 步骤 5：上传到 PyPI

**如果目标是 TestPyPI（test）**：
```powershell
python -m twine upload --repository testpypi dist/*
```

**如果目标是正式 PyPI（prod 或默认）**：
```powershell
python -m twine upload dist/*
```

**认证信息**：
- Username: `__token__`
- Password: 用户的 PyPI API Token（含 `pypi-` 前缀）

**注意**：
- TestPyPI 和正式 PyPI 使用不同的账号和 Token
- Token 创建后只显示一次，需妥善保存
- 如果用户配置了 `.pypirc` 文件，twine 会自动使用其中的凭证

### 3. 验证发布结果

上传成功后，提示用户：
- **TestPyPI**: 访问 `https://test.pypi.org/project/unifiles-mcp/` 查看
- **正式 PyPI**: 访问 `https://pypi.org/project/unifiles-mcp/` 查看

并提供安装测试命令：
```powershell
# TestPyPI
pip install --index-url https://test.pypi.org/simple/ --no-deps unifiles-mcp

# 正式 PyPI
pip install unifiles-mcp
```

## 错误处理

### 常见错误及处理

1. **版本已存在**
   - **错误信息**: `HTTPError: 400 Client Error: File already exists`
   - **处理**: 提示用户更新 `pyproject.toml` 和 `src/unifiles_mcp/__init__.py` 中的 `version` 字段

2. **包名已存在（仅正式 PyPI）**
   - **错误信息**: `HTTPError: 403 Client Error: Invalid or non-existent authentication information`
   - **处理**: 提示用户检查包名是否已被占用，或使用 TestPyPI 测试

3. **认证失败**
   - **错误信息**: `HTTPError: 401 Client Error: Invalid or non-existent authentication information`
   - **处理**: 提示用户检查 API Token 是否正确，或重新创建 Token

4. **构建失败**
   - **错误信息**: 构建过程中的错误
   - **处理**: 检查 `pyproject.toml` 配置、依赖是否完整、代码是否有语法错误

## 输出

- 执行每个步骤时，显示清晰的进度信息
- 如果某个步骤失败，立即停止并报告错误
- 上传成功后，显示项目在 PyPI 上的访问链接
- 提供后续验证安装的命令

## 注意事项

- **版本管理**：每次发布前必须更新版本号，PyPI 不允许覆盖已发布的版本
- **测试优先**：建议先发布到 TestPyPI 验证，确认无误后再发布到正式 PyPI
- **Token 安全**：不要将 API Token 提交到版本控制系统
- **网络环境**：国内访问 PyPI 可能较慢，上传时建议使用稳定的网络连接或配置代理
- **文档**：更多说明见 `docs/PYPI_RELEASE_CHECKLIST.md`

## 完整命令示例

### 发布到 TestPyPI
```powershell
chcp 65001
.\.venv\Scripts\Activate.ps1
pip install --upgrade build twine
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
python -m twine upload --repository testpypi dist/*
```

### 发布到正式 PyPI
```powershell
chcp 65001
.\.venv\Scripts\Activate.ps1
pip install --upgrade build twine
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build
python -m twine upload dist/*
```
