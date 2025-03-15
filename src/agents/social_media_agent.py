
    def post_content(self, content: str, platform: str, image_path: Optional[str] = None) -> dict:
        """
        Post content immediately.
        
        Args:
            content (str): The content to post
            platform (str): The target platform
            image_path (Optional[str]): Path to an image to include with the post
            
        Returns:
            dict: Posting confirmation and metadata
        """
        logger.info(f"Posting content to {platform}")
        try:
            if platform.lower() == "linkedin":
                tool = next((tool for tool in self.tools if isinstance(tool, LinkedInTool)), None)
            elif platform.lower() in ["twitter", "x"]:
                tool = next((tool for tool in self.tools if isinstance(tool, TwitterTool)), None)
            else:
                logger.error(f"Unsupported platform: {platform}")
                return {"error": f"Unsupported platform: {platform}"}
                
            if tool:
                # Execute the post and capture the full result
                result = tool._execute(text=content, image_path=image_path)
                
                # Check if the post was successful
                if result.get("success", False):
                    # Ensure we have a consistent result format
                    return {
                        "success": True,
                        "post_id": result.get("post_id") or result.get("tweet_id"),
                        "message": f"Successfully posted to {platform}"
                    }
                else:
                    # Return the error from the tool
                    return result
            else:
                logger.error(f"{platform} tool not found")
                return {"error": f"{platform} tool not found"}
        except Exception as e:
            logger.error(f"Error posting content: {str(e)}")
            return {"error": f"Error posting content: {str(e)}"}
