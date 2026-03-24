@echo off
chcp 65001 >nul
title CAJ Converter Web
color 0A

echo.
echo  ╔══════════════════════════════════════╗
echo  ║   CAJ Converter Web - 快速启动      ║
echo  ╚══════════════════════════════════════╝
echo.

REM 切换到项目目录
cd /d "%~dp0"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    echo.
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [√] Python环境检测通过
echo.

REM 检查依赖
echo [*] 检查依赖包...
python -c "import fastapi, uvicorn, PyPDF2, imagesize" 2>nul
if errorlevel 1 (
    echo [!] 正在安装依赖包，请稍候...
    python -m pip install -q -r requirements.txt
    echo [√] 依赖安装完成
) else (
    echo [√] 依赖包已就绪
)

echo.
echo  ╔══════════════════════════════════════╗
echo  ║  服务启动中，请稍候...              ║
echo  ║  启动后会自动打开浏览器             ║
echo  ╚══════════════════════════════════════╝
echo.

REM 启动浏览器（延迟2秒）
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"

REM 启动服务
python backend/main.py

pause
