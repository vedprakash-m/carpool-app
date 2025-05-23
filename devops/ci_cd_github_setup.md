# CI/CD Setup Guide for Carpool Management Application

This guide explains how to set up the CI/CD pipeline for the Carpool Management application using GitHub Actions and Azure services.

## Prerequisites

Before setting up the CI/CD pipeline, ensure you have:

1. An Azure account with appropriate permissions to create resources
2. A GitHub repository for the Carpool Management application
3. GitHub CLI or access to GitHub repository settings

## Required GitHub Secrets

The CI/CD pipeline requires the following secrets to be configured in your GitHub repository:

### 1. Azure Authentication Secrets

These secrets are used for authenticating with Azure from GitHub Actions:

- `AZURE_CLIENT_ID`: The client ID of your Azure service principal
- `AZURE_TENANT_ID`: The tenant ID of your Azure service principal
- `AZURE_SUBSCRIPTION_ID`: Your Azure subscription ID

To create these secrets:

```bash
# Install Azure CLI if you haven't already
# https://docs.microsoft.com/en-us/cli/azure/install-azure-cli

# Login to Azure
az login

# Create a service principal for GitHub Actions
# Replace <subscription-id> with your Azure subscription ID
SUBSCRIPTION_ID=$(az account show --query id -o tsv)
SERVICE_PRINCIPAL=$(az ad sp create-for-rbac --name "carpool-github-actions" \
                                            --role Contributor \
                                            --scopes /subscriptions/$SUBSCRIPTION_ID)

# Extract the required values
CLIENT_ID=$(echo $SERVICE_PRINCIPAL | jq -r .appId)
TENANT_ID=$(echo $SERVICE_PRINCIPAL | jq -r .tenant)

# Output the values to use for GitHub secrets
echo "AZURE_CLIENT_ID: $CLIENT_ID"
echo "AZURE_TENANT_ID: $TENANT_ID"
echo "AZURE_SUBSCRIPTION_ID: $SUBSCRIPTION_ID"
```

### 2. `AZURE_STATIC_WEB_APPS_API_TOKEN`

This token is used to deploy the frontend to Azure Static Web Apps. To obtain this token:

1. After running the initial infrastructure deployment, go to the Azure Portal
2. Navigate to the Static Web App resource that was created
3. Go to "Overview" and click on "Manage deployment token"
4. Copy the deployment token
5. Add it as a GitHub repository secret named `AZURE_STATIC_WEB_APPS_API_TOKEN`

## Setting Up GitHub Secrets

To add these secrets to your GitHub repository:

### Using GitHub CLI

```bash
# Install GitHub CLI if you haven't already
# https://cli.github.com/

# Set the secrets
gh secret set AZURE_CLIENT_ID -b"$CLIENT_ID"
gh secret set AZURE_TENANT_ID -b"$TENANT_ID"
gh secret set AZURE_SUBSCRIPTION_ID -b"$SUBSCRIPTION_ID"

# Set AZURE_STATIC_WEB_APPS_API_TOKEN (replace <token> with your actual token)
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN -b"<token>"
```

### Using GitHub Web Interface

1. Navigate to your GitHub repository
2. Go to Settings > Secrets > Actions
3. Click "New repository secret"
4. Add each secret with its appropriate name and value

## CI/CD Pipeline Overview

The CI/CD pipeline consists of the following jobs:

1. **validate-infrastructure**: Validates the Bicep template
2. **build-and-test-backend**: Builds and tests the backend application
3. **build-and-test-frontend**: Builds and tests the frontend application
4. **deploy-infrastructure**: Deploys the Azure infrastructure using Bicep
5. **deploy-backend**: Deploys the backend to Azure App Service
6. **deploy-frontend**: Deploys the frontend to Azure Static Web App

The pipeline is triggered on:
- Push to the main branch
- Pull requests to the main branch
- Manual workflow dispatch with environment selection

## Environment Selection

When triggering the workflow manually, you can select the target environment:
- `dev` (default)
- `test`
- `prod`

This will deploy the infrastructure and applications to the selected environment, creating environment-specific resource groups and resources.

## First-Time Setup

For the first-time setup of the application, follow these steps:

1. Configure the GitHub secrets as described above
2. Manually trigger the workflow with the desired environment
3. After the infrastructure is deployed, configure the Key Vault secrets:
   - Obtain the Key Vault name from the workflow output
   - Run the `set-key-vault-secrets.ps1` script to set up the required secrets

## Troubleshooting

If you encounter issues with the CI/CD pipeline:

1. Check the workflow run logs for specific error messages
2. Verify that all required secrets are configured correctly
3. Ensure that the service principal has the necessary permissions in Azure
4. Check that the Azure resources are properly configured and accessible

For persistent issues, examine the detailed logs in each job step and check Azure resource health in the Azure Portal.
