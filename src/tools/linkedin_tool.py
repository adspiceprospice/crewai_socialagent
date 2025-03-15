import requests
import json
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import PrivateAttr
from src.config.config import (
    LINKEDIN_ACCESS_TOKEN,
    LINKEDIN_CLIENT_ID,
    LINKEDIN_CLIENT_SECRET
)

class LinkedInTool(BaseTool):
    """Tool for posting content to LinkedIn."""
    
    name: str = "LinkedIn Poster"
    description: str = "Post content to LinkedIn, including text and images."
    
    # Use PrivateAttr for instance attributes that shouldn't be part of the model
    _access_token: str = PrivateAttr()
    _api_url: str = PrivateAttr()
    
    def __init__(self):
        super().__init__()
        self._access_token = LINKEDIN_ACCESS_TOKEN
        self._api_url = "https://api.linkedin.com/v2"
        
    def _execute(
        self, 
        text: str, 
        image_path: Optional[str] = None,
        schedule_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content to LinkedIn.
        
        Args:
            text: The text content to post
            image_path: Optional path to an image to include in the post
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            Dictionary containing the result of the posting operation
        """
        try:
            # Get the user's LinkedIn URN
            user_info = self._get_user_info()
            if not user_info.get("success", False):
                return user_info
                
            user_urn = user_info.get("user_urn")
            
            # Create the post payload
            post_data = {
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add image if provided
            if image_path:
                # First, upload the image to LinkedIn
                image_upload_result = self._upload_image(image_path)
                if not image_upload_result.get("success", False):
                    return image_upload_result
                
                # Add the image to the post
                media_asset = image_upload_result.get("asset")
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": "Image"
                        },
                        "media": media_asset,
                        "title": {
                            "text": "Image"
                        }
                    }
                ]
            
            # Add scheduling if provided
            if schedule_time:
                post_data["distribution"] = {
                    "linkedInDistributionTarget": {
                        "visibleToGuest": True
                    }
                }
                post_data["scheduledTime"] = schedule_time
                post_data["lifecycleState"] = "SCHEDULED"
            
            # Make the API request to create the post
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = requests.post(
                f"{self._api_url}/ugcPosts",
                headers=headers,
                data=json.dumps(post_data)
            )
            
            if response.status_code in (200, 201):
                return {
                    "success": True,
                    "post_id": response.headers.get("x-restli-id", "Unknown"),
                    "message": "Successfully posted to LinkedIn"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to post to LinkedIn: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error posting to LinkedIn: {str(e)}"
            }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get the user's LinkedIn information."""
        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = requests.get(
                f"{self._api_url}/me",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "user_urn": f"urn:li:person:{data.get('id')}"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get user info: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting user info: {str(e)}"
            }
    
    def _upload_image(self, image_path: str) -> Dict[str, Any]:
        """Upload an image to LinkedIn."""
        try:
            # Get the user's LinkedIn URN
            user_info = self._get_user_info()
            if not user_info.get("success", False):
                return user_info
                
            user_urn = user_info.get("user_urn")
            
            # Step 1: Register the image upload
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": user_urn,
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            register_response = requests.post(
                f"{self._api_url}/assets?action=registerUpload",
                headers=headers,
                data=json.dumps(register_data)
            )
            
            if register_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to register image upload: {register_response.status_code} - {register_response.text}"
                }
                
            register_data = register_response.json()
            upload_url = register_data.get("value", {}).get("uploadMechanism", {}).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get("uploadUrl")
            asset = register_data.get("value", {}).get("asset")
            
            if not upload_url or not asset:
                return {
                    "success": False,
                    "error": "Failed to get upload URL or asset from registration response"
                }
            
            # Step 2: Upload the image
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                
            upload_headers = {
                "Authorization": f"Bearer {self._access_token}"
            }
            
            upload_response = requests.put(
                upload_url,
                headers=upload_headers,
                data=image_data
            )
            
            if upload_response.status_code != 201:
                return {
                    "success": False,
                    "error": f"Failed to upload image: {upload_response.status_code} - {upload_response.text}"
                }
                
            return {
                "success": True,
                "asset": asset,
                "message": "Successfully uploaded image to LinkedIn"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error uploading image: {str(e)}"
            }
            
    def get_post_comments(self, post_id: str) -> Dict[str, Any]:
        """Get comments on a LinkedIn post."""
        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = requests.get(
                f"{self._api_url}/socialActions/urn:li:share:{post_id}/comments",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "comments": data.get("elements", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get post comments: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting post comments: {str(e)}"
            }

    def _run(self, text: str, image_path: Optional[str] = None, schedule_time: Optional[str] = None) -> Dict[str, Any]:
        """
        Required method from BaseTool. Executes the LinkedIn posting operation.
        
        Args:
            text: The text content to post
            image_path: Optional path to an image to include in the post
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            Dictionary containing the result of the posting operation
        """
        return self._execute(text, image_path, schedule_time) 