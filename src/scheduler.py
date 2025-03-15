#!/usr/bin/env python
"""
Scheduler for the CrewAI Social Media Agent.
This script handles scheduling and posting of content at specified times.
"""

import os
import sys
import time
import json
import logging
import datetime
from typing import Dict, Any, List
from src.tools.linkedin_tool import LinkedInTool
from src.tools.twitter_tool import TwitterTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("scheduler")

class PostScheduler:
    """
    A scheduler for running scheduled social media posts.
    """
    
    def __init__(self, schedule_file: str = "content_schedule.json", check_interval: int = 60):
        """
        Initialize the post scheduler.
        
        Args:
            schedule_file: Path to the schedule file
            check_interval: Interval in seconds to check for scheduled posts
        """
        self.schedule_file = schedule_file
        self.check_interval = check_interval
        
        try:
            self.linkedin_tool = LinkedInTool()
            self.twitter_tool = TwitterTool()
            logger.info("Successfully initialized social media tools")
        except Exception as e:
            logger.error(f"Error initializing social media tools: {str(e)}")
            # Still create the scheduler but disable posting functionality
            self.linkedin_tool = None
            self.twitter_tool = None
        
    def _load_schedule(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load the schedule from the file."""
        try:
            if not os.path.exists(self.schedule_file):
                return {"scheduled_posts": []}
                
            with open(self.schedule_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading schedule: {str(e)}")
            return {"scheduled_posts": []}
            
    def _save_schedule(self, schedule: Dict[str, List[Dict[str, Any]]]):
        """Save the schedule to the file."""
        try:
            with open(self.schedule_file, "w") as f:
                json.dump(schedule, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving schedule: {str(e)}")
            
    def _post_to_platform(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post content to the specified platform.
        
        Args:
            post: The post to publish
            
        Returns:
            Dictionary containing the result of the posting operation
        """
        if self.linkedin_tool is None or self.twitter_tool is None:
            return {
                "success": False,
                "error": "Social media tools are not initialized"
            }
            
        platform = post.get("platform", "").lower()
        content = post.get("content", "")
        image_path = post.get("image_path")
        
        try:
            if platform == "linkedin":
                return self.linkedin_tool._execute(content, image_path)
            elif platform == "twitter":
                return self.twitter_tool._execute(content, image_path)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported platform: {platform}"
                }
        except Exception as e:
            logger.error(f"Error posting to {platform}: {str(e)}")
            return {
                "success": False,
                "error": f"Error posting to {platform}: {str(e)}"
            }
            
    def _is_due(self, post: Dict[str, Any]) -> bool:
        """
        Check if a post is due to be published.
        
        Args:
            post: The post to check
            
        Returns:
            True if the post is due, False otherwise
        """
        try:
            schedule_time = post.get("schedule_time")
            if not schedule_time:
                return False
                
            # Parse the schedule time
            schedule_datetime = datetime.datetime.fromisoformat(schedule_time.replace("Z", "+00:00"))
            
            # Convert to UTC
            schedule_datetime = schedule_datetime.astimezone(datetime.timezone.utc)
            
            # Get the current time in UTC
            now = datetime.datetime.now(datetime.timezone.utc)
            
            # Check if the post is due
            return now >= schedule_datetime
        except Exception as e:
            logger.error(f"Error checking if post is due: {str(e)}")
            return False
            
    def run(self):
        """Run the scheduler."""
        logger.info("Starting post scheduler")
        
        try:
            while True:
                try:
                    # Load the schedule
                    schedule = self._load_schedule()
                    
                    # Check for posts that are due
                    posts_to_remove = []
                    for i, post in enumerate(schedule.get("scheduled_posts", [])):
                        if post.get("status") == "scheduled" and self._is_due(post):
                            logger.info(f"Publishing scheduled post: {post.get('id')}")
                            
                            # Post to the platform
                            result = self._post_to_platform(post)
                            
                            if result.get("success", False):
                                logger.info(f"Successfully published post: {post.get('id')}")
                                
                                # Update the post status
                                post["status"] = "published"
                                post["published_at"] = datetime.datetime.now().isoformat()
                                
                                # Handle different key names from different platforms
                                if result.get("post_id"):
                                    post["platform_post_id"] = result.get("post_id")
                                elif result.get("tweet_id"):
                                    post["platform_post_id"] = result.get("tweet_id")
                                
                                # Save the updated schedule
                                self._save_schedule(schedule)
                            else:
                                logger.error(f"Failed to publish post: {post.get('id')} - {result.get('error')}")
                                
                                # Update the post status
                                post["status"] = "failed"
                                post["error"] = result.get("error")
                                post["failed_at"] = datetime.datetime.now().isoformat()
                                
                                # Save the updated schedule
                                self._save_schedule(schedule)
                
                    # Sleep for the check interval
                    time.sleep(self.check_interval)
                except Exception as e:
                    logger.error(f"Error in scheduler loop: {str(e)}")
                    time.sleep(self.check_interval)  # Sleep and try again
                
        except KeyboardInterrupt:
            logger.info("Stopping post scheduler")
        except Exception as e:
            logger.error(f"Error in scheduler: {str(e)}")
            # Keep the process running instead of crashing
            time.sleep(60)
            self.run()  # Restart the scheduler

def main():
    """Main function to run the scheduler."""
    try:
        scheduler = PostScheduler()
        scheduler.run()
    except Exception as e:
        logger.error(f"Fatal error in scheduler main: {str(e)}")
        # Sleep before exiting to prevent rapid restarts
        time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Unhandled exception in scheduler: {str(e)}")
        # Sleep before exiting to prevent rapid restarts
        time.sleep(60)