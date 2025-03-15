import os
import json
import datetime
import uuid
from typing import Dict, List, Any, Optional

class SchedulerTool:
    def __init__(self, schedule_file: str = "content_schedule.json"):
        """
        Initialize the scheduler tool.
        
        Args:
            schedule_file: Path to the schedule file
        """
        self.schedule_file = schedule_file
        
        # Create the schedule file if it doesn't exist
        if not os.path.exists(schedule_file):
            self._save_schedule({
                "scheduled_posts": [],
                "last_updated": datetime.datetime.now().isoformat()
            })
    
    def update_post_status(self, post_id: str, new_status: str, platform_post_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the status of a scheduled post.
        
        Args:
            post_id: The ID of the post to update
            new_status: The new status for the post
            platform_post_id: Optional platform-specific post ID
            
        Returns:
            Dictionary containing the result of the update operation
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Find the post to update
            post_found = False
            for i, post in enumerate(schedule["scheduled_posts"]):
                if post.get("id") == post_id:
                    post_found = True
                    # Update the post status
                    schedule["scheduled_posts"][i]["status"] = new_status
                    
                    # Update platform_post_id if provided
                    if platform_post_id:
                        schedule["scheduled_posts"][i]["platform_post_id"] = platform_post_id
                        
                    # Add timestamp for the update
                    if new_status == "published":
                        schedule["scheduled_posts"][i]["published_at"] = datetime.datetime.now().isoformat()
                    elif new_status == "failed":
                        schedule["scheduled_posts"][i]["failed_at"] = datetime.datetime.now().isoformat()
                    
                    # Save the updated schedule
                    self._save_schedule(schedule)
                    
                    return {
                        "success": True,
                        "message": f"Successfully updated post status to {new_status}",
                        "updated_post": schedule["scheduled_posts"][i]
                    }
            
            if not post_found:
                return {
                    "success": False,
                    "error": f"Post with ID {post_id} not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating post status: {str(e)}"
            }
            
    def _load_schedule(self) -> Dict[str, Any]:
        """Load the schedule from the file."""
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        return {"scheduled_posts": [], "last_updated": datetime.datetime.now().isoformat()}
    
    def _save_schedule(self, schedule: Dict[str, Any]) -> None:
        """Save the schedule to the file."""
        schedule["last_updated"] = datetime.datetime.now().isoformat()
        with open(self.schedule_file, "w") as f:
            json.dump(schedule, f, indent=2)
    
    def schedule_post(self, content: str, platform: str, schedule_time: datetime.datetime, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Schedule a post for later publication.
        
        Args:
            content: The content of the post
            platform: The platform to post to (e.g., 'linkedin', 'twitter')
            schedule_time: When to publish the post
            image_path: Optional path to an image to include with the post
            
        Returns:
            Dictionary containing the result of the scheduling operation
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Create a new post entry
            post_id = str(uuid.uuid4())
            new_post = {
                "id": post_id,
                "content": content,
                "platform": platform,
                "schedule_time": schedule_time.isoformat(),
                "status": "scheduled",
                "created_at": datetime.datetime.now().isoformat()
            }
            
            if image_path:
                new_post["image_path"] = image_path
            
            # Add the new post to the schedule
            schedule["scheduled_posts"].append(new_post)
            
            # Save the updated schedule
            self._save_schedule(schedule)
            
            return {
                "success": True,
                "message": f"Post scheduled for {schedule_time.isoformat()}",
                "post_id": post_id,
                "scheduled_post": new_post
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error scheduling post: {str(e)}"
            }
    
    def get_scheduled_posts(self) -> Dict[str, Any]:
        """
        Get all scheduled posts.
        
        Returns:
            Dictionary containing all scheduled posts
        """
        try:
            schedule = self._load_schedule()
            return {
                "success": True,
                "scheduled_posts": schedule["scheduled_posts"],
                "count": len(schedule["scheduled_posts"])
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting scheduled posts: {str(e)}"
            }
    
    def get_pending_posts(self) -> Dict[str, Any]:
        """
        Get posts that are scheduled but not yet published.
        
        Returns:
            Dictionary containing pending posts
        """
        try:
            schedule = self._load_schedule()
            pending_posts = [
                post for post in schedule["scheduled_posts"]
                if post.get("status") == "scheduled"
            ]
            
            return {
                "success": True,
                "pending_posts": pending_posts,
                "count": len(pending_posts)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting pending posts: {str(e)}"
            }
    
    def get_due_posts(self) -> Dict[str, Any]:
        """
        Get posts that are due for publication (scheduled time has passed).
        
        Returns:
            Dictionary containing due posts
        """
        try:
            schedule = self._load_schedule()
            now = datetime.datetime.now()
            
            due_posts = [
                post for post in schedule["scheduled_posts"]
                if post.get("status") == "scheduled" and
                datetime.datetime.fromisoformat(post.get("schedule_time")) <= now
            ]
            
            return {
                "success": True,
                "due_posts": due_posts,
                "count": len(due_posts)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting due posts: {str(e)}"
            }
    
    def cancel_scheduled_post(self, post_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: The ID of the post to cancel
            
        Returns:
            Dictionary containing the result of the cancellation
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Find the post to cancel
            post_found = False
            for i, post in enumerate(schedule["scheduled_posts"]):
                if post.get("id") == post_id:
                    post_found = True
                    
                    # Remove the post from the schedule
                    cancelled_post = schedule["scheduled_posts"].pop(i)
                    
                    # Save the updated schedule
                    self._save_schedule(schedule)
                    
                    return {
                        "success": True,
                        "message": f"Post {post_id} cancelled successfully",
                        "cancelled_post": cancelled_post
                    }
            
            if not post_found:
                return {
                    "success": False,
                    "error": f"Post with ID {post_id} not found"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error cancelling post: {str(e)}"
            }
