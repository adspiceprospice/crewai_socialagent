import json
import os
import datetime
from typing import Dict, Any, List, Optional
from crewai.tools import BaseTool

class SchedulerTool(BaseTool):
    """Tool for scheduling social media posts."""
    
    name: str = "Content Scheduler"
    description: str = "Schedule social media posts for future publication."
    
    def __init__(self, schedule_file: str = "content_schedule.json"):
        super().__init__()
        self.schedule_file = schedule_file
        self._ensure_schedule_file_exists()
        
    def _ensure_schedule_file_exists(self):
        """Ensure the schedule file exists."""
        if not os.path.exists(self.schedule_file):
            with open(self.schedule_file, "w") as f:
                json.dump({"scheduled_posts": []}, f)
                
    def _load_schedule(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load the schedule from the file."""
        with open(self.schedule_file, "r") as f:
            return json.load(f)
            
    def _save_schedule(self, schedule: Dict[str, List[Dict[str, Any]]]):
        """Save the schedule to the file."""
        with open(self.schedule_file, "w") as f:
            json.dump(schedule, f, indent=2)
    
    def _execute(
        self, 
        content: str, 
        platform: str,
        schedule_time: str,
        image_path: Optional[str] = None,
        post_type: str = "regular"
    ) -> Dict[str, Any]:
        """
        Schedule a social media post.
        
        Args:
            content: The content of the post
            platform: The platform to post to (e.g., "linkedin", "twitter")
            schedule_time: ISO-8601 timestamp for when to post
            image_path: Optional path to an image to include in the post
            post_type: Type of post (e.g., "regular", "promotion", "engagement")
            
        Returns:
            Dictionary containing the result of the scheduling operation
        """
        try:
            # Validate the schedule time
            try:
                schedule_datetime = datetime.datetime.fromisoformat(schedule_time.replace("Z", "+00:00"))
            except ValueError:
                return {
                    "success": False,
                    "error": f"Invalid schedule time format: {schedule_time}. Use ISO-8601 format (e.g., '2023-12-31T12:00:00Z')."
                }
                
            # Validate the platform
            if platform.lower() not in ["linkedin", "twitter", "x"]:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}. Supported platforms are 'linkedin', 'twitter', and 'x'."
                }
                
            # Normalize platform name
            if platform.lower() == "x":
                platform = "twitter"
                
            # Create the scheduled post entry
            post_id = f"{platform}_{int(datetime.datetime.now().timestamp())}"
            scheduled_post = {
                "id": post_id,
                "content": content,
                "platform": platform.lower(),
                "schedule_time": schedule_time,
                "image_path": image_path,
                "post_type": post_type,
                "status": "scheduled",
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Add the new post to the schedule
            schedule["scheduled_posts"].append(scheduled_post)
            
            # Save the updated schedule
            self._save_schedule(schedule)
            
            return {
                "success": True,
                "post_id": post_id,
                "message": f"Successfully scheduled post for {schedule_time} on {platform}."
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error scheduling post: {str(e)}"
            }
            
    def get_scheduled_posts(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """
        Get scheduled posts, optionally filtered by platform.
        
        Args:
            platform: Optional platform to filter by
            
        Returns:
            Dictionary containing the scheduled posts
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Filter by platform if specified
            if platform:
                # Normalize platform name
                if platform.lower() == "x":
                    platform = "twitter"
                    
                filtered_posts = [
                    post for post in schedule["scheduled_posts"]
                    if post["platform"].lower() == platform.lower()
                ]
                
                return {
                    "success": True,
                    "scheduled_posts": filtered_posts
                }
            
            return {
                "success": True,
                "scheduled_posts": schedule["scheduled_posts"]
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting scheduled posts: {str(e)}"
            }
            
    def cancel_scheduled_post(self, post_id: str) -> Dict[str, Any]:
        """
        Cancel a scheduled post.
        
        Args:
            post_id: The ID of the post to cancel
            
        Returns:
            Dictionary containing the result of the cancellation operation
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Find the post to cancel
            for i, post in enumerate(schedule["scheduled_posts"]):
                if post["id"] == post_id:
                    # Remove the post from the schedule
                    cancelled_post = schedule["scheduled_posts"].pop(i)
                    
                    # Save the updated schedule
                    self._save_schedule(schedule)
                    
                    return {
                        "success": True,
                        "message": f"Successfully cancelled scheduled post {post_id}.",
                        "cancelled_post": cancelled_post
                    }
            
            return {
                "success": False,
                "error": f"Scheduled post with ID {post_id} not found."
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error cancelling scheduled post: {str(e)}"
            }
            
    def update_scheduled_post(
        self, 
        post_id: str,
        content: Optional[str] = None,
        schedule_time: Optional[str] = None,
        image_path: Optional[str] = None,
        post_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a scheduled post.
        
        Args:
            post_id: The ID of the post to update
            content: Optional new content for the post
            schedule_time: Optional new schedule time for the post
            image_path: Optional new image path for the post
            post_type: Optional new post type for the post
            
        Returns:
            Dictionary containing the result of the update operation
        """
        try:
            # Load the current schedule
            schedule = self._load_schedule()
            
            # Find the post to update
            for i, post in enumerate(schedule["scheduled_posts"]):
                if post["id"] == post_id:
                    # Update the post
                    if content is not None:
                        schedule["scheduled_posts"][i]["content"] = content
                        
                    if schedule_time is not None:
                        # Validate the schedule time
                        try:
                            schedule_datetime = datetime.datetime.fromisoformat(schedule_time.replace("Z", "+00:00"))
                            schedule["scheduled_posts"][i]["schedule_time"] = schedule_time
                        except ValueError:
                            return {
                                "success": False,
                                "error": f"Invalid schedule time format: {schedule_time}. Use ISO-8601 format (e.g., '2023-12-31T12:00:00Z')."
                            }
                            
                    if image_path is not None:
                        schedule["scheduled_posts"][i]["image_path"] = image_path
                        
                    if post_type is not None:
                        schedule["scheduled_posts"][i]["post_type"] = post_type
                        
                    # Save the updated schedule
                    self._save_schedule(schedule)
                    
                    return {
                        "success": True,
                        "message": f"Successfully updated scheduled post {post_id}.",
                        "updated_post": schedule["scheduled_posts"][i]
                    }
            
            return {
                "success": False,
                "error": f"Scheduled post with ID {post_id} not found."
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error updating scheduled post: {str(e)}"
            } 