#!/usr/bin/env python
"""
Web UI for the CrewAI Social Media Agent.
This script runs a Flask web server that provides a user interface for the social media agent.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_ui import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000) 