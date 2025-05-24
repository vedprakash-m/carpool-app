# Set environment variables for testing
$env:COSMOS_ENDPOINT = "https://mock-cosmos.azure.com:443/"
$env:COSMOS_KEY = "mock-key=="
$env:COSMOS_DATABASE = "carpool_db_test"
$env:JWT_SECRET_KEY = "mock-jwt-key"

# Run unit tests
Write-Host "Running unit tests..." -ForegroundColor Green
python -m pytest app/tests/test_schedule_generator_unit.py -v

# Run comprehensive tests
Write-Host "Running comprehensive tests..." -ForegroundColor Green
python -m pytest app/tests/test_schedule_generator_comprehensive.py -v

# Run visual verification (if required packages are installed)
Write-Host "Running visual verification..." -ForegroundColor Green
try {
    python app/tests/verify_schedule_generator_visual.py
}
catch {
    Write-Host "Error running visual verification. Make sure tabulate and colorama are installed:" -ForegroundColor Red
    Write-Host "pip install tabulate colorama" -ForegroundColor Yellow
}

Write-Host "All schedule tests completed!" -ForegroundColor Cyan
