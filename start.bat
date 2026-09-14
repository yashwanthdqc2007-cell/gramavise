@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%backend"
set "FRONTEND_DIR=%ROOT_DIR%frontend"
set "BACKEND_LOG=%ROOT_DIR%.gramavise-backend.log"
set "FRONTEND_LOG=%ROOT_DIR%.gramavise-frontend.log"

if not exist "%ROOT_DIR%.env" if exist "%ROOT_DIR%.env.example" copy /Y "%ROOT_DIR%.env.example" "%ROOT_DIR%.env" >nul

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ports = 8000,3000; foreach ($port in $ports) { Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue } }"

if not exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
    python -m venv "%BACKEND_DIR%\.venv"
    if errorlevel 1 (
        echo Failed to create the backend virtual environment.
        pause
        exit /b 1
    )
    "%BACKEND_DIR%\.venv\Scripts\python.exe" -m pip install -r "%BACKEND_DIR%\requirements.txt"
    if errorlevel 1 (
        echo Failed to install backend dependencies.
        pause
        exit /b 1
    )
)

if not exist "%FRONTEND_DIR%\node_modules" (
    pushd "%FRONTEND_DIR%"
    call npm.cmd install
    set "INSTALL_ERROR=%ERRORLEVEL%"
    popd
    if not "%INSTALL_ERROR%"=="0" (
        echo Failed to install frontend dependencies.
        pause
        exit /b 1
    )
)

start "GramaVise Backend" /min cmd /d /c "cd /d "%BACKEND_DIR%" && "%BACKEND_DIR%\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload >> "%BACKEND_LOG%" 2>&1"
start "GramaVise Frontend" /min cmd /d /c "cd /d "%FRONTEND_DIR%" && call npm.cmd run dev -- --hostname 0.0.0.0 --port 3000 >> "%FRONTEND_LOG%" 2>&1"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline = (Get-Date).AddSeconds(90); do { try { Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:3000' -TimeoutSec 3 | Out-Null; break } catch { Start-Sleep -Seconds 1 } } while ((Get-Date) -lt $deadline); if ((Get-Date) -ge $deadline) { exit 1 }"
if errorlevel 1 (
    echo GramaVise failed to start. Check:
    echo %BACKEND_LOG%
    echo %FRONTEND_LOG%
    pause
    exit /b 1
)

start "" "http://localhost:3000"
exit /b 0
