Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "   DoctorIn — Full-Stack Development Startup" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "[1/3] Launching FastAPI Backend (with auto-reload) on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d `"$projectRoot\backend`" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/3] Launching Next.js Frontend (with hot-reload) on http://localhost:3000..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d `"$projectRoot\frontend`" && npm run dev"

Write-Host "[3/3] Waiting for servers to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 4

Write-Host "Opening DoctorIn in default browser..." -ForegroundColor Green
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "DoctorIn is active in Development Mode!" -ForegroundColor Cyan
Write-Host "Auto-reload / Hot-reload is enabled on both servers." -ForegroundColor Gray
Write-Host "Keep the terminal windows open while working." -ForegroundColor Gray
