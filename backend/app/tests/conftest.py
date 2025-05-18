"""
Configuration file for pytest
"""
import os
import sys
import pytest

# Add the parent directory to sys.path to allow imports from the app directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import your fixtures here if needed
