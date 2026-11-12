# One-click PowerShell runner
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting Campus Placement Prediction System..." -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

if (Test-Path ".\venv\Scripts\python.exe") {
    & ".\venv\Scripts\python.exe" app.py
} else {
    python app.py
}
