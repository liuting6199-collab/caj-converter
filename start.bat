@echo off
chcp 65001 >nul
echo ==========================================
echo    CAJ Converter Web - 启动脚本
echo ==========================================
echo.

REM 检查是否已设置CAJViewer路径
if defined CAJVIEWER_PATH (
    echo [信息] 使用指定的CAJViewer路径: %CAJVIEWER_PATH%
) else (
    echo [提示] 未设置CAJViewer路径
    echo.
    echo 如果CAJViewer未自动找到，请设置环境变量：
    echo   set CAJVIEWER_PATH=您的CAJViewer.exe完整路径
    echo.
    echo 按任意键继续，或按Ctrl+C取消...
    pause >nul
)

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查Python环境... 通过

REM 检查虚拟环境
if not exist "..\venv" (
    echo [警告] 未检测到虚拟环境，将使用系统Python
    set PYTHON_CMD=python
) else (
    echo [2/4] 激活虚拟环境...
    call ..\venv\Scripts\activate.bat
    set PYTHON_CMD=python
)

REM 检查依赖
echo [3/4] 检查依赖...
%PYTHON_CMD% -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [信息] 正在安装依赖...
    %PYTHON_CMD% -m pip install fastapi uvicorn python-multipart aiofiles
)

echo.
echo ==========================================
echo    启动服务中...
echo    请稍候...
echo ==========================================
echo.

REM 启动服务
start http://127.0.0.1:8000

%PYTHON_CMD% backend/main.py

pause