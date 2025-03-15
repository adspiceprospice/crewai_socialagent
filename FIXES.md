# Social Media Reactions Checkers Fixes

This document outlines the changes made to improve the social media reactions checkers and ensure proper monitoring of comments on posts made on LinkedIn and X.

## Issues Fixed

1. **Fixed Import in Monitor.py**: The monitor module was trying to import `respond_to_comments` from src.main, but that function is properly defined as a method in the `SocialMediaAgent` class. We've updated the code to use the agent's method directly.

2. **Improved Monitor Process Management**: Unlike the scheduler, the monitor process wasn't properly managed with start/stop functionality. We've added proper process management with an `is_running` flag.

3. **Updated UI for Comments**: We've added new UI components to display comments and allow manual checking for new comments.

4. **Fixed Post ID Handling**: There was an inconsistency in how post IDs were handled between LinkedIn and Twitter/X. We've normalized this to ensure both platforms work consistently.

5. **Fixed LinkedIn Posting Issues**: The LinkedIn API was returning 403 ACCESS_DENIED errors when trying to post content. We've implemented multiple fixes:
   - Added a debug LinkedIn post page to test different posting methods
   - Updated the LinkedIn tool to try multiple posting approaches (shares endpoint, UGC posts endpoint)
   - Improved error handling with detailed error messages
   - Added organization posting support with multiple fallback methods
   - Created a permissions checker to verify LinkedIn API token permissions

## Files Modified

1. **monitor.py**
   - Fixed how it calls `respond_to_comments` to use the agent's method
   - Added `is_running` flag for better process management
   - Improved error handling and logging

2. **twitter_tool.py**
   - Added `post_id` to the response structure to match LinkedInTool
   - Ensured consistent response format between platforms

3. **scheduler.py**
   - Updated to handle both `post_id` and `tweet_id` from responses
   - Improved platform post ID tracking

4. **src/tools/scheduler_tool.py**
   - Added `update_post_status` method to allow updating post statuses

5. **src/config/api_helper.py** (new file)
   - Added helper function `normalize_post_response` to standardize responses

6. **src/web_ui/publish_helpers.py** (new file)
   - Added helper function for publishing posts with better error handling

7. **src/web_ui/templates/view_comments.html** (new file)
   - New template for viewing comments on posts

8. **src/web_ui/templates/manual_check_comments.html** (new file)
   - New template for manually checking for comments

9. **src/web_ui/templates/respond_comments.html**
   - Updated with links to new features for comment monitoring

10. **src/web_ui/templates/base.html**
    - Added new navigation items and improved UI with Font Awesome icons

11. **src/tools/linkedin_tool.py**
    - Completely overhauled the LinkedIn posting functionality
    - Added multiple posting methods (shares endpoint, UGC posts endpoint)
    - Improved error handling with detailed error messages
    - Added organization posting support with multiple fallback methods
    - Added debug_post method to test different posting approaches
    - Added check_permissions method to verify LinkedIn API token permissions

12. **src/web_ui/routes.py**
    - Added debug_linkedin_post route to test LinkedIn posting
    - Added check_linkedin_permissions route to verify LinkedIn API permissions
    - Improved error handling in publish_post route with specific LinkedIn error detection
    - Added redirect to debug tool when LinkedIn permission issues are detected

13. **src/web_ui/templates/debug_linkedin_post.html** (new file)
    - New template for debugging LinkedIn posting issues
    - Includes form for testing different posting methods
    - Displays detailed results of posting attempts
    - Shows recommendations based on results

14. **src/web_ui/templates/linkedin_permissions.html** (new file)
    - New template for checking LinkedIn API permissions
    - Displays detailed permission information
    - Shows recommendations for fixing permission issues

## Running the Updated Application

1. Make sure you have all the required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up your environment variables in a `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   GEMINI_API_KEY=your_key_here
   LINKEDIN_ACCESS_TOKEN=your_token_here
   LINKEDIN_ORGANIZATION_ID=your_org_id_here (optional)
   TWITTER_API_KEY=your_key_here
   TWITTER_API_SECRET=your_secret_here
   TWITTER_ACCESS_TOKEN=your_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret_here
   ```

3. Run the application:
   ```bash
   python run.py
   ```

4. Access the web interface at http://localhost:5001

## LinkedIn Posting Troubleshooting

If you encounter issues with LinkedIn posting:

1. Go to http://localhost:5001/check-linkedin-permissions to verify your LinkedIn API permissions
2. Make sure your LinkedIn access token has the necessary permissions:
   - w_member_social (for posting as yourself)
   - r_liteprofile (for accessing your profile)
   - w_organization_social (for posting as an organization)
3. If you're trying to post as an organization, make sure you've added the correct organization ID to your .env file
4. Use the debug tool at http://localhost:5001/debug-linkedin-post to test different posting methods
5. Check the detailed error messages for specific issues with your LinkedIn API setup

## Testing the Social Media Reactions Checker

1. Schedule content for both LinkedIn and X/Twitter using the scheduling page.

2. Wait for the scheduled time or use the "Publish Now" option to publish immediately.

3. Once a post is published, the post ID will be tracked in the system.

4. To check for comments on a post:
   - Go to the "Respond to Comments" page
   - Use the "Manually Check for Comments" button
   - Enter the platform and post ID
   - Check for comments

5. Alternatively, start the monitor process which will automatically check for comments:
   - Click "Start Monitor" in the UI
   - The monitor will periodically check for new comments on published posts
   - When comments are found, it will generate responses

## Troubleshooting

If you encounter any issues:

1. Check the log files (`monitor.log` and `scheduler.log`)
2. Make sure all API keys are correct in your `.env` file
3. Verify that the scheduler and monitor processes are running (you can see this in the UI)
4. If posts are not showing as published, check the response from the LinkedIn or Twitter API
5. For errors in response generation, check the OpenAI API key and connectivity
6. For LinkedIn posting issues, use the debug tool at http://localhost:5001/debug-linkedin-post

The changes made should ensure more robust operation of the system and better handling of post IDs between different platforms.
