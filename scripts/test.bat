@echo off
setlocal
echo ===================================================
echo   DoctorIn — Running Full Test Suite
echo ===================================================

echo [1/2] Running Backend Unit & Integration Tests (pytest)...
cd /d %~dp0..\backend
python -m pytest tests -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend tests failed!
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Running Frontend TypeScript Type Checking...
cd /d %~dp0..\frontend
call npm run type-check
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend type check failed!
    exit /b %ERRORLEVEL%
)

echo.
echo ===================================================
echo   All DoctorIn tests passed successfully!
echo ===================================================
endlocal
