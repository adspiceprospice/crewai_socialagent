"""
Helper functions for publishing content from the web UI.
"""

import logging
from typing import Dict, Any, Optional
from src.agents.social_media_agent import SocialMediaAgent
from src.tools.scheduler_tool import SchedulerTool
from src.config.api_helper import normalize_post_response

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("publish_helpers")

def publish_scheduled_post(post_id: str, agent: SocialMediaAgent, scheduler_tool: SchedulerTool) -> Dict[str, Any]:
    """
    Publish a scheduled post immediately and update its status.
    
    Args:
        post_id: ID of the post to publish
        agent: Social media agent instance
        scheduler_tool: Scheduler tool instance
        
    Returns:
        Dict with the result of the operation
    """
    try:
        # Get all scheduled posts
        all_posts = scheduler_tool.get_scheduled_posts()
        
        if not all_posts.get('success', False):
            return {"success": False, "error": "Failed to get scheduled posts"}
            
        # Find the post with the given ID
        post_to_publish = None
        for post in all_posts.get('scheduled_posts', []):
            if post.get('id') == post_id:
                post_to_publish = post
                break
        
        if not post_to_publish:
            return {"success": False, "error": f"Post with ID {post_id} not found"}
            
        # Log post details for debugging
        logger.info(f"Attempting to publish post: {post_id}, Platform: {post_to_publish.get('platform')}")
        
        # Publish the post immediately
        result = agent.post_content(
            content=post_to_publish.get('content'),
            platform=post_to_publish.get('platform'),
            image_path=post_to_publish.get('image_path')
        )
        
        # Normalize the response
        result = normalize_post_response(result)
        
        # Log the result for debugging
        logger.info(f"Publish result: {result}")
        
        if result.get('success', False):
            # Update the post status in the scheduler
            platform_post_id = result.get('post_id')
            if platform_post_id:
                update_result = scheduler_tool.update_post_status(
                    post_id=post_id,
                    new_status="published",
                    platform_post_id=platform_post_id
                )
                
                if update_result.get('success', False):
                    return {
                        "success": True,
                        "message": "Post published and status updated successfully",
                        "post_id": post_id,
                        "platform_post_id": platform_post_id
                    }
                else:
                    return {
                        "success": True,
                        "warning": "Post published but status could not be updated",
                        "post_id": post_id,
                        "platform_post_id": platform_post_id,
                        "update_error": update_result.get('error')
                    }
            else:
                return {
                    "success": True,
                    "warning": "Post published but no platform post ID was returned",
                    "post_id": post_id
                }
        else:
            # Update the post status to failed
            scheduler_tool.update_post_status(
                post_id=post_id,
                new_status="failed"
            )
            
            return {
                "success": False,
                "error": result.get('error', "Unknown error during publishing"),
                "post_id": post_id
            }
            
    except Exception as e:
        logger.error(f"Error publishing scheduled post: {str(e)}")
        return {
            "success": False,
            "error": f"Error publishing post: {str(e)}",
            "post_id": post_id
        }
