@echo off
setlocal
echo ===================================================
echo   DoctorIn — Full-Stack Development Startup
echo ===================================================
echo [1/3] Launching FastAPI Backend (with auto-reload) on http://127.0.0.1:8000...
start "DoctorIn Backend (FastAPI)" cmd /k "cd /d %~dp0..\backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/3] Launching Next.js Frontend (with hot-reload) on http://localhost:3000...
start "DoctorIn Frontend (Next.js)" cmd /k "cd /d %~dp0..\frontend && npm run dev"

echo [3/3] Waiting for servers to initialize...
timeout /t 4 /nobreak >nul 2>&1 || ping -n 5 127.0.0.1 >nul

echo Opening DoctorIn in default browser...
start http://localhost:3000
echo.
echo ===================================================
echo   DoctorIn is active in Development Mode!
echo   Auto-reload / Hot-reload is enabled on both servers.
echo   Keep the terminal windows open while working.
echo ===================================================
endlocal
