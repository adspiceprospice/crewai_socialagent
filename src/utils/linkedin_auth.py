import os
import requests
import json
import webbrowser
import http.server
import socketserver
import urllib.parse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LinkedIn OAuth endpoints
AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
REDIRECT_URI = "http://localhost:8000/callback"

# Required scopes for LinkedIn API
SCOPES = [
    "w_member_social"
]

# Global variable to store the authorization code
authorization_code = None

class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback."""
        global authorization_code
        
        # Parse the query parameters
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        
        if "error" in query_components:
            error = query_components["error"][0]
            error_description = query_components.get("error_description", ["Unknown error"])[0]
            response = f"""
            <html>
                <body>
                    <h1>Authentication Error</h1>
                    <p>Error: {error}</p>
                    <p>Description: {error_description}</p>
                    <p>Please close this window and try again.</p>
                </body>
            </html>
            """
            self.send_response(400)
        elif "code" in query_components:
            authorization_code = query_components["code"][0]
            response = """
            <html>
                <body>
                    <h1>Authentication Successful!</h1>
                    <p>You can now close this window and return to the terminal.</p>
                </body>
            </html>
            """
            self.send_response(200)
        else:
            response = """
            <html>
                <body>
                    <h1>Invalid Request</h1>
                    <p>No authorization code or error received.</p>
                </body>
            </html>
            """
            self.send_response(400)
        
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(response.encode())

def get_authorization_url():
    """Construct the authorization URL."""
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    if not client_id:
        raise ValueError("LINKEDIN_CLIENT_ID not found in environment variables")
    
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "state": "random_state_string"  # In production, use a secure random string
    }
    
    query_string = urllib.parse.urlencode(params)
    return f"{AUTHORIZATION_URL}?{query_string}"

def get_access_token(code):
    """Exchange the authorization code for an access token."""
    client_id = os.getenv("LINKEDIN_CLIENT_ID")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("LINKEDIN_CLIENT_ID or LINKEDIN_CLIENT_SECRET not found in environment variables")
    
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret
    }
    
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code != 200:
        raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    return response.json()

def save_token_to_env(token_data):
    """Save the access token to the .env file."""
    access_token = token_data["access_token"]
    
    # Read existing .env file
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
    else:
        lines = []
    
    # Find and replace or append the access token
    token_line = f"LINKEDIN_ACCESS_TOKEN={access_token}\n"
    token_found = False
    
    for i, line in enumerate(lines):
        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
            lines[i] = token_line
            token_found = True
            break
    
    if not token_found:
        lines.append(token_line)
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.writelines(lines)

def main():
    """Run the OAuth flow."""
    print("Starting LinkedIn OAuth flow...")
    
    # Check for required environment variables
    if not os.getenv("LINKEDIN_CLIENT_ID") or not os.getenv("LINKEDIN_CLIENT_SECRET"):
        print("Error: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in your .env file")
        print("\nPlease follow these steps:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Create a new app or select an existing one")
        print("3. Get the Client ID and Client Secret")
        print("4. Add them to your .env file")
        print("5. Add http://localhost:8000/callback to the app's Authorized redirect URLs")
        return
    
    try:
        # Get the authorization URL
        auth_url = get_authorization_url()
        
        print("\nOpening browser to authorize the application...")
        print(f"If the browser doesn't open automatically, visit:\n{auth_url}\n")
        webbrowser.open(auth_url)
        
        # Start the local server to handle the callback
        print("Starting HTTP server to handle the callback...")
        with socketserver.TCPServer(("", 8000), OAuthCallbackHandler) as httpd:
            print("Server started at http://localhost:8000")
            print("Waiting for authorization...")
            
            # Handle one request then exit
            httpd.handle_request()
        
        if not authorization_code:
            print("\nError: No authorization code received")
            return
        
        print("\nAuthorization code received. Getting access token...")
        token_data = get_access_token(authorization_code)
        
        print("Access token received. Saving to .env file...")
        save_token_to_env(token_data)
        
        print("\n✅ LinkedIn OAuth setup completed successfully!")
        print("You can now use the LinkedIn API with your access token.")
        
    except Exception as e:
        print(f"\nError during OAuth flow: {str(e)}")
        print("\nPlease verify your LinkedIn application settings and try again.")

if __name__ == "__main__":
    main() 