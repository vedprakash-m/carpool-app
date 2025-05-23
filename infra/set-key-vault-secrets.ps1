# filepath: infra/set-key-vault-secrets.ps1
# Azure Key Vault Secrets Setup Script
# This PowerShell script sets up the necessary secrets in Azure Key Vault for the Carpool Management application

param(
    [Parameter(Mandatory=$true)]
    [string]$KeyVaultName,
    
    [Parameter(Mandatory=$false)]
    [string]$SubscriptionId
)

# Login and set subscription if provided
if ($SubscriptionId) {
    Write-Host "Setting subscription to $SubscriptionId..." -ForegroundColor Green
    az account set --subscription $SubscriptionId
}

# Verify Key Vault exists
Write-Host "Verifying Key Vault '$KeyVaultName' exists..." -ForegroundColor Green
$keyVaultExists = az keyvault show --name $KeyVaultName --query id --output tsv 2>$null

if (-not $keyVaultExists) {
    Write-Host "Key Vault '$KeyVaultName' not found. Please check the name and ensure it exists." -ForegroundColor Red
    exit 1
}

# Prompt for secret values
Write-Host "Please provide the following secret values for your application:" -ForegroundColor Yellow

$cosmosEndpoint = Read-Host -Prompt "Enter Cosmos DB Endpoint URL"
$cosmosKey = Read-Host -Prompt "Enter Cosmos DB Key" -AsSecureString
$jwtSecretKey = Read-Host -Prompt "Enter JWT Secret Key (should be a strong random string)" -AsSecureString

# Convert secure strings to plain text for Azure CLI
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($cosmosKey)
$cosmosKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($jwtSecretKey)
$jwtSecretKeyPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Store secrets in Key Vault
Write-Host "Storing secrets in Key Vault..." -ForegroundColor Green

# Set Azure Key Vault secrets
Write-Host "Setting COSMOS-ENDPOINT secret..." -ForegroundColor Green
az keyvault secret set --vault-name $KeyVaultName --name "COSMOS-ENDPOINT" --value $cosmosEndpoint

Write-Host "Setting COSMOS-KEY secret..." -ForegroundColor Green
az keyvault secret set --vault-name $KeyVaultName --name "COSMOS-KEY" --value $cosmosKeyPlain

Write-Host "Setting JWT-SECRET-KEY secret..." -ForegroundColor Green
az keyvault secret set --vault-name $KeyVaultName --name "JWT-SECRET-KEY" --value $jwtSecretKeyPlain

Write-Host "Secrets have been stored in Key Vault!" -ForegroundColor Green
Write-Host "Your application is now configured with the following secrets:" -ForegroundColor Yellow
Write-Host "- COSMOS-ENDPOINT" -ForegroundColor Yellow
Write-Host "- COSMOS-KEY" -ForegroundColor Yellow
Write-Host "- JWT-SECRET-KEY" -ForegroundColor Yellow
