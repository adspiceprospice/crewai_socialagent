#!/usr/bin/env python
"""
LinkedIn OAuth Script

This script runs the LinkedIn OAuth flow to obtain an access token.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the LinkedIn OAuth module
from src.utils.linkedin_auth import main

if __name__ == "__main__":
    main() 