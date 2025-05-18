# Script to run the email service tests

# Ensure we're in the backend directory
Set-Location -Path $PSScriptRoot

# Run the tests
python -m pytest app/tests/test_email_service.py -v
