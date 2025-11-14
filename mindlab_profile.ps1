# PowerShell Profile for MindLab Health Development
# This file ensures all PowerShell sessions start in the correct directory

$MindLabDirectory = "C:\Multi Agent\mindlab_health_v2"

if (Test-Path $MindLabDirectory) {
    Set-Location $MindLabDirectory
    Write-Host "Automatically navigated to MindLab Health directory: $MindLabDirectory" -ForegroundColor Green
} else {
    Write-Host "Warning: MindLab Health directory not found: $MindLabDirectory" -ForegroundColor Yellow
}

# Display current location
Write-Host "Current directory: $(Get-Location)" -ForegroundColor Cyan