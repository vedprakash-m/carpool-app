"""
Azure Function App Fix Script
----------------------------
This script automatically fixes common issues with Azure Function Apps running FastAPI applications.
"""

import os
import json
import sys
import shutil
from pathlib import Path

def ensure_directory(path):
    """Ensure a directory exists."""
    os.makedirs(path, exist_ok=True)
    print(f"✅ Ensured directory exists: {path}")

def backup_file(file_path):
    """Create a backup of a file."""
    if not os.path.isfile(file_path):
        return False
        
    backup_path = f"{file_path}.bak"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Created backup: {backup_path}")
    return True

def fix_function_json():
    """Fix or create the function.json file."""
    function_dir = os.path.join(os.path.dirname(__file__), "api")
    function_json_path = os.path.join(function_dir, "function.json")
    
    # Create directory if it doesn't exist
    ensure_directory(function_dir)
    
    # Backup existing file
    if os.path.isfile(function_json_path):
        backup_file(function_json_path)
    
    # Create/update function.json
    function_config = {
        "scriptFile": "__init__.py",
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
    
    with open(function_json_path, "w") as file:
        json.dump(function_config, file, indent=2)
    
    print(f"✅ Created/updated function.json at: {function_json_path}")
    return True

def fix_init_py():
    """Fix or create the __init__.py file."""
    api_dir = os.path.join(os.path.dirname(__file__), "api")
    init_path = os.path.join(api_dir, "__init__.py")
    
    # Create directory if it doesn't exist
    ensure_directory(api_dir)
    
    # Backup existing file
    if os.path.isfile(init_path):
        backup_file(init_path)
    
    # Create/update __init__.py
    init_content = """import azure.functions as func
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Carpool API", 
    description="API for carpool management with mobile-friendly design. Supports admin, parent, and student roles.",
    version="0.1.0"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Carpool API is healthy!"}

# Azure Functions entry point
async def main(req: func.HttpRequest) -> func.HttpResponse:
    """Azure Functions entry point for FastAPI application."""
    from azure.functions._http.asgi import AsgiMiddleware
    asgi_handler = AsgiMiddleware(app).handle_async
    return await asgi_handler(req)
"""
    
    with open(init_path, "w") as file:
        file.write(init_content)
    
    print(f"✅ Created/updated __init__.py at: {init_path}")
    return True

def fix_proxies_json():
    """Create proxies.json file to handle root path routing."""
    proxies_path = os.path.join(os.path.dirname(__file__), "proxies.json")
    
    # Backup existing file
    if os.path.isfile(proxies_path):
        backup_file(proxies_path)
    
    # Create/update proxies.json
    proxies_config = {
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
    
    with open(proxies_path, "w") as file:
        json.dump(proxies_config, file, indent=2)
    
    print(f"✅ Created/updated proxies.json at: {proxies_path}")
    return True

def fix_host_json():
    """Fix or create the host.json file."""
    host_path = os.path.join(os.path.dirname(__file__), "host.json")
    
    # Backup existing file
    if os.path.isfile(host_path):
        backup_file(host_path)
    
    # Create/update host.json
    host_config = {
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
    
    with open(host_path, "w") as file:
        json.dump(host_config, file, indent=2)
    
    print(f"✅ Created/updated host.json at: {host_path}")
    return True

def create_deployment_zip():
    """Create a deployment ZIP file."""
    try:
        import zipfile
        
        # Define the output zip file
        zip_path = os.path.join(os.path.dirname(__file__), "function_app_deployment.zip")
        
        # Create a backup if the file already exists
        if os.path.isfile(zip_path):
            backup_file(zip_path)
        
        # Create the zip file
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files and directories in the current directory
            for root, dirs, files in os.walk(os.path.dirname(__file__)):
                # Skip the deployment zip itself and backup files
                files = [f for f in files if not f.endswith('.zip') and not f.endswith('.bak')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    # Add the file with a relative path
                    arcname = os.path.relpath(file_path, os.path.dirname(__file__))
                    zipf.write(file_path, arcname)
        
        print(f"\n✅ Created deployment ZIP file at: {zip_path}")
        print("   You can deploy this ZIP file to your Azure Function App.")
    except Exception as e:
        print(f"❌ Error creating deployment ZIP: {str(e)}")

def run_fixes():
    """Run all fixes."""
    print("=== Azure Function App FastAPI Integration Fixes ===\n")
    
    fixes = [
        ("Fix function.json", fix_function_json),
        ("Fix __init__.py", fix_init_py),
        ("Fix host.json", fix_host_json),
        ("Fix proxies.json", fix_proxies_json)
    ]
    
    for name, fix_func in fixes:
        print(f"Running: {name}")
        try:
            fix_func()
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    # Ask if user wants to create deployment ZIP
    choice = input("\nDo you want to create a deployment ZIP file? (y/n): ")
    if choice.lower() == 'y':
        create_deployment_zip()
    
    print("\n=== Fix Summary ===")
    print("✅ All fixes have been applied.")
    print("\nNext steps:")
    print("1. Run the diagnostic script to verify fixes: python diagnose_function_app.py")
    print("2. Test locally: python test_fastapi_local.py")
    print("3. Deploy to Azure Function App")
    print("   - Using ZIP file (if created)")
    print("   - Or using Azure Functions Core Tools: func azure functionapp publish <app-name>")
    print("   - Or via CI/CD pipeline")

if __name__ == "__main__":
    run_fixes()
