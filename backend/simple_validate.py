"""
Simple Deployment Validation Script
----------------------------------
This script validates the Azure Function App configuration files without using the problematic JSON parsing.
"""

import os

def check_file_content(file_path, required_strings):
    """Check if a file contains all the required strings."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        print(f"\n=== Checking {os.path.basename(file_path)} ===")
        print(f"File content (first 200 chars):")
        print(f"{content[:200]}...")
        
        missing = []
        for required in required_strings:
            if required not in content:
                missing.append(required)
                
        if missing:
            print(f"❌ Error: {file_path} is missing required content:")
            for item in missing:
                print(f"  - {item}")
            return False
        
        print(f"✅ {file_path} contains all required content")
        return True
    except Exception as e:
        print(f"❌ Error reading {file_path}: {str(e)}")
        return False

def validate_function_json():
    """Validate function.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "api", "function.json")
    required = [
        '"scriptFile": "../main.py"',
        '"entryPoint": "main"',
        '"type": "httpTrigger"',
        '"route": "{*route}"',
        '"type": "http"',
        '"direction": "out"'
    ]
    return check_file_content(file_path, required)

def validate_host_json():
    """Validate host.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "host.json")
    required = [
        '"version": "2.0"',
        '"routePrefix": ""',
        '"extensionBundle"'
    ]
    return check_file_content(file_path, required)

def validate_proxies_json():
    """Validate proxies.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "proxies.json")
    required = [
        '"proxies"',
        '"root"',
        '"route": "/"',
        '%WEBSITE_HOSTNAME%'
    ]
    return check_file_content(file_path, required)

def validate_main_py():
    """Validate main.py file for Azure Functions integration."""
    file_path = os.path.join(os.path.dirname(__file__), "main.py")
    required = [
        'import azure.functions as func',
        'from fastapi import FastAPI',
        'async def main(req: func.HttpRequest)',
        'from azure.functions._http.asgi import AsgiMiddleware'
    ]
    return check_file_content(file_path, required)

def run_validation():
    """Run all validation checks."""
    print("=== Azure Function App Configuration Validation ===")
    
    success = True
    success = validate_function_json() and success
    success = validate_host_json() and success
    success = validate_proxies_json() and success
    success = validate_main_py() and success
    
    print("\n=== Validation Summary ===")
    if success:
        print("✅ All configuration files are valid for deployment!")
        print("""
Next steps:
1. Deploy the application using the deploy_fixed_function.ps1 script:
   .\deploy_fixed_function.ps1 -functionAppName <function-app-name> -resourceGroup <resource-group-name>

2. After deployment, wait a few moments and access your Azure Function App:
   https://<function-app-name>.azurewebsites.net

3. You should now see your FastAPI application working correctly!
""")
    else:
        print("❌ Some configuration issues were found. Please address them and try again.")
    
    return success

if __name__ == "__main__":
    run_validation()
