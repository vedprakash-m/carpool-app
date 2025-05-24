# Troubleshoot Azure Function App Deployment
# This script will help diagnose issues with the deployed Function App

param(
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "vcarpool-dev-api",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "vcarpool-dev-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Endpoint = "api/v1/users"
)

Write-Host "Starting Azure Function App troubleshooting..." -ForegroundColor Green

# 1. Check Function App existence and status
Write-Host "Checking if Function App $FunctionAppName exists..." -ForegroundColor Yellow
$functionApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "{name:name, state:state, defaultHostName:defaultHostName}" | ConvertFrom-Json

if (-not $functionApp) {
    Write-Host "Function App $FunctionAppName not found in resource group $ResourceGroupName" -ForegroundColor Red
    exit 1
}

Write-Host "Function App $($functionApp.name) found with status: $($functionApp.state)" -ForegroundColor Green
Write-Host "Host name: https://$($functionApp.defaultHostName)" -ForegroundColor Green

# 2. Check application settings
Write-Host "`nChecking application settings..." -ForegroundColor Yellow
$appSettings = az functionapp config appsettings list --name $FunctionAppName --resource-group $ResourceGroupName | ConvertFrom-Json

Write-Host "Found $($appSettings.Count) application settings" -ForegroundColor Green
Write-Host "Checking critical settings:" -ForegroundColor Yellow

# Check for important settings
$criticalSettings = @("FUNCTIONS_WORKER_RUNTIME", "WEBSITE_RUN_FROM_PACKAGE", "WEBSITE_CONTENTSHARE")
foreach ($setting in $criticalSettings) {
    $settingValue = ($appSettings | Where-Object { $_.name -eq $setting }).value
    if ($settingValue) {
        Write-Host "  $setting = $settingValue" -ForegroundColor Green
    } else {
        Write-Host "  $setting not found" -ForegroundColor Red
    }
}

# 3. Check Python version
Write-Host "`nChecking Python version..." -ForegroundColor Yellow
$pythonVersion = az functionapp config show --name $FunctionAppName --resource-group $ResourceGroupName --query linuxFxVersion --output tsv

if ($pythonVersion) {
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} else {
    # Try Windows function apps
    $pythonVersion = ($appSettings | Where-Object { $_.name -eq "FUNCTIONS_WORKER_RUNTIME_VERSION" }).value
    if ($pythonVersion) {
        Write-Host "Python version: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "Unable to determine Python version" -ForegroundColor Yellow
    }
}

# 4. Test API endpoints
Write-Host "`nTesting API endpoints..." -ForegroundColor Yellow

# Test root endpoint
Write-Host "Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://$($functionApp.defaultHostName)" -Method Get -ErrorAction Stop
    Write-Host "Root endpoint response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Error accessing root endpoint: $_" -ForegroundColor Red
}

# Test health check endpoint
Write-Host "`nTesting health check endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://$($functionApp.defaultHostName)/api/v1" -Method Get -ErrorAction Stop
    Write-Host "Health check endpoint response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Error accessing health check endpoint: $_" -ForegroundColor Red
}

# Test specific endpoint
Write-Host "`nTesting specific endpoint: $Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://$($functionApp.defaultHostName)/$Endpoint" -Method Get -ErrorAction Stop
    Write-Host "Endpoint response:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 3
} catch {
    Write-Host "Error accessing endpoint: $_" -ForegroundColor Red
}

# 5. Check function app logs
Write-Host "`nFetching recent function app logs (last 10)..." -ForegroundColor Yellow
az functionapp log tail --name $FunctionAppName --resource-group $ResourceGroupName --limit 10

Write-Host "`nTroubleshooting completed. Check the information above for any issues." -ForegroundColor Green
Write-Host "For more detailed logs, run: az functionapp log tail --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor Cyan
