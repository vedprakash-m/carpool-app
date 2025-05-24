# Deploy Azure Function App with FastAPI
# This script properly packages and deploys your FastAPI application as an Azure Function

param(
    [Parameter(Mandatory=$false)]
    [string]$FunctionAppName = "vcarpool-dev-api",
    
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "vcarpool-dev-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$SourceFolder = ".",
    
    [Parameter(Mandatory=$false)]
    [string]$DeploymentPackage = "./function-app-deploy.zip"
)

$ErrorActionPreference = "Stop"

Write-Host "Starting Azure Function App Deployment..." -ForegroundColor Green

# 1. Validate function app existence
Write-Host "Checking if Function App $FunctionAppName exists..." -ForegroundColor Yellow
$functionApp = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query "name" --output tsv 2>$null

if (-not $functionApp) {
    Write-Host "Function App $FunctionAppName not found in resource group $ResourceGroupName" -ForegroundColor Red
    Write-Host "Please deploy the infrastructure first" -ForegroundColor Red
    exit 1
}

# 2. Prepare deployment package
Write-Host "Preparing deployment package..." -ForegroundColor Yellow

# Create temp directory for deployment files
$tempDir = Join-Path $env:TEMP "function-deploy-$(Get-Random)"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Write-Host "Created temporary directory: $tempDir" -ForegroundColor Yellow

try {
    # Copy necessary files
    Write-Host "Copying source files..." -ForegroundColor Yellow
    
    # Core function files
    Copy-Item -Path "$SourceFolder\api" -Destination $tempDir -Recurse
    Copy-Item -Path "$SourceFolder\app" -Destination $tempDir -Recurse
    
    # Configuration files
    Copy-Item -Path "$SourceFolder\requirements.txt" -Destination $tempDir
    Copy-Item -Path "$SourceFolder\host.json" -Destination $tempDir
    
    # Ensure __init__.py is properly set
    if (-not (Test-Path "$tempDir\api\__init__.py")) {
        Write-Host "Warning: api\__init__.py not found, creating it..." -ForegroundColor Yellow
        New-Item -ItemType File -Path "$tempDir\api\__init__.py" -Force | Out-Null
    }

    # Copy main.py to the root
    if (Test-Path "$SourceFolder\main.py") {
        Copy-Item -Path "$SourceFolder\main.py" -Destination $tempDir
    } else {
        Write-Host "Warning: main.py not found in source folder, app may not function correctly" -ForegroundColor Yellow
    }

    # Create deployment package
    Write-Host "Creating ZIP package..." -ForegroundColor Yellow
    if (Test-Path $DeploymentPackage) {
        Remove-Item $DeploymentPackage -Force
    }

    $compress = @{
        Path = "$tempDir\*"
        CompressionLevel = "Optimal"
        DestinationPath = $DeploymentPackage
    }
    Compress-Archive @compress

    if (-not (Test-Path $DeploymentPackage)) {
        Write-Host "Failed to create deployment package at $DeploymentPackage" -ForegroundColor Red
        exit 1
    }

    Write-Host "Deployment package created at $DeploymentPackage" -ForegroundColor Green

    # 3. Deploy to Azure Function App
    Write-Host "Deploying to Azure Function App $FunctionAppName..." -ForegroundColor Yellow
    az functionapp deployment source config-zip `
        --resource-group $ResourceGroupName `
        --name $FunctionAppName `
        --src $DeploymentPackage

    # 4. Verify deployment
    Write-Host "Verifying deployment..." -ForegroundColor Yellow
    $hostName = az functionapp show --name $FunctionAppName --resource-group $ResourceGroupName --query defaultHostName --output tsv
    
    Write-Host "Function App deployed successfully!" -ForegroundColor Green
    Write-Host "Function App URL: https://$hostName" -ForegroundColor Cyan
    Write-Host "API URL: https://$hostName/api/v1" -ForegroundColor Cyan
    
    Write-Host "`nNOTE: It may take a few minutes for your Function App to fully initialize after deployment" -ForegroundColor Yellow
    Write-Host "If you see 'Function not found' errors, wait a few minutes and try again" -ForegroundColor Yellow
    
    Write-Host "`nTo check logs, run:" -ForegroundColor Green
    Write-Host "az functionapp log tail --name $FunctionAppName --resource-group $ResourceGroupName" -ForegroundColor White
    
} finally {
    # Cleanup
    if (Test-Path $tempDir) {
        Write-Host "Cleaning up temporary files..." -ForegroundColor Yellow
        Remove-Item -Path $tempDir -Recurse -Force
    }
}
