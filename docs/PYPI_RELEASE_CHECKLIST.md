# 发布 PyPI 前检查清单

本文档列出本项目距离发布到 PyPI 的差距与已完成的项。**构建已通过**（`python -m build --outdir dist` 可成功生成 sdist 与 wheel）。

---

## 已就绪项（无需再改）

| 项 | 说明 |
|----|------|
| **pyproject.toml** | 包名、版本、描述、readme、Python 版本、依赖、作者、keywords、classifiers、urls、license、license-files 已配置 |
| **license** | 使用 `license = "MIT"`（字符串），且已移除废弃的 `License :: OSI Approved :: MIT License` classifier（PEP 639） |
| **LICENSE 文件** | 根目录已有 MIT LICENSE，会被打入 sdist/wheel |
| **README.md** | 作为 long description，PyPI 会展示 |
| **src 布局** | `src/unifiles_mcp/` 包结构正确，setuptools 能正确发现 |
| **依赖** | `unifiles>=0.3.1` 已在 PyPI，`mcp[cli]`、`pydantic` 均可安装 |
| **.gitignore** | 已忽略 `dist/`、`build/`、`*.egg-info` 等 |

---

## 发布前必做（还差这些）

### 1. PyPI 账号与 Token

- 在 [pypi.org](https://pypi.org) 注册账号（若尚未注册）。
- 在 Account settings → API tokens 中创建 Token，用于 `twine upload`。
- 若仅测试，可使用 [test.pypi.org](https://test.pypi.org) 的账号与 Token。

### 2. 安装 twine 并上传

```powershell
pip install twine
# 检查打包产物
twine check dist/*
# 上传到 PyPI（会提示输入用户名和密码，用户名填 __token__，密码填 Token）
twine upload dist/*
```

上传前请确认：

- **版本号**：`pyproject.toml` 与 `src/unifiles_mcp/__init__.py` 中 `__version__` 一致（当前为 `0.1.2`）。
- **包名**：PyPI 上 `unifiles-mcp` 未被占用（首次发布前在 pypi.org 搜索确认）。

---

## 可选改进（不影响“能发布”）

| 项 | 说明 |
|----|------|
| **命令行入口** | ✅ 已实现：`[project.scripts]` 中配置 `unifiles-mcp = "unifiles_mcp.main:run"`，`main.py` 中提供 `run()`，安装后可直接执行 `unifiles-mcp`。 |
| **发布脚本** | ✅ 已实现：项目根目录 `publish_pypi.bat`，支持 `publish_pypi.bat test`（TestPyPI）与 `publish_pypi.bat`（正式 PyPI）。 |
| **CI 自动发布** | 参考 unifiles 的 `docs/03-用GitHub-Actions自动发布到PyPI.md`，用 GitHub Actions 在打 tag 时自动构建并上传 PyPI。 |
| **tests** | 当前无 `tests/` 目录，不影响打包与上传；若后续补充测试，可在 CI 中增加 `pytest`。 |

---

## 本次已修复（构建曾失败的原因）

1. **license 格式**：由 `license = {text = "MIT"}` 改为 `license = "MIT"`，满足当前 setuptools 要求。
2. **dependencies 位置**：`dependencies` 曾写在 `[project.urls]` 之后，被解析为 `project.urls.dependencies`（要求 URL 字符串），已移回 `[project]` 下。
3. **License classifier**：在启用 PEP 639 后，保留 `License :: OSI Approved :: MIT License` 会触发 setuptools 报错，已移除；PyPI 会从 `license` 和 `license-files` 展示 MIT。

---

## 快速发布命令汇总

**方式一：使用发布脚本（推荐）**

```cmd
publish_pypi.bat test   rem 发布到 TestPyPI
publish_pypi.bat        rem 发布到正式 PyPI
```

脚本会依次：升级 build/twine → 清理 dist → 构建 → 上传。需已存在 `.venv` 且安装 `.[dev]`。

**方式二：手动命令**

```powershell
.\.venv\Scripts\Activate.ps1
pip install build twine
python -m build --outdir dist
twine check dist/*
twine upload dist/*
```

按上述步骤完成 **PyPI 账号/Token** 和 **twine 上传** 后，即可完成首次发布。
