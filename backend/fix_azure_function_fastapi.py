"""
Fix Azure Function App FastAPI Integration Issues
------------------------------------------------
This script automatically fixes the Azure Function App configuration to properly integrate with the FastAPI application.
"""

import json
import os
import shutil

def backup_file(file_path):
    """Create a backup of a file."""
    if os.path.isfile(file_path):
        backup_path = f"{file_path}.bak"
        shutil.copy2(file_path, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return True
    return False

def fix_function_json():
    """Fix the function.json file to point to the main.py file."""
    function_json_path = os.path.join(os.path.dirname(__file__), "api", "function.json")
    if os.path.isfile(function_json_path):
        backup_file(function_json_path)
    
    function_json = {
        "scriptFile": "../main.py",
        "entryPoint": "main",
        "bindings": [
            {
                "authLevel": "anonymous",
                "type": "httpTrigger",
                "direction": "in",
                "name": "req",
                "methods": [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options"
                ],
                "route": "{*route}"
            },
            {
                "type": "http",
                "direction": "out",
                "name": "$return"
            }
        ]
    }
    
    with open(function_json_path, "w") as f:
        json.dump(function_json, f, indent=2)
    
    print(f"✅ Updated function.json to point to main.py")

def fix_host_json():
    """Fix the host.json file for proper routing."""
    host_json_path = os.path.join(os.path.dirname(__file__), "host.json")
    if os.path.isfile(host_json_path):
        backup_file(host_json_path)
    
    host_json = {
        "version": "2.0",
        "extensions": {
            "http": {
                "routePrefix": ""
            }
        },
        "extensionBundle": {
            "id": "Microsoft.Azure.Functions.ExtensionBundle",
            "version": "[3.*, 4.0.0)"
        }
    }
    
    with open(host_json_path, "w") as f:
        json.dump(host_json, f, indent=2)
    
    print(f"✅ Updated host.json with proper HTTP extensions configuration")

def create_proxies_json():
    """Create a proxies.json file for proper root URL handling."""
    proxies_json_path = os.path.join(os.path.dirname(__file__), "proxies.json")
    if os.path.isfile(proxies_json_path):
        backup_file(proxies_json_path)
    
    proxies_json = {
        "$schema": "http://json.schemastore.org/proxies",
        "proxies": {
            "root": {
                "matchCondition": {
                    "route": "/"
                },
                "backendUri": "https://%WEBSITE_HOSTNAME%/api"
            }
        }
    }
    
    with open(proxies_json_path, "w") as f:
        json.dump(proxies_json, f, indent=2)
    
    print(f"✅ Created proxies.json for proper root URL handling")

def create_deploy_script():
    """Create a PowerShell script for deploying the fixed application."""
    deploy_script_path = os.path.join(os.path.dirname(__file__), "deploy_fixed_function.ps1")
    
    deploy_script = """# PowerShell script to deploy the fixed Azure Function App
$functionAppName = $args[0]
$resourceGroup = $args[1]

if (-not $functionAppName -or -not $resourceGroup) {
    Write-Host "Usage: ./deploy_fixed_function.ps1 <function-app-name> <resource-group-name>"
    exit 1
}

Write-Host "Creating deployment package..."
Remove-Item -Path "deploy_fixed.zip" -ErrorAction SilentlyContinue
Compress-Archive -Path * -DestinationPath "deploy_fixed.zip" -Force

Write-Host "Deploying to Azure Function App: $functionAppName..."
az functionapp deployment source config-zip -g $resourceGroup -n $functionAppName --src "deploy_fixed.zip"

Write-Host "Restarting the Function App to apply changes..."
az functionapp restart --name $functionAppName --resource-group $resourceGroup

Write-Host "Deployment complete! Wait a few moments for the changes to take effect."
Write-Host "You can check the Function App at: https://$functionAppName.azurewebsites.net"
"""
    
    with open(deploy_script_path, "w") as f:
        f.write(deploy_script)
    
    print(f"✅ Created deployment script: deploy_fixed_function.ps1")

def main():
    print("=== Fixing Azure Function App FastAPI Integration ===\n")
    
    # Apply fixes
    fix_function_json()
    fix_host_json()
    create_proxies_json()
    create_deploy_script()
    
    print("\n=== All fixes applied ===")
    print("""
Next steps:
1. Deploy the fixed application using the deploy_fixed_function.ps1 script:
   .\deploy_fixed_function.ps1 <function-app-name> <resource-group-name>

2. After deployment, wait a few moments and access your Azure Function App:
   https://<function-app-name>.azurewebsites.net

3. You should now see your FastAPI application working correctly!
""")

if __name__ == "__main__":
    main()
