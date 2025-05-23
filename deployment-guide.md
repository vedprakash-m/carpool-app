# Deployment Guide

## CI/CD Pipeline Setup

The carpool management application includes a complete CI/CD pipeline using GitHub Actions, which automates testing and deployment to Azure services. This guide explains how to set up and use the CI/CD pipeline.

## Overview

The CI/CD pipeline consists of:

1. **GitHub Actions Workflows**:
   - Located in `.github/workflows/main.yml`
   - Triggers on pushes to main branch, pull requests, and manual triggers

2. **Deployment Scripts**:
   - Located in the `devops` folder
   - Setup scripts for Azure infrastructure and Key Vault secrets

3. **Configuration Files**:
   - `frontend/staticwebapp.config.json` for Azure Static Web Apps configuration

## Azure Resources

The application requires the following Azure resources:

1. **Azure App Service**: Hosts the backend FastAPI application
2. **Azure Key Vault**: Securely stores application secrets
3. **Azure Cosmos DB**: Database for application data
4. **Azure Static Web Apps**: Hosts the frontend Next.js application

## Initial Setup

### 1. Create Azure Resources

Run the infrastructure setup script:

```powershell
./devops/setup_azure_infrastructure.ps1
```

This script creates:
- Resource Group
- App Service Plan
- Web App for the backend
- Key Vault with RBAC authorization
- Static Web App for the frontend

### 2. Configure Key Vault Secrets

Run the Key Vault secrets setup script:

```powershell
./devops/setup_key_vault_secrets.ps1
```

This script prompts for and securely stores:
- Cosmos DB Endpoint
- Cosmos DB Key
- JWT Secret Key

### 3. Set Up GitHub Secrets

Add the following secrets to your GitHub repository:

- **AZURE_CREDENTIALS**: Azure Service Principal credentials
  ```bash
  # Create a service principal
  az ad sp create-for-rbac --name "carpool-app-cicd" --role contributor \
    --scopes /subscriptions/<subscription-id>/resourceGroups/carpool-app-rg \
    --sdk-auth
  ```
  Add the entire JSON output as the secret value.

- **AZURE_STATIC_WEB_APPS_API_TOKEN**: Deployment token for Static Web App
  This is available in the Azure Portal under your Static Web App resource.

## CI/CD Workflow

The GitHub Actions workflow includes the following jobs:

1. **build-and-test-backend**:
   - Runs on every push and pull request
   - Sets up Python environment
   - Installs dependencies
   - Runs pytest tests

2. **build-and-test-frontend**:
   - Runs on every push and pull request
   - Sets up Node.js environment
   - Installs dependencies
   - Runs Jest tests

3. **deploy-backend**:
   - Runs only on pushes to main branch or manual triggers
   - Creates a deployment package with web.config
   - Deploys to Azure App Service
   - Configures app settings with Key Vault references

4. **deploy-frontend**:
   - Runs only on pushes to main branch or manual triggers
   - Builds the Next.js application
   - Deploys to Azure Static Web Apps

## Manual Deployment

You can manually trigger the deployment workflow:

1. Go to the Actions tab in your GitHub repository
2. Select the "Carpool App CI/CD Pipeline" workflow
3. Click "Run workflow"
4. Select the branch and environment
5. Click "Run workflow"

## Troubleshooting

If you encounter issues with the CI/CD pipeline:

1. **Authentication errors**:
   - Verify the AZURE_CREDENTIALS secret is correctly formatted
   - Check if the service principal has sufficient permissions

2. **Backend deployment failures**:
   - Check the deployment logs in GitHub Actions
   - Verify the web.config file is correctly formatted
   - Ensure all required environment variables are set

3. **Frontend deployment failures**:
   - Check the deployment logs in GitHub Actions
   - Verify the staticwebapp.config.json file is correctly formatted
   - Ensure the build process completes successfully

4. **Environment variable issues**:
   - Verify Key Vault references are correctly formatted
   - Check if the web app's managed identity has access to Key Vault
   - Ensure all required secrets are present in Key Vault

## Monitoring Deployments

You can monitor deployments in the following ways:

1. **GitHub Actions**: Check the Actions tab for workflow run status
2. **Azure Portal**: Check the deployment center in your App Service resource
3. **Application Logs**: Check the logs in your App Service resource
4. **Azure Monitor**: Set up alerts for deployment failures

## Security Considerations

The CI/CD pipeline follows these security best practices:

1. **No hardcoded secrets**: All secrets are stored in GitHub Secrets or Azure Key Vault
2. **Managed identities**: The web app uses managed identity to access Key Vault
3. **Principle of least privilege**: Service principals have only necessary permissions
4. **Secret rotation**: Regularly rotate service principal credentials

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure App Service Deployment](https://docs.microsoft.com/en-us/azure/app-service/deploy-github-actions)
- [Azure Static Web Apps Deployment](https://docs.microsoft.com/en-us/azure/static-web-apps/github-actions-workflow)
- [Azure Key Vault References](https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references)
