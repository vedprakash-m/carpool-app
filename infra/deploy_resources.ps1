# Deploy Azure resources for Carpool Management Application
# This script creates the necessary Azure resources using Azure CLI commands

# Parameters
$resourcePrefix = "vcarpool"
$environment = "dev"
$location = "westus2"
$resourceGroupName = "$resourcePrefix-$environment-rg"

# Variables
$resourceToken = "$resourcePrefix-$environment"
$storageAccountName = "$($resourceToken -replace '-', '')stor"
$functionAppName = "$resourceToken-api"
$keyVaultName = "$resourceToken-vault"
$staticWebAppName = "$resourceToken-frontend"

# Create Resource Group
Write-Host "Creating resource group $resourceGroupName..." -ForegroundColor Green
az group create --name $resourceGroupName --location $location

# Create Storage Account for Function App
Write-Host "Creating storage account $storageAccountName..." -ForegroundColor Green
az storage account create `
    --name $storageAccountName `
    --resource-group $resourceGroupName `
    --location $location `
    --sku Standard_LRS `
    --kind StorageV2 `
    --https-only true `
    --min-tls-version TLS1_2

# Get storage account connection string
$storageConnectionString = az storage account show-connection-string `
    --name $storageAccountName `
    --resource-group $resourceGroupName `
    --query connectionString `
    --output tsv

# Create Key Vault
Write-Host "Creating Key Vault $keyVaultName..." -ForegroundColor Green
az keyvault create `
    --name $keyVaultName `
    --resource-group $resourceGroupName `
    --location $location `
    --enable-rbac-authorization true

# Create Function App
Write-Host "Creating Function App $functionAppName..." -ForegroundColor Green
az functionapp create `
    --name $functionAppName `
    --resource-group $resourceGroupName `
    --storage-account $storageAccountName `
    --consumption-plan-location $location `
    --runtime python `
    --runtime-version 3.12 `
    --functions-version 4 `
    --os-type Linux

# Enable managed identity for Function App
Write-Host "Enabling managed identity for Function App..." -ForegroundColor Green
$functionAppIdentity = az functionapp identity assign `
    --name $functionAppName `
    --resource-group $resourceGroupName `
    --query principalId `
    --output tsv

# Create Static Web App
Write-Host "Creating Static Web App $staticWebAppName..." -ForegroundColor Green
az staticwebapp create `
    --name $staticWebAppName `
    --resource-group $resourceGroupName `
    --location $location `
    --sku Free

# Assign Key Vault access to Function App
Write-Host "Assigning Key Vault access to Function App..." -ForegroundColor Green
az role assignment create `
    --assignee $functionAppIdentity `
    --role "Key Vault Secrets User" `
    --scope "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$resourceGroupName/providers/Microsoft.KeyVault/vaults/$keyVaultName"

# Configure Function App settings to use Key Vault references
Write-Host "Configuring Function App settings..." -ForegroundColor Green
az functionapp config appsettings set `
    --name $functionAppName `
    --resource-group $resourceGroupName `
    --settings "COSMOS_ENDPOINT=@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/COSMOS-ENDPOINT/)" `
              "COSMOS_KEY=@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/COSMOS-KEY/)" `
              "JWT_SECRET_KEY=@Microsoft.KeyVault(SecretUri=https://$keyVaultName.vault.azure.net/secrets/JWT-SECRET-KEY/)"

# Output resource information
Write-Host "`nDeployment completed successfully!" -ForegroundColor Green
Write-Host "Infrastructure Resources:" -ForegroundColor Yellow
Write-Host "Function App Name: $functionAppName" -ForegroundColor Yellow
Write-Host "Function App URL: https://$functionAppName.azurewebsites.net" -ForegroundColor Yellow
Write-Host "Key Vault Name: $keyVaultName" -ForegroundColor Yellow
Write-Host "Static Web App Name: $staticWebAppName" -ForegroundColor Yellow

Write-Host "`nNext Steps:" -ForegroundColor Green
Write-Host "1. Configure Key Vault secrets by running:" -ForegroundColor Green
Write-Host "   .\set-key-vault-secrets.ps1 -KeyVaultName $keyVaultName" -ForegroundColor Cyan
Write-Host "2. Deploy your backend application to the Function App" -ForegroundColor Green
Write-Host "3. Deploy your frontend application to the Static Web App" -ForegroundColor Green
