@REM 为当前这个项目写个requirements.txt文件

@echo off

chcp 65001

echo Creating virtual environment...

python -m venv .venv

echo Virtual environment created.

echo Waiting for 10 seconds...

timeout /t 10 /nobreak

echo Activating virtual environment...

call .venv\Scripts\activate.bat

echo Upgrading pip...

.venv\Scripts\python.exe -m pip install --upgrade pip

echo Waiting for 3 seconds...

timeout /t 3 /nobreak

echo Installing dependencies...

if exist pyproject.toml (
    echo Found pyproject.toml, installing with pip install .
    .venv\Scripts\python.exe -m pip install .
) else if exist requirements.txt (
    echo Found requirements.txt, installing with pip install -r requirements.txt
    .venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
    echo Error: Neither pyproject.toml nor requirements.txt found in current directory!
    pause
    exit /b 1
)

echo Setup complete. You can now run the application.

pause
