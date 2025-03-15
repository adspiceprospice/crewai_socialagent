#!/usr/bin/env python
"""
Verify the setup of CrewAI Social Media Agent.
This script checks all required environment variables and dependencies.
"""

import os
import sys
import pkg_resources
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
    
    # Required packages to check
    required_packages = [
        'crewai',
        'google-generativeai',
        'python-dotenv',
        'requests',
        'python-dateutil'
    ]
    
    all_packages_installed = True
    for package in required_packages:
        try:
            pkg_resources.require(package)
            print(f"✅ {package} is installed")
        except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
            print(f"❌ {package} is not installed")
            all_packages_installed = False
    
    if not all_packages_installed:
        print("\n📦 To install missing packages, run:")
        print("pip install -r requirements.txt")
    
    return all_packages_installed

def main():
    """Run all verification checks."""
    try:
        env_vars_ok = check_env_variables()
        print("\n" + "="*50)  # Separator for better readability
        dependencies_ok = check_dependencies()
        
        print("\n" + "="*50)  # Separator for better readability
        if env_vars_ok and dependencies_ok:
            print("\n✅ All checks passed!")
            return True
        else:
            print("\n❌ Some checks failed. Please fix the issues above.")
            if not dependencies_ok:
                print("\nTo install missing packages:")
                print("1. Activate your virtual environment (if using one)")
                print("2. Run: pip install -r requirements.txt")
                print("3. Run this verification script again")
            return False
    except Exception as e:
        print(f"\n❌ Error during verification: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    print("")  # Add a blank line for better readability
    sys.exit(0 if success else 1) 