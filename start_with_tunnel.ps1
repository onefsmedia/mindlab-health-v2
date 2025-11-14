# MindLab Health - Start with Internet Access
# This script starts both the Python server and Ngrok tunnel

Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "  MindLab Health - Internet Access" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""

# Check if ngrok is configured
$ngrokConfigPath = "$env:USERPROFILE\.ngrok2\ngrok.yml"
if (-not (Test-Path $ngrokConfigPath)) {
    Write-Host "ERROR: Ngrok not configured!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run:" -ForegroundColor Yellow
    Write-Host "  .\ngrok.exe config add-authtoken YOUR_TOKEN" -ForegroundColor White
    Write-Host ""
    Write-Host "Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken" -ForegroundColor Cyan
    exit 1
}

Write-Host "Starting MindLab Health server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\venv\Scripts\python.exe .\start_local.py" -WindowStyle Normal

Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting Ngrok tunnel..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; .\ngrok.exe http 8081 --log=stdout" -WindowStyle Normal

Write-Host ""
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Two windows opened:" -ForegroundColor White
Write-Host "  1. Python Server (port 8081)" -ForegroundColor White
Write-Host "  2. Ngrok Tunnel" -ForegroundColor White
Write-Host ""
Write-Host "Check the Ngrok window for your public URL!" -ForegroundColor Yellow
Write-Host "It will look like: https://abc123.ngrok.io" -ForegroundColor Cyan
Write-Host ""
Write-Host "Login Credentials:" -ForegroundColor White
Write-Host "  Username: admin" -ForegroundColor White
Write-Host "  Password: Admin123!@#" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to exit (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
