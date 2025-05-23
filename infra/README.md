# Azure Infrastructure for Carpool Management Application

This folder contains Bicep templates and scripts for deploying the Azure infrastructure required by the Carpool Management application.

## Infrastructure Components

The Bicep template provisions the following Azure resources:

- **Azure App Service Plan**: Hosts the backend API application
- **Azure Web App**: Runs the Python-based backend API
- **Azure Key Vault**: Securely stores application secrets
- **Azure Static Web App**: Hosts the frontend Next.js application

## Prerequisites

Before deploying, ensure you have the following installed:

- [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- [PowerShell](https://docs.microsoft.com/en-us/powershell/scripting/install/installing-powershell) (version 7.0 or later recommended)
- Azure subscription with sufficient permissions to create resources

## Deployment Steps

### 1. Login to Azure

```powershell
az login
```

### 2. Deploy the infrastructure

```powershell
# Preview changes without deploying (recommended first step)
./deploy.ps1 -WhatIf

# Deploy the infrastructure
./deploy.ps1
```

You can customize the deployment by providing parameters:

```powershell
./deploy.ps1 -ResourceGroupName "my-carpool-rg" -Location "eastus" -SubscriptionId "your-subscription-id"
```

### 3. Set up Key Vault secrets

After deployment, configure the required secrets in Key Vault:

```powershell
./set-key-vault-secrets.ps1 -KeyVaultName "vault-name-from-deployment-output"
```

## CI/CD Integration

This infrastructure is designed to work with the GitHub Actions CI/CD workflows defined in `.github/workflows/main.yml`. The workflows deploy:

1. The backend Python application to Azure App Service
2. The frontend Next.js application to Azure Static Web App

## Customization

You can customize the deployment by modifying the following files:

- `main.bicep`: The main Bicep template defining all resources
- `main.parameters.json`: Parameter values for the Bicep template

## Additional Notes

- **Managed Identity**: The Web App is configured with a system-assigned managed identity that has access to Key Vault secrets.
- **CORS**: The Web App is configured to allow cross-origin requests from any origin.
- **HTTPS**: Both the Web App and Static Web App enforce HTTPS for all traffic.
