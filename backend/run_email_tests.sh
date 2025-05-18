#!/bin/bash
# Script to run the email service tests

# Ensure we're in the backend directory
cd "$(dirname "$0")"

# Run the tests
python -m pytest app/tests/test_email_service.py -v
