
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
