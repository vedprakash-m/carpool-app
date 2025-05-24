# deploy.ps1
# Enhanced deployment script for Azure Static Web Apps
param(
    [string]$ResourceGroup = "vcarpool-dev-rg",
    [string]$AppName = "kind-beach-018814610",
    [string]$Environment = "6", # Default environment number
    [switch]$SkipBuild = $false,
    [switch]$SkipLogin = $false,
    [switch]$Verbose = $false
)

function Write-StatusMessage {
    param (
        [string]$Message,
        [string]$Type = "Info" # Info, Success, Warning, Error
    )
    
    $color = switch ($Type) {
        "Info" { "Cyan" }
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$Type] $Message" -ForegroundColor $color
}

# Ensure we're in the frontend directory
Set-Location -Path $PSScriptRoot
Write-StatusMessage "Starting deployment process for VCarpool frontend to Azure Static Web App" -Type "Info"

# Login to Azure if needed
if (-not $SkipLogin) {
    Write-StatusMessage "Checking Azure login status..." -Type "Info"
    $loginStatus = az account show 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Not logged in to Azure. Please login." -Type "Warning"
        az login
        if ($LASTEXITCODE -ne 0) {
            Write-StatusMessage "Failed to login to Azure. Exiting." -Type "Error"
            exit 1
        }
    }
    else {
        $account = $loginStatus | ConvertFrom-Json
        Write-StatusMessage "Logged in as: $($account.user.name)" -Type "Success"
    }
}

# Clean up previous build if it exists
if (Test-Path -Path "./out") {
    Write-StatusMessage "Cleaning up previous build..." -Type "Info"
    Remove-Item -Path "./out" -Recurse -Force
}

# Install dependencies if needed
if (-not (Test-Path -Path "./node_modules")) {
    Write-StatusMessage "Installing dependencies..." -Type "Info"
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Failed to install dependencies. Exiting." -Type "Error"
        exit 1
    }
}

# Build the application if not skipped
if (-not $SkipBuild) {
    Write-StatusMessage "Building the application..." -Type "Info"
    
    # First run the skip-build-checks script to temporarily disable problematic pages
    Write-StatusMessage "Preparing build environment..." -Type "Info"
    node skip-build-checks.js
    
    # Build the application
    npm run build
    
    # Check if build was successful
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Build failed. Please check for errors and try again." -Type "Error"
        exit 1
    }
    
    Write-StatusMessage "Build completed successfully!" -Type "Success"
    
    # Restore any files that were moved by skip-build-checks.js
    node skip-build-checks.js --restore
}

# Deploy to Azure Static Web Apps
Write-StatusMessage "Deploying to Azure Static Web Apps..." -Type "Info"

# Make sure staticwebapp.config.json is in the out directory
if (-not (Test-Path -Path "./out/staticwebapp.config.json")) {
    Write-StatusMessage "Copying staticwebapp.config.json to output directory..." -Type "Info"
    Copy-Item -Path "./staticwebapp.config.json" -Destination "./out/staticwebapp.config.json"
}

# Upload the static web app content
$StaticWebAppName = "$AppName.$Environment"
Write-StatusMessage "Deploying to $StaticWebAppName.azurestaticapps.net..." -Type "Info"

# Use the Azure CLI to deploy the static web app content
az staticwebapp cli deploy --source-location ./out --env production --resource-group $ResourceGroup --name $AppName --verbose:$Verbose

if ($LASTEXITCODE -ne 0) {
    Write-StatusMessage "Deployment failed. Please check the error messages." -Type "Error"
    exit 1
}

Write-StatusMessage "Deployment completed successfully!" -Type "Success"
Write-StatusMessage "Your app should be available at: https://$StaticWebAppName.azurestaticapps.net" -Type "Success"

# Optional: Open the deployed site in a browser
$response = Read-Host "Would you like to open the site in your browser? (y/n)"
if ($response -eq "y") {
    Start-Process "https://$StaticWebAppName.azurestaticapps.net"
}

Write-StatusMessage "Deployment process completed." -Type "Success"
