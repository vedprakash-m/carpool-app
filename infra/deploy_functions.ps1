# Azure Infrastructure Deployment Script for Function App
# This PowerShell script deploys the Bicep template for the Carpool Management application using Azure Functions

param(
    [Parameter(Mandatory=$false)]
    [string]$ResourceGroupName = "vcarpool-dev-rg",
    
    [Parameter(Mandatory=$false)]
    [string]$Location = "westus2",
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId,
    
    [Parameter(Mandatory=$false)]
    [switch]$WhatIf
)

# Login and set subscription if provided
if ($SubscriptionId) {
    Write-Host "Setting subscription to $SubscriptionId..." -ForegroundColor Green
    az account set --subscription $SubscriptionId
}

# Create resource group if it doesn't exist
Write-Host "Checking if resource group $ResourceGroupName exists..." -ForegroundColor Green
$rgExists = az group exists --name $ResourceGroupName --query exists --output tsv

if ($rgExists -eq "false") {
    Write-Host "Creating resource group $ResourceGroupName in $Location..." -ForegroundColor Green
    az group create --name $ResourceGroupName --location $Location
}

# Path to Bicep template and parameters file
$templateFile = Join-Path $PSScriptRoot "main_functions.bicep"
$parametersFile = Join-Path $PSScriptRoot "main_functions.parameters.json"

# Validate template without deploying if WhatIf is specified
if ($WhatIf) {
    Write-Host "Validating Bicep template deployment..." -ForegroundColor Green
    az deployment group what-if `
        --resource-group $ResourceGroupName `
        --template-file $templateFile `
        --parameters @$parametersFile
}
else {
    # Deploy the Bicep template
    Write-Host "Deploying Bicep template..." -ForegroundColor Green
    $deployment = az deployment group create `
        --resource-group $ResourceGroupName `
        --template-file $templateFile `
        --parameters @$parametersFile

    # Get the deployment outputs
    $outputs = ($deployment | ConvertFrom-Json).properties.outputs

    Write-Host "Deployment completed successfully!" -ForegroundColor Green
    Write-Host "Infrastructure Resources:" -ForegroundColor Yellow
    Write-Host "Function App Name: $($outputs.functionAppName.value)" -ForegroundColor Yellow
    Write-Host "Function App URL: https://$($outputs.functionAppHostName.value)" -ForegroundColor Yellow
    Write-Host "Key Vault Name: $($outputs.keyVaultName.value)" -ForegroundColor Yellow
    Write-Host "Static Web App Name: $($outputs.staticWebAppName.value)" -ForegroundColor Yellow
    Write-Host "Static Web App URL: https://$($outputs.staticWebAppHostName.value)" -ForegroundColor Yellow
    
    Write-Host "`nNext Steps:" -ForegroundColor Green
    Write-Host "1. Configure Key Vault secrets by running:" -ForegroundColor Green
    Write-Host "   ./set-key-vault-secrets.ps1 -KeyVaultName $($outputs.keyVaultName.value)" -ForegroundColor Cyan
    Write-Host "2. Deploy your backend application to the Function App" -ForegroundColor Green
    Write-Host "3. Deploy your frontend application to the Static Web App" -ForegroundColor Green
}
