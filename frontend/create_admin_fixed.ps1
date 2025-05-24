# create_admin_fixed.ps1
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

# Prompt user for missing values if needed
if (-not $CosmosEndpoint) {
    $CosmosEndpoint = Read-Host "Enter Cosmos DB Endpoint URL"
}
if (-not $CosmosKey) {
    $CosmosKey = Read-Host "Enter Cosmos DB Key"
}
if (-not $CosmosDatabase) {
    $CosmosDatabase = Read-Host "Enter Cosmos DB Database Name"
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
try {
    $hashedPassword = python -c "import bcrypt; password='$Password'; hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()); print(hashed.decode('utf-8'))"
    if (-not $hashedPassword) {
        throw "Failed to generate password hash"
    }
    Write-StatusMessage "Password hash generated successfully" -Type "Success"
}
catch {
    Write-StatusMessage "Failed to generate password hash. Make sure Python and the bcrypt package are installed." -Type "Error"
    Write-StatusMessage "You can install bcrypt with: pip install bcrypt" -Type "Info"
    exit 1
}

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

Write-StatusMessage "User document created with the following details:" -Type "Info"
Write-Host "  ID: $userId" -ForegroundColor White
Write-Host "  Email: $Email" -ForegroundColor White
Write-Host "  Role: ADMIN" -ForegroundColor White
Write-Host "  Created At: $timestamp" -ForegroundColor White

# Save the document to a temporary file
$tempDocPath = [System.IO.Path]::GetTempFileName() + ".json"
$userDoc | Out-File -FilePath $tempDocPath -Encoding utf8

Write-Host ""
Write-StatusMessage "You can now log in to the application with:" -Type "Success"
Write-Host "  Email: $Email" -ForegroundColor Green
Write-Host "  Password: $Password" -ForegroundColor Green

Write-Host ""
Write-StatusMessage "Admin user creation completed. You now have the admin credentials." -Type "Success"
