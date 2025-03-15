import os
import json
import time
import datetime
import logging
from typing import Dict, Any, List
from src.tools.linkedin_tool import LinkedInTool
from src.tools.twitter_tool import TwitterTool
from src.main import respond_to_comments

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("monitor")

class SocialMediaMonitor:
    """
    A monitor for checking for comments on social media posts.
    """
    
    def __init__(self, schedule_file: str = "content_schedule.json", check_interval: int = 300):
        """
        Initialize the social media monitor.
        
        Args:
            schedule_file: Path to the schedule file
            check_interval: Interval in seconds to check for comments
        """
        self.schedule_file = schedule_file
        self.check_interval = check_interval
        self.linkedin_tool = LinkedInTool()
        self.twitter_tool = TwitterTool()
        self.comments_dir = "comments"
        self.responses_dir = "responses"
        
        # Ensure the comments and responses directories exist
        os.makedirs(self.comments_dir, exist_ok=True)
        os.makedirs(self.responses_dir, exist_ok=True)
        
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
            
    def _get_comments(self, platform: str, post_id: str) -> List[Dict[str, Any]]:
        """
        Get comments on a post.
        
        Args:
            platform: The platform to get comments from
            post_id: The ID of the post to get comments from
            
        Returns:
            A list of comments
        """
        if platform == "linkedin":
            result = self.linkedin_tool.get_post_comments(post_id)
            if result.get("success", False):
                return result.get("comments", [])
        elif platform == "twitter":
            result = self.twitter_tool.get_tweet_replies(post_id)
            if result.get("success", False):
                return result.get("replies", [])
                
        return []
        
    def _save_comments(self, post_id: str, comments: List[Dict[str, Any]]):
        """
        Save comments to a file.
        
        Args:
            post_id: The ID of the post the comments are on
            comments: The comments to save
        """
        try:
            comments_file = os.path.join(self.comments_dir, f"{post_id}_comments.json")
            with open(comments_file, "w") as f:
                json.dump(comments, f, indent=2)
                
            return comments_file
        except Exception as e:
            logger.error(f"Error saving comments: {str(e)}")
            return None
            
    def _load_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """
        Load comments from a file.
        
        Args:
            post_id: The ID of the post the comments are on
            
        Returns:
            A list of comments
        """
        try:
            comments_file = os.path.join(self.comments_dir, f"{post_id}_comments.json")
            if not os.path.exists(comments_file):
                return []
                
            with open(comments_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading comments: {str(e)}")
            return []
            
    def _save_responses(self, post_id: str, responses: str):
        """
        Save responses to a file.
        
        Args:
            post_id: The ID of the post the responses are for
            responses: The responses to save
        """
        try:
            responses_file = os.path.join(self.responses_dir, f"{post_id}_responses.txt")
            with open(responses_file, "w") as f:
                f.write(responses)
                
            return responses_file
        except Exception as e:
            logger.error(f"Error saving responses: {str(e)}")
            return None
            
    def _has_new_comments(self, post_id: str, current_comments: List[Dict[str, Any]]) -> bool:
        """
        Check if there are new comments.
        
        Args:
            post_id: The ID of the post to check
            current_comments: The current comments on the post
            
        Returns:
            True if there are new comments, False otherwise
        """
        # Load the previous comments
        previous_comments = self._load_comments(post_id)
        
        # Check if there are more comments now
        return len(current_comments) > len(previous_comments)
            
    def run(self):
        """Run the monitor."""
        logger.info("Starting social media monitor")
        
        try:
            while True:
                # Load the schedule
                schedule = self._load_schedule()
                
                # Check for published posts
                for post in schedule.get("scheduled_posts", []):
                    if post.get("status") == "published" and post.get("platform_post_id"):
                        platform = post.get("platform", "").lower()
                        post_id = post.get("platform_post_id")
                        
                        logger.info(f"Checking for comments on {platform} post: {post_id}")
                        
                        # Get the comments
                        comments = self._get_comments(platform, post_id)
                        
                        # Check if there are new comments
                        if self._has_new_comments(post_id, comments):
                            logger.info(f"New comments found on {platform} post: {post_id}")
                            
                            # Save the comments
                            comments_file = self._save_comments(post_id, comments)
                            
                            if comments_file:
                                # Generate responses
                                try:
                                    responses = respond_to_comments(platform, post_id, comments)
                                    
                                    # Save the responses
                                    responses_file = self._save_responses(post_id, responses)
                                    
                                    if responses_file:
                                        logger.info(f"Generated responses for {platform} post: {post_id}")
                                        logger.info(f"Responses saved to: {responses_file}")
                                except Exception as e:
                                    logger.error(f"Error generating responses: {str(e)}")
                        else:
                            logger.info(f"No new comments on {platform} post: {post_id}")
                
                # Sleep for the check interval
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping social media monitor")
        except Exception as e:
            logger.error(f"Error in monitor: {str(e)}")
            
def main():
    """Main function to run the monitor."""
    monitor = SocialMediaMonitor()
    monitor.run()
    
if __name__ == "__main__":
    main() 