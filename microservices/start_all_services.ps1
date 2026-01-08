<# 
PowerShell script to start all microservices
Run this script from the project root directory
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Flight Ticket Booking Microservices  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ProjectRoot = Split-Path -Parent $PSScriptRoot
if (-not $ProjectRoot) {
    $ProjectRoot = Get-Location
}

Write-Host "Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host ""

# Check if virtual environment exists
$VenvPath = Join-Path $ProjectRoot "venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $VenvPath
}

# Function to start a service in a new PowerShell window
function Start-Service {
    param (
        [string]$ServiceName,
        [string]$Port,
        [string]$SettingsModule
    )
    
    Write-Host "Starting $ServiceName on port $Port..." -ForegroundColor Green
    
    $Command = @"
cd '$ProjectRoot'
if (Test-Path 'venv\Scripts\Activate.ps1') { & 'venv\Scripts\Activate.ps1' }
`$env:DJANGO_SETTINGS_MODULE = '$SettingsModule'
python -m django runserver $Port --settings=$SettingsModule
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Command
}

# Start all services
Write-Host ""
Write-Host "Starting Microservices..." -ForegroundColor Cyan
Write-Host ""

Start-Service -ServiceName "User Service" -Port "8001" -SettingsModule "microservices.user_service.settings"
Start-Sleep -Seconds 2

Start-Service -ServiceName "Flight Service" -Port "8002" -SettingsModule "microservices.flight_service.settings"
Start-Sleep -Seconds 2

Start-Service -ServiceName "Booking Service" -Port "8003" -SettingsModule "microservices.booking_service.settings"
Start-Sleep -Seconds 2

Start-Service -ServiceName "API Gateway" -Port "8000" -SettingsModule "microservices.api_gateway.settings"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  All Services Started!                " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Service URLs:" -ForegroundColor Yellow
Write-Host "  API Gateway:     http://localhost:8000" -ForegroundColor White
Write-Host "  User Service:    http://localhost:8001" -ForegroundColor White
Write-Host "  Flight Service:  http://localhost:8002" -ForegroundColor White
Write-Host "  Booking Service: http://localhost:8003" -ForegroundColor White
Write-Host ""
Write-Host "Health Check: http://localhost:8000/health/" -ForegroundColor Green
Write-Host ""
