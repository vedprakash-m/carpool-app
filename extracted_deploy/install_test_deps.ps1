#!/usr/bin/env pwsh
# Install test dependencies for the carpool management system

Write-Host "Installing test dependencies..." -ForegroundColor Cyan

# Install primary requirements
pip install -r requirements.txt

# Install visualization packages
pip install tabulate colorama

# Install additional test packages
pip install pytest-asyncio

Write-Host "Dependencies installed successfully!" -ForegroundColor Green
Write-Host "You can now run tests with:" -ForegroundColor Yellow
Write-Host "  ./run_schedule_tests.ps1" -ForegroundColor Yellow
