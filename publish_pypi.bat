@echo off
setlocal

rem Change to script directory (project root)
cd /d "%~dp0"

rem UTF-8 for console output
chcp 65001 >NUL
rem Python stdin/stdout/stderr use UTF-8 (avoids twine/rich encoding errors on Windows)
set PYTHONIOENCODING=utf-8

echo ===============================
echo unifiles-mcp - Publish to PyPI
echo Usage:
echo   publish_pypi.bat test  = TestPyPI
echo   publish_pypi.bat       = Production PyPI
echo ===============================

set "PYTHON=.venv\Scripts\python.exe"

if not exist "%PYTHON%" (
 echo [ERROR] .venv not found. Run in project root:
 echo   python -m venv .venv
 echo   .\.venv\Scripts\Activate.ps1
 echo   pip install -e ".[dev]"
 exit /b 1
)

echo.
echo [1/4] Upgrade build, twine...
"%PYTHON%" -m pip install --upgrade build twine
if errorlevel 1 (
 echo [ERROR] pip install build twine failed.
 exit /b 1
)

echo.
echo [2/4] Clean dist...
if exist "dist" (
 rmdir /s /q "dist"
)

echo.
echo [3/4] Build sdist and wheel...
"%PYTHON%" -m build
if errorlevel 1 (
 echo [ERROR] Build failed. Check pyproject.toml and code.
 exit /b 1
)

echo.
echo [4/4] Upload to PyPI...

if /I "%1"=="test" (
 echo Target: TestPyPI
 "%PYTHON%" -m twine upload --repository testpypi dist\*
) else (
 echo Target: Production PyPI
 "%PYTHON%" -m twine upload dist\*
)

if errorlevel 1 (
 echo [ERROR] Upload failed. Check network, credentials, or version.
 exit /b 1
)

echo.
echo [DONE] Built and uploaded:
echo   dist\unifiles_mcp-*.tar.gz
echo   dist\unifiles_mcp-*-py3-none-any.whl
echo.
echo TestPyPI:  https://test.pypi.org/project/unifiles-mcp/
echo PyPI:      https://pypi.org/project/unifiles-mcp/

endlocal
exit /b 0
