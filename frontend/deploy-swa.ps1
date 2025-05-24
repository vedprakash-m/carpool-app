# deploy-swa.ps1
# A simplified deployment script for Azure Static Web Apps using the SWA CLI

param(
    [string]$ResourceGroup = "vcarpool-dev-rg",
    [string]$AppName = "vcarpool-dev-frontend"
)

Write-Host "Starting deployment with SWA CLI..." -ForegroundColor Cyan

# Ensure we're in the frontend directory
Set-Location -Path $PSScriptRoot

# Check if out directory exists
if (-not (Test-Path -Path "./out")) {
    Write-Host "Building the application..." -ForegroundColor Yellow
    npm run build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed. Please check for errors and try again." -ForegroundColor Red
        exit 1
    }
}

# Ensure staticwebapp.config.json is in the out directory
if (-not (Test-Path -Path "./out/staticwebapp.config.json")) {
    Write-Host "Copying staticwebapp.config.json to output directory..." -ForegroundColor Yellow
    Copy-Item -Path "./staticwebapp.config.json" -Destination "./out/staticwebapp.config.json"
}

# Deploy using SWA CLI
Write-Host "Deploying to Azure Static Web App..." -ForegroundColor Cyan

# Login to Azure if needed
$loginStatus = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Please login to Azure..." -ForegroundColor Yellow
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to login to Azure. Exiting." -ForegroundColor Red
        exit 1
    }
}

# Get the deployment token from the Azure CLI
Write-Host "Getting deployment token..." -ForegroundColor Cyan
$deploymentToken = az staticwebapp secrets list --name $AppName --resource-group $ResourceGroup --query "properties.apiKey" -o tsv

if ($LASTEXITCODE -ne 0 -or -not $deploymentToken) {
    Write-Host "Failed to get deployment token. Make sure you have access to the static web app." -ForegroundColor Red
    exit 1
}

# Deploy using the SWA CLI
Write-Host "Deploying to $AppName.azurestaticapps.net..." -ForegroundColor Cyan
swa deploy ./out --deployment-token $deploymentToken --env production

if ($LASTEXITCODE -ne 0) {
    Write-Host "Deployment failed. Please check the error messages." -ForegroundColor Red
    exit 1
}

Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "Your app should be available at: https://$AppName.azurestaticapps.net" -ForegroundColor Green

# Optional: Open the deployed site in a browser
$response = Read-Host "Would you like to open the site in your browser? (y/n)"
if ($response -eq "y") {
    Start-Process "https://kind-beach-018814610.6.azurestaticapps.net"
}
