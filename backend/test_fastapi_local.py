"""
Local FastAPI Test Script
------------------------
This script tests the FastAPI application locally without Azure Functions.
It helps isolate whether the issue is with the FastAPI app itself or the Azure Functions integration.
"""

import importlib.util
import os
import sys
import uvicorn
import importlib
from pathlib import Path

def get_app_module_path():
    """Get the path to the FastAPI app module."""
    # Check for __init__.py in the api directory
    api_init_path = os.path.join(os.path.dirname(__file__), "api", "__init__.py")
    if os.path.isfile(api_init_path):
        return "api", api_init_path
    
    # Otherwise, search for other potential FastAPI app modules
    for root, dirs, files in os.walk(os.path.dirname(__file__)):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Look for FastAPI app initialization
                    if "FastAPI(" in content and "app =" in content:
                        rel_path = os.path.relpath(file_path, os.path.dirname(__file__))
                        module_name = os.path.splitext(rel_path.replace(os.sep, "."))[0]
                        return module_name, file_path
    
    return None, None

def load_app():
    """Try to load the FastAPI app."""
    module_name, module_path = get_app_module_path()
    
    if not module_path:
        print("❌ Could not find FastAPI app module.")
        return None
        
    print(f"📁 Found potential FastAPI app in: {module_path}")
    
    try:
        # Try standard import first
        if "." not in module_name:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, "app"):
                    print("✅ Successfully imported FastAPI app via standard import")
                    return module.app
            except ImportError:
                pass
        
        # Fall back to file-based import
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if not spec or not spec.loader:
            print("❌ Cannot load app module")
            return None
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        if not hasattr(module, "app"):
            print("❌ No 'app' instance found in the module")
            return None
            
        print("✅ Successfully loaded FastAPI app")
        return module.app
    except Exception as e:
        print(f"❌ Error loading FastAPI app: {str(e)}")
        return None

def discover_api_routes(app):
    """Discover and print all API routes."""
    if not app:
        return
        
    print("\n=== API Routes ===")
    routes = []
    
    for route in app.routes:
        methods = getattr(route, "methods", ["GET"])
        path = getattr(route, "path", "")
        name = getattr(route, "name", "")
        
        if path:
            for method in methods:
                routes.append({
                    "method": method,
                    "path": path,
                    "name": name
                })
    
    # Sort routes by path
    routes.sort(key=lambda x: x["path"])
    
    # Print routes
    for route in routes:
        print(f"{route['method']:<7} {route['path']:<40} {route['name']}")
        
    print(f"\nTotal routes: {len(routes)}")

def run_local_server(app, port=8000):
    """Run the FastAPI app locally."""
    if not app:
        return
        
    print(f"\n🚀 Starting local FastAPI server on port {port}...")
    print(f"   Access your API at http://localhost:{port}")
    print("   Press CTRL+C to stop the server")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"❌ Error starting server: {str(e)}")

def main():
    """Main function."""
    print("=== FastAPI Local Test ===\n")
    
    # Add the current directory to sys.path if it's not already there
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Load the FastAPI app
    app = load_app()
    if not app:
        print("\n❌ Could not load the FastAPI app. Please check your app configuration.")
        return
    
    # Discover API routes
    discover_api_routes(app)
    
    # Ask if the user wants to run the server
    choice = input("\nDo you want to start a local server to test the API? (y/n): ")
    if choice.lower() == 'y':
        port = input("Enter port number (default: 8000): ")
        try:
            port = int(port) if port else 8000
        except ValueError:
            print("Invalid port number, using default 8000")
            port = 8000
        
        run_local_server(app, port)
    else:
        print("\n✅ API route discovery completed. Exiting without starting server.")

if __name__ == "__main__":
    main()
