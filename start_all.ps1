# ==============================================================================
# ZuvoCloud AI Solution - Full Stack Launcher (PowerShell)
# ==============================================================================

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "   ZuvoCloud Full-Stack Platform Launcher           " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check port 8000
$port8000 = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if (-not $port8000) {
    Write-Host "--> Starting FastAPI Backend on http://localhost:8000 in background..." -ForegroundColor Blue
    Start-Process -FilePath "python" -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Hidden
    Start-Sleep -Seconds 2
} else {
    Write-Host "[OK] FastAPI Backend is already running on port 8000." -ForegroundColor Green
}

Write-Host "--> Starting React Owner Command Center on http://localhost:3000..." -ForegroundColor Blue
Set-Location -Path "$PSScriptRoot\frontend"
npm run dev -- --host 0.0.0.0 --port 3000
