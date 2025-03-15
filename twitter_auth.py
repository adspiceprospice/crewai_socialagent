#!/usr/bin/env python
"""
Twitter OAuth verification script.
This script verifies your Twitter API credentials and confirms your authentication.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.twitter_auth import main

if __name__ == "__main__":
    main() 