import os
import requests
from dotenv import load_dotenv
import base64
import urllib.parse
import hmac
import hashlib
import time
import json

# Load environment variables
load_dotenv()

def generate_oauth1_signature(method, url, params, consumer_secret, oauth_token_secret):
    """Generate OAuth1.0a signature"""
    # Create parameter string
    param_string = '&'.join(sorted([f"{k}={urllib.parse.quote(str(v), safe='')}" 
                                  for k, v in params.items()]))
    
    # Create signature base string
    signature_base = '&'.join([
        method,
        urllib.parse.quote(url, safe=''),
        urllib.parse.quote(param_string, safe='')
    ])
    
    # Create signing key
    signing_key = '&'.join([
        urllib.parse.quote(consumer_secret, safe=''),
        urllib.parse.quote(oauth_token_secret, safe='')
    ])
    
    # Generate signature
    signature = base64.b64encode(
        hmac.new(
            signing_key.encode('utf-8'),
            signature_base.encode('utf-8'),
            hashlib.sha1
        ).digest()
    ).decode('utf-8')
    
    return signature

def verify_credentials():
    """Verify Twitter API credentials"""
    api_key = os.getenv('TWITTER_API_KEY')
    api_secret = os.getenv('TWITTER_API_SECRET')
    access_token = os.getenv('TWITTER_ACCESS_TOKEN')
    access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    
    if not all([api_key, api_secret, access_token, access_token_secret]):
        raise ValueError(
            "Missing Twitter credentials. Please ensure all required environment "
            "variables are set in your .env file:\n"
            "- TWITTER_API_KEY\n"
            "- TWITTER_API_SECRET\n"
            "- TWITTER_ACCESS_TOKEN\n"
            "- TWITTER_ACCESS_TOKEN_SECRET"
        )
    
    # Verification endpoint
    url = 'https://api.twitter.com/2/users/me'
    
    # Generate OAuth 1.0a parameters
    oauth_timestamp = str(int(time.time()))
    oauth_nonce = base64.b64encode(os.urandom(32)).decode('utf-8')
    
    oauth_params = {
        'oauth_consumer_key': api_key,
        'oauth_nonce': oauth_nonce,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_timestamp': oauth_timestamp,
        'oauth_token': access_token,
        'oauth_version': '1.0'
    }
    
    # Generate signature
    signature = generate_oauth1_signature(
        'GET', url, oauth_params, api_secret, access_token_secret
    )
    oauth_params['oauth_signature'] = signature
    
    # Create Authorization header
    auth_header = 'OAuth ' + ', '.join([
        f'{k}="{urllib.parse.quote(v, safe="")}"'
        for k, v in oauth_params.items()
    ])
    
    # Make request
    headers = {'Authorization': auth_header}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        error_msg = f"{response.status_code}"
        try:
            error_details = response.json()
            error_msg += f" - {json.dumps(error_details)}"
        except:
            error_msg += f" - {response.text}"
        
        print("\n❌ Failed to verify Twitter credentials:", error_msg)
        print("\nPossible issues:")
        print("1. Invalid API keys or access tokens")
        print("2. Expired tokens")
        print("3. Rate limiting")
        print("4. Incorrect OAuth signature generation")
        print("\nPlease verify your credentials:")
        print("1. Go to https://developer.twitter.com/en/portal/projects-and-apps")
        print("2. Select your project and app")
        print("3. Check your API keys and access tokens")
        print("4. Make sure your app has appropriate permissions (Read and Write)")
        print("5. Update your .env file with the correct credentials")
        print("\nRequired .env variables:")
        print("TWITTER_API_KEY=your_api_key")
        print("TWITTER_API_SECRET=your_api_secret")
        print("TWITTER_ACCESS_TOKEN=your_access_token")
        print("TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret")
        return False
    
    print("\n✅ Twitter credentials verified successfully!")
    print(f"Authenticated as: {response.json()['data']['username']}")
    return True

def main():
    """Main function to verify Twitter credentials"""
    print("🔍 Verifying Twitter API credentials...")
    try:
        verify_credentials()
    except ValueError as e:
        print(f"\n❌ Error: {str(e)}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print("\nPlease try again or contact support if the issue persists.")

if __name__ == "__main__":
    main() 