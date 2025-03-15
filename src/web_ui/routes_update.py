"""
Updated route handlers for the web UI.
This file contains improved versions of the routes that should be integrated 
into the main routes.py file. We're creating this separate file because GitHub 
has size limitations when updating large files directly.
"""

from flask import flash, redirect, url_for
import logging
from src.web_ui.publish_helpers import publish_scheduled_post

# Configure logging
logger = logging.getLogger("web_ui_routes")

def publish_post_updated(post_id):
    """
    Updated endpoint to publish a scheduled post immediately.
    This should replace the existing publish_post function in routes.py.
    
    Args:
        post_id: ID of the post to publish
    """
    try:
        # Call the helper function to publish the post
        result = publish_scheduled_post(post_id, agent, scheduler_tool)
        
        if result.get('success', False):
            if result.get('warning'):
                flash(f"Post published with warning: {result['warning']}", 'warning')
            else:
                flash('Post published successfully!', 'success')
        else:
            flash(f"Error publishing post: {result.get('error', 'Unknown error')}", 'danger')
    except Exception as e:
        logger.error(f"Error publishing post immediately: {str(e)}")
        flash(f'Error publishing post: {str(e)}', 'danger')
    
    return redirect(url_for('main.schedule_content_route'))
