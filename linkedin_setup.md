# LinkedIn API Setup Guide

This guide will help you properly configure LinkedIn API integration for CrewAI Social Media Agent.

## Prerequisites

- LinkedIn Developer Account
- LinkedIn Application with API access
- Proper API permissions

## Step 1: Create a LinkedIn Developer Application

1. Visit [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Sign in with your LinkedIn account
3. Click "Create app" button
4. Fill in the required information:
   - App name: `CrewAI Social Agent`
   - LinkedIn Page: Select your company page (or your personal profile)
   - App logo: Upload a logo (optional)
   - Legal Agreement: Accept the terms
5. Click "Create app"

## Step 2: Configure API Permissions

1. In your app dashboard, go to the "Auth" tab
2. Under "OAuth 2.0 scopes", add the following permissions:
   - `r_liteprofile` - To access your profile information
   - `w_member_social` - To post content as yourself
   - `w_organization_social` - To post content as your organization (if needed)
   - `r_organization_social` - To read organization content (if needed)

## Step 3: Configure Redirect URLs

1. Still in the "Auth" tab, under "OAuth 2.0 settings"
2. Add `http://localhost:8000/callback` to "Authorized redirect URLs"
3. Save changes

## Step 4: Generate API Credentials

1. Go to the app's "Settings" tab
2. Note your Client ID and Client Secret
3. Add these values to your `.env` file:
   ```
   LINKEDIN_CLIENT_ID=your_client_id
   LINKEDIN_CLIENT_SECRET=your_client_secret
   ```

## Step 5: Obtain an Access Token

1. Run the authentication script:
   ```
   python linkedin_auth.py
   ```
2. This will open a browser window to authorize your application
3. Log in with your LinkedIn account and grant the requested permissions
4. The script will automatically save the access token to your `.env` file

## Step 6: Configure Organization ID (Optional)

If you want to post as an organization:

1. Get your LinkedIn Organization ID (Company Page ID)
2. Add it to your `.env` file:
   ```
   LINKEDIN_ORGANIZATION_ID=your_organization_id
   ```

## Troubleshooting

If you encounter issues:

1. Check permissions in the LinkedIn Developer Portal
2. Ensure your access token is valid and has the required permissions
3. Use the Debug LinkedIn Post tool in the web UI to diagnose issues
4. Check the LinkedIn Permissions page in the web UI for permission status

## Additional Resources

- [LinkedIn Marketing API Documentation](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api)
- [LinkedIn Authentication Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow) 