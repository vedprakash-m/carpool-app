"""
Deployment Validation Test Script
--------------------------------
This script validates that the Azure Function App configuration is correct for deployment.
"""

import os
import json
import sys

def validate_file(file_path):
    """Validate that a file exists and is valid JSON."""
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Print raw file content for debugging
            print(f"Raw content of {file_path}:")
            print(content[:200] + "..." if len(content) > 200 else content)
            print()
            
            # Remove any comments (lines starting with //)
            lines = content.split('\n')
            clean_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped.startswith('//'):
                    clean_lines.append(line)
            
            clean_content = '\n'.join(clean_lines)
            
            # Print cleaned content for debugging
            print(f"Cleaned content of {file_path}:")
            print(clean_content[:200] + "..." if len(clean_content) > 200 else clean_content)
            print()
            
            # Parse the JSON
            data = json.loads(clean_content)
            print(f"✅ {file_path} is valid JSON")
            return True
    except json.JSONDecodeError as e:
        print(f"❌ Error: {file_path} contains invalid JSON: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error reading {file_path}: {str(e)}")
        return False

def validate_function_json():
    """Validate function.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "api", "function.json")
    if not validate_file(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Remove any comments (lines starting with //)
            lines = content.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('//')]
            clean_content = '\n'.join(clean_lines)
            
            data = json.loads(clean_content)
            
            script_file = data.get("scriptFile")
            if script_file != "../main.py":
                print(f"❌ Error: scriptFile should be '../main.py', but is '{script_file}'")
                return False
                
            entry_point = data.get("entryPoint")
            if entry_point != "main":
                print(f"❌ Error: entryPoint should be 'main', but is '{entry_point}'")
                return False
                
            bindings = data.get("bindings", [])
            if not bindings:
                print("❌ Error: No bindings found in function.json")
                return False
                
            http_trigger = next((b for b in bindings if b.get("type") == "httpTrigger"), None)
            if not http_trigger:
                print("❌ Error: No httpTrigger binding found in function.json")
                return False
                
            route = http_trigger.get("route")
            if route != "{*route}":
                print(f"❌ Error: route should be '{{*route}}', but is '{route}'")
                return False
                
            methods = http_trigger.get("methods", [])
            required_methods = ["get", "post", "put", "delete"]
            for method in required_methods:
                if method not in methods:
                    print(f"❌ Error: '{method}' method not found in function.json")
                    return False
                    
            http_output = next((b for b in bindings if b.get("type") == "http" and b.get("direction") == "out"), None)
            if not http_output:
                print("❌ Error: No HTTP output binding found in function.json")
                return False
                
            print("✅ function.json is correctly configured for FastAPI")
            return True
    except Exception as e:
        print(f"❌ Error validating function.json: {str(e)}")
        return False

def validate_host_json():
    """Validate host.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "host.json")
    if not validate_file(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Remove any comments (lines starting with //)
            lines = content.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('//')]
            clean_content = '\n'.join(clean_lines)
            
            data = json.loads(clean_content)
            
            version = data.get("version")
            if version != "2.0":
                print(f"❌ Error: version should be '2.0', but is '{version}'")
                return False
                
            extensions = data.get("extensions", {})
            http_ext = extensions.get("http", {})
            route_prefix = http_ext.get("routePrefix")
            if route_prefix != "":
                print(f"❌ Error: routePrefix should be empty string, but is '{route_prefix}'")
                return False
                
            ext_bundle = data.get("extensionBundle", {})
            if not ext_bundle:
                print("❌ Error: No extensionBundle found in host.json")
                return False
                
            print("✅ host.json is correctly configured")
            return True
    except Exception as e:
        print(f"❌ Error validating host.json: {str(e)}")
        return False

def validate_proxies_json():
    """Validate proxies.json file."""
    file_path = os.path.join(os.path.dirname(__file__), "proxies.json")
    if not validate_file(file_path):
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Remove any comments (lines starting with //)
            lines = content.split('\n')
            clean_lines = [line for line in lines if not line.strip().startswith('//')]
            clean_content = '\n'.join(clean_lines)
            
            data = json.loads(clean_content)
            
            proxies = data.get("proxies", {})
            if not proxies:
                print("❌ Error: No proxies found in proxies.json")
                return False
                
            root_proxy = proxies.get("root")
            if not root_proxy:
                print("❌ Error: No 'root' proxy found in proxies.json")
                return False
                
            match_condition = root_proxy.get("matchCondition", {})
            route = match_condition.get("route")
            if route != "/":
                print(f"❌ Error: root proxy route should be '/', but is '{route}'")
                return False
                
            backend_uri = root_proxy.get("backendUri")
            if not backend_uri or "%WEBSITE_HOSTNAME%" not in backend_uri:
                print(f"❌ Error: backendUri should contain '%WEBSITE_HOSTNAME%', but is '{backend_uri}'")
                return False
                
            print("✅ proxies.json is correctly configured")
            return True
    except Exception as e:
        print(f"❌ Error validating proxies.json: {str(e)}")
        return False

def validate_main_py():
    """Validate main.py file for Azure Functions integration."""
    file_path = os.path.join(os.path.dirname(__file__), "main.py")
    if not os.path.exists(file_path):
        print(f"❌ Error: {file_path} does not exist")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
            # Check for essential imports and functions
            if "import azure.functions as func" not in content:
                print("❌ Error: 'import azure.functions as func' not found in main.py")
                return False
                
            if "from fastapi import FastAPI" not in content:
                print("❌ Error: 'from fastapi import FastAPI' not found in main.py")
                return False
                
            if "async def main(req: func.HttpRequest)" not in content:
                print("❌ Error: 'async def main(req: func.HttpRequest)' function not found in main.py")
                return False
                
            if "from azure.functions._http.asgi import AsgiMiddleware" not in content:
                print("❌ Error: 'from azure.functions._http.asgi import AsgiMiddleware' not found in main.py")
                return False
                
            print("✅ main.py is correctly configured for Azure Functions and FastAPI integration")
            return True
    except Exception as e:
        print(f"❌ Error validating main.py: {str(e)}")
        return False

def run_validation():
    """Run all validation checks."""
    print("=== Azure Function App Configuration Validation ===\n")
    
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
