# create_admin_user.ps1
# Script to create an admin user for the Carpool Management Application

param(
    [string]$Email = "admin@example.com",
    [string]$FullName = "Admin User",
    [string]$Password = "Admin@0987654",
    [string]$CosmosEndpoint = $env:COSMOS_ENDPOINT,
    [string]$CosmosKey = $env:COSMOS_KEY,
    [string]$CosmosDatabase = $env:COSMOS_DATABASE
)

# Display script header
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "    Carpool Management Application - Admin User Creation Tool" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to write colored status messages
function Write-StatusMessage {
    param (
        [string]$Message,
        [string]$Type = "Info" # Info, Success, Warning, Error
    )
    
    $color = switch ($Type) {
        "Info" { "Cyan" }
        "Success" { "Green" }
        "Warning" { "Yellow" }
        "Error" { "Red" }
        default { "White" }
    }
    
    Write-Host "[$Type] $Message" -ForegroundColor $color
}

# Check if we have the required environment variables or parameters
if (-not $CosmosEndpoint -or -not $CosmosKey -or -not $CosmosDatabase) {
    # Try to load from .env file if it exists
    if (Test-Path -Path "..\backend\.env") {
        Write-StatusMessage "Loading environment variables from .env file..." -Type "Info"
        Get-Content -Path "..\backend\.env" | ForEach-Object {
            if ($_ -match '^COSMOS_ENDPOINT=(.*)$') { $CosmosEndpoint = $matches[1] }
            if ($_ -match '^COSMOS_KEY=(.*)$') { $CosmosKey = $matches[1] }
            if ($_ -match '^COSMOS_DATABASE=(.*)$') { $CosmosDatabase = $matches[1] }
        }
    }
    else {
        Write-StatusMessage "No .env file found. Please provide Cosmos DB connection details." -Type "Warning"
    }
}

if (-not $CosmosEndpoint -or -not $CosmosKey -or -not $CosmosDatabase) {
    Write-StatusMessage "Missing required Cosmos DB connection details. Please provide them as parameters or set environment variables." -Type "Error"
    Write-StatusMessage "Example: .\create_admin_user.ps1 -CosmosEndpoint 'https://your-cosmos.documents.azure.com:443/' -CosmosKey 'your-key' -CosmosDatabase 'your-db'" -Type "Info"
    exit 1
}

# Validate password complexity
$passwordValid = $true
$passwordErrors = @()

if ($Password.Length -lt 8) {
    $passwordValid = $false
    $passwordErrors += "Password must be at least 8 characters long"
}
if (-not ($Password -cmatch '[A-Z]')) {
    $passwordValid = $false
    $passwordErrors += "Password must contain at least one uppercase letter"
}
if (-not ($Password -cmatch '[a-z]')) {
    $passwordValid = $false
    $passwordErrors += "Password must contain at least one lowercase letter"
}
if (-not ($Password -cmatch '[0-9]')) {
    $passwordValid = $false
    $passwordErrors += "Password must contain at least one number"
}
if (-not ($Password -cmatch '[^A-Za-z0-9]')) {
    $passwordValid = $false
    $passwordErrors += "Password must contain at least one special character"
}

if (-not $passwordValid) {
    Write-StatusMessage "Password does not meet complexity requirements:" -Type "Error"
    foreach ($error in $passwordErrors) {
        Write-StatusMessage "- $error" -Type "Error"
    }
    exit 1
}

# Check if the Azure CLI and CosmosDB tools are available
try {
    $azVersion = az --version
    if ($LASTEXITCODE -ne 0) {
        throw "Azure CLI not found"
    }
    Write-StatusMessage "Azure CLI is available" -Type "Success"
}
catch {
    Write-StatusMessage "Azure CLI is required but not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -Type "Error"
    exit 1
}

# Check if logged in to Azure
$loginStatus = az account show 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-StatusMessage "Not logged in to Azure. Please login." -Type "Warning"
    az login
    if ($LASTEXITCODE -ne 0) {
        Write-StatusMessage "Failed to login to Azure. Exiting." -Type "Error"
        exit 1
    }
}

# Confirm with the user before proceeding
Write-StatusMessage "About to create an admin user with the following details:" -Type "Info"
Write-Host "  Email: $Email" -ForegroundColor White
Write-Host "  Full Name: $FullName" -ForegroundColor White
Write-Host "  Cosmos DB: $CosmosDatabase" -ForegroundColor White
Write-Host ""
$confirmation = Read-Host "Do you want to proceed? (y/n)"
if ($confirmation -ne "y") {
    Write-StatusMessage "Operation cancelled by user." -Type "Warning"
    exit 0
}

# Generate a unique ID for the user
$userId = [guid]::NewGuid().ToString()
$timestamp = (Get-Date).ToUniversalTime().ToString("o")

# Hash the password using bcrypt
Write-StatusMessage "Generating password hash..." -Type "Info"

$bcryptScript = @"
import bcrypt
import sys

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

if __name__ == '__main__':
    password = sys.argv[1]
    print(hash_password(password))
"@

# Save the script to a temporary file
$tempScriptPath = [System.IO.Path]::GetTempFileName() + ".py"
$bcryptScript | Out-File -FilePath $tempScriptPath -Encoding utf8

# Execute the Python script to hash the password
try {
    $hashedPassword = python $tempScriptPath $Password
    Write-StatusMessage "Password hash generated successfully" -Type "Success"
}
catch {
    Write-StatusMessage "Failed to generate password hash. Make sure Python and the bcrypt package are installed." -Type "Error"
    Write-StatusMessage "You can install bcrypt with: pip install bcrypt" -Type "Info"
    Remove-Item -Path $tempScriptPath -Force
    exit 1
}

# Clean up the temporary script
Remove-Item -Path $tempScriptPath -Force

# Create the user document in JSON format
$userDoc = @{
    id = $userId
    email = $Email
    full_name = $FullName
    role = "ADMIN"
    hashed_password = $hashedPassword
    created_at = $timestamp
    updated_at = $timestamp
    is_active_driver = $false
} | ConvertTo-Json -Depth 10

# Save the document to a temporary file
$tempDocPath = [System.IO.Path]::GetTempFileName() + ".json"
$userDoc | Out-File -FilePath $tempDocPath -Encoding utf8

# Create the user in Cosmos DB
Write-StatusMessage "Creating admin user in Cosmos DB..." -Type "Info"
try {
    $result = az cosmosdb sql container document create `
        --resource-group $(az cosmosdb show --name $CosmosDatabase --query resourceGroup -o tsv) `
        --account-name $(az cosmosdb list --query "[0].name" -o tsv) `
        --database-name $CosmosDatabase `
        --container-name "users" `
        --id $userId `
        --partition-key $userId `
        --body "$tempDocPath"
    
    Write-StatusMessage "Admin user created successfully!" -Type "Success"
    Write-StatusMessage "You can now log in with:" -Type "Success"
    Write-Host "  Email: $Email" -ForegroundColor Green
    Write-Host "  Password: $Password" -ForegroundColor Green
}
catch {
    Write-StatusMessage "Failed to create admin user in Cosmos DB. Error: $_" -Type "Error"
}

# Clean up the temporary document file
Remove-Item -Path $tempDocPath -Force

Write-Host ""
Write-StatusMessage "Admin user creation process completed." -Type "Success"
