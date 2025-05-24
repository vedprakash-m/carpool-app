"""
Azure Function App Diagnostic Script
-----------------------------------
This script helps diagnose issues with Azure Function Apps running FastAPI applications.
It checks for common configuration issues and provides suggestions for fixes.
"""

import os
import json
import sys
import importlib.util
import inspect

def check_file_exists(file_path):
    """Check if a file exists and return its status."""
    exists = os.path.isfile(file_path)
    print(f"Checking {file_path}: {'✅ Exists' if exists else '❌ Not found'}")
    return exists

def validate_function_json():
    """Validate the function.json file configuration."""
    try:
        function_json_path = os.path.join(os.path.dirname(__file__), "api", "function.json")
        if not check_file_exists(function_json_path):
            return False
        
        with open(function_json_path, "r") as file:
            config = json.load(file)
            
        # Check for required fields
        print("\nValidating function.json configuration...")
        
        script_file = config.get("scriptFile")
        entry_point = config.get("entryPoint")
        bindings = config.get("bindings", [])
        
        if not script_file:
            print("❌ Missing 'scriptFile' in function.json")
            return False
            
        if not entry_point:
            print("❌ Missing 'entryPoint' in function.json")
            return False
            
        if not bindings:
            print("❌ Missing 'bindings' in function.json")
            return False
            
        # Check HTTP trigger configuration
        http_trigger = next((b for b in bindings if b.get("type") == "httpTrigger"), None)
        if not http_trigger:
            print("❌ Missing 'httpTrigger' binding in function.json")
            return False
            
        route = http_trigger.get("route")
        if route != "{*route}":
            print(f"⚠️ 'route' parameter is '{route}', but should be '{{*route}}' for FastAPI integration")
            
        methods = http_trigger.get("methods", [])
        required_methods = ["get", "post", "put", "delete", "patch", "head", "options"]
        missing_methods = [m for m in required_methods if m not in methods]
        if missing_methods:
            print(f"⚠️ Missing HTTP methods in function.json: {missing_methods}")
            
        # Check HTTP output binding
        http_output = next((b for b in bindings if b.get("type") == "http" and b.get("direction") == "out"), None)
        if not http_output:
            print("❌ Missing HTTP output binding in function.json")
            return False
            
        print("✅ function.json appears to be correctly configured")
        return True
    except Exception as e:
        print(f"❌ Error validating function.json: {str(e)}")
        return False

def validate_init_file():
    """Validate the __init__.py file for proper FastAPI integration."""
    try:
        init_path = os.path.join(os.path.dirname(__file__), "api", "__init__.py")
        if not check_file_exists(init_path):
            return False
            
        print("\nValidating FastAPI integration in __init__.py...")
        
        # Check if we can import the module
        spec = importlib.util.spec_from_file_location("api_init", init_path)
        if not spec or not spec.loader:
            print("❌ Cannot load __init__.py as a module")
            return False
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check for app definition
        if not hasattr(module, "app"):
            print("❌ No FastAPI 'app' instance found in __init__.py")
            return False
        
        # Check for main function
        if not hasattr(module, "main"):
            print("❌ No 'main' function found in __init__.py")
            return False
            
        main_func = getattr(module, "main")
        if not inspect.iscoroutinefunction(main_func):
            print("⚠️ 'main' function is not async, which might cause issues")
            
        # Check for AsgiMiddleware usage
        with open(init_path, "r") as file:
            content = file.read()
            if "AsgiMiddleware" not in content:
                print("❌ 'AsgiMiddleware' not found in __init__.py - required for FastAPI integration")
                return False
                
        print("✅ __init__.py appears to be correctly configured")
        return True
    except Exception as e:
        print(f"❌ Error validating __init__.py: {str(e)}")
        return False

def validate_requirements():
    """Validate the requirements.txt file for necessary dependencies."""
    try:
        req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        if not check_file_exists(req_path):
            return False
            
        print("\nValidating requirements.txt...")
        
        with open(req_path, "r") as file:
            content = file.read().lower()
            
        required_packages = ["fastapi", "azure-functions"]
        missing = []
        
        for package in required_packages:
            if package.lower() not in content:
                missing.append(package)
                
        if missing:
            print(f"❌ Missing required packages in requirements.txt: {missing}")
            return False
            
        print("✅ requirements.txt contains necessary dependencies")
        return True
    except Exception as e:
        print(f"❌ Error validating requirements.txt: {str(e)}")
        return False

def check_host_json():
    """Check the host.json file configuration."""
    try:
        host_path = os.path.join(os.path.dirname(__file__), "host.json")
        if not check_file_exists(host_path):
            return False
            
        print("\nValidating host.json...")
        
        with open(host_path, "r") as file:
            config = json.load(file)
            
        version = config.get("version")
        if version != "2.0":
            print(f"⚠️ 'version' in host.json is '{version}', but should be '2.0'")
            
        ext_bundle = config.get("extensionBundle", {})
        if not ext_bundle:
            print("⚠️ No 'extensionBundle' configuration in host.json")
            
        print("✅ host.json appears to be correctly configured")
        return True
    except Exception as e:
        print(f"❌ Error validating host.json: {str(e)}")
        return False

def check_local_settings():
    """Check if local.settings.json exists and has proper configuration."""
    try:
        settings_path = os.path.join(os.path.dirname(__file__), "local.settings.json")
        if not os.path.isfile(settings_path):
            print(f"\n⚠️ local.settings.json not found. This might be normal in a production environment.")
            return True
        
        print("\nValidating local.settings.json...")
        
        with open(settings_path, "r") as file:
            settings = json.load(file)
            
        values = settings.get("Values", {})
        if not values:
            print("⚠️ No 'Values' section in local.settings.json")
            
        az_web_jobs_storage = values.get("AzureWebJobsStorage")
        if not az_web_jobs_storage:
            print("⚠️ Missing 'AzureWebJobsStorage' setting")
            
        functions_worker_runtime = values.get("FUNCTIONS_WORKER_RUNTIME")
        if functions_worker_runtime != "python":
            print(f"⚠️ 'FUNCTIONS_WORKER_RUNTIME' is '{functions_worker_runtime}', should be 'python'")
            
        print("✅ local.settings.json appears to be correctly configured")
        return True
    except Exception as e:
        print(f"⚠️ Error validating local.settings.json: {str(e)}")
        return True  # Non-critical error

def run_diagnostics():
    """Run all diagnostic checks."""
    print("=== Azure Function App FastAPI Integration Diagnostics ===\n")
    
    success = True
    success = validate_function_json() and success
    success = validate_init_file() and success
    success = validate_requirements() and success
    success = check_host_json() and success
    success = check_local_settings() and success
    
    print("\n=== Diagnostic Summary ===")
    if success:
        print("✅ All critical configurations appear to be correct.")
        print("\nIf you're still having issues, consider:")
        print("1. Checking Azure Portal for Function App configuration issues")
        print("2. Ensuring your Function App is properly deployed")
        print("3. Checking application logs in the Azure Portal")
        print("4. Verifying any environment variables required by your app")
    else:
        print("❌ Some configuration issues were found. Please address them and try again.")
    
    return success

if __name__ == "__main__":
    run_diagnostics()
