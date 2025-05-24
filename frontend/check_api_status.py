# check_api_status.py
# Simple script to check if the backend API is responsive

import requests
import sys

# API base URL from your staticwebapp.config.json
API_BASE_URL = "https://vcarpool-dev-api.azurewebsites.net/api"

def check_api():
    """Check if the API is responsive"""
    try:
        # Try to access a public endpoint
        print(f"Testing connection to {API_BASE_URL}...")
        response = requests.get(f"{API_BASE_URL}/v1/health", timeout=10)
        
        if response.ok:
            print(f"✅ API is responsive with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return False

if __name__ == "__main__":
    print("=================================================================")
    print("    Carpool Management Application - API Status Check")
    print("=================================================================")
    print("")
    
    success = check_api()
    
    print("")
    if success:
        print("API check completed successfully.")
    else:
        print("API check failed. Please verify your backend deployment.")
    
    print("=================================================================")
