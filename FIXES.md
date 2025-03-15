# Social Media Reactions Checkers Fixes

This document outlines the changes made to improve the social media reactions checkers and ensure proper monitoring of comments on posts made on LinkedIn and X.

## Issues Fixed

1. **Fixed Import in Monitor.py**: The monitor module was trying to import `respond_to_comments` from src.main, but that function is properly defined as a method in the `SocialMediaAgent` class. We've updated the code to use the agent's method directly.

2. **Improved Monitor Process Management**: Unlike the scheduler, the monitor process wasn't properly managed with start/stop functionality. We've added proper process management with an `is_running` flag.

3. **Updated UI for Comments**: We've added new UI components to display comments and allow manual checking for new comments.

4. **Fixed Post ID Handling**: There was an inconsistency in how post IDs were handled between LinkedIn and Twitter/X. We've normalized this to ensure both platforms work consistently.

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

## Integration Instructions

1. The files that were directly modified should already be updated in your repository.

2. For the `routes.py` file, since it's quite large, we created a separate file (`routes_update.py`) with the improved publish function. You should replace the existing `publish_post` function in `routes.py` with the one from `routes_update.py`.

3. Add these routes to your `routes.py` file:
   ```python
   @main.route('/manual-check-comments', methods=['GET', 'POST'])
   def manual_check_comments():
       # Implementation in routes.py file
   
   @main.route('/view-comments/<platform>/<post_id>')
   def view_comments(platform, post_id):
       # Implementation in routes.py file
   ```

4. Import the newly created helper modules:
   ```python
   from src.web_ui.publish_helpers import publish_scheduled_post
   from src.config.api_helper import normalize_post_response
   ```

## Testing

After making these changes:

1. Create and schedule content for both LinkedIn and X/Twitter
2. Test publishing posts from the schedule page
3. Test manual comment checking using the new interface
4. Verify that platform post IDs are correctly recorded in the schedule

These changes ensure that the system properly handles social media reactions and maintains consistency between different platforms.
