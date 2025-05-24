# PowerShell script to deploy the fixed Azure Function App
param(
    [Parameter(Mandatory=$true)]
    [string]$functionAppName,
    
    [Parameter(Mandatory=$true)]
    [string]$resourceGroup
)

Write-Host "Creating deployment package..."
Remove-Item -Path "deploy_fixed.zip" -ErrorAction SilentlyContinue
Compress-Archive -Path * -DestinationPath "deploy_fixed.zip" -Force

Write-Host "Deploying to Azure Function App: $functionAppName..."
az functionapp deployment source config-zip -g $resourceGroup -n $functionAppName --src "deploy_fixed.zip"

Write-Host "Restarting the Function App to apply changes..."
az functionapp restart --name $functionAppName --resource-group $resourceGroup

Write-Host "Deployment complete! Wait a few moments for the changes to take effect."
Write-Host "You can check the Function App at: https://$functionAppName.azurewebsites.net"
