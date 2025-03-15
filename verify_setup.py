#!/usr/bin/env python
"""
Verify the setup of CrewAI Social Media Agent.
This script checks all required environment variables and dependencies.
"""

import os
import sys
from dotenv import load_dotenv

def check_env_variables():
    """Check if all required environment variables are set."""
    print("\n🔍 Verifying CrewAI Social Media Agent setup...\n")
    print("Checking environment variables:")
    
    # Load environment variables
    load_dotenv()
    
    # Required environment variables
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API Key',
        'GEMINI_API_KEY': 'Google Gemini API Key',
        'TWITTER_API_KEY': 'Twitter API Key',
        'TWITTER_API_SECRET': 'Twitter API Secret',
        'TWITTER_ACCESS_TOKEN': 'Twitter Access Token',
        'TWITTER_ACCESS_TOKEN_SECRET': 'Twitter Access Token Secret',
        'LINKEDIN_CLIENT_ID': 'LinkedIn Client ID',
        'LINKEDIN_CLIENT_SECRET': 'LinkedIn Client Secret',
        'LINKEDIN_ACCESS_TOKEN': 'LinkedIn Access Token'
    }
    
    all_vars_set = True
    for var, name in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {name} is set")
        else:
            print(f"❌ {name} is not set")
            all_vars_set = False
    
    return all_vars_set

def check_dependencies():
    """Check if all required Python packages are installed."""
    print("\nChecking required packages:")
    
    # List of required packages
    required_packages = [
        'crewai',
        'crewai-tools',
        'google-generativeai',
        'python-dotenv',
        'requests',
        'python-dateutil'
    ]
    
    all_packages_installed = True
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is not installed")
            all_packages_installed = False
    
    return all_packages_installed

def main():
    """Run all verification checks."""
    env_vars_ok = check_env_variables()
    dependencies_ok = check_dependencies()
    
    if env_vars_ok and dependencies_ok:
        print("\n✅ All checks passed!")
        return True
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 