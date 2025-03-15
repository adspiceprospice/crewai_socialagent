import requests
import json
import base64
import hmac
import hashlib
import time
import os
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import PrivateAttr
from src.config.config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

class TwitterTool(BaseTool):
    """Tool for posting content to X.com (Twitter)."""
    
    name: str = "Twitter Poster"
    description: str = "Post content to X.com (Twitter), including text and images."
    
    # Use PrivateAttr for instance attributes that shouldn't be part of the model
    _api_key: str = PrivateAttr()
    _api_secret: str = PrivateAttr()
    _access_token: str = PrivateAttr()
    _access_token_secret: str = PrivateAttr()
    _api_url: str = PrivateAttr()
    
    def __init__(self):
        super().__init__()
        self._api_key = TWITTER_API_KEY
        self._api_secret = TWITTER_API_SECRET
        self._access_token = TWITTER_ACCESS_TOKEN
        self._access_token_secret = TWITTER_ACCESS_TOKEN_SECRET
        self._api_url = "https://api.twitter.com/2"
        
    def _run(
        self, 
        text: str, 
        image_path: Optional[str] = None,
        schedule_time: Optional[str] = None
    ) -> str:
        """
        Required method from BaseTool. Executes the Twitter posting operation.
        
        Args:
            text: The text content to post (max 280 characters)
            image_path: Optional path to an image to include in the post
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            str: Result message of the posting operation
        """
        result = self._execute(text, image_path, schedule_time)
        if result.get("success", False):
            return f"Successfully posted to Twitter. Tweet ID: {result.get('tweet_id', 'N/A')}"
        else:
            return f"Error posting to Twitter: {result.get('error', 'Unknown error')}"
    
    def _execute(
        self, 
        text: str, 
        image_path: Optional[str] = None,
        schedule_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content to X.com (Twitter).
        
        Args:
            text: The text content to post (max 280 characters)
            image_path: Optional path to an image to include in the post
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            Dictionary containing the result of the posting operation
        """
        try:
            # Truncate text if it's too long
            if len(text) > 280:
                text = text[:277] + "..."
                
            # Create the post payload
            post_data = {
                "text": text
            }
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                # First, upload the image to Twitter
                media_id = self._upload_media(image_path)
                if not media_id:
                    return {
                        "success": False,
                        "error": "Failed to upload image to Twitter"
                    }
                
                # Add the media ID to the post
                post_data["media"] = {
                    "media_ids": [media_id]
                }
            
            # Add scheduling if provided
            if schedule_time:
                # Convert ISO-8601 to UNIX timestamp
                from datetime import datetime
                import dateutil.parser
                dt = dateutil.parser.parse(schedule_time)
                unix_timestamp = int(dt.timestamp())
                
                post_data["scheduled_at"] = unix_timestamp
                
                # Use the scheduled tweets endpoint
                endpoint = f"{self._api_url}/tweets/scheduled"
            else:
                # Use the regular tweets endpoint
                endpoint = f"{self._api_url}/tweets"
            
            # Make the API request to create the post
            headers = self._get_auth_headers("POST", endpoint)
            headers["Content-Type"] = "application/json"
            
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(post_data)
            )
            
            if response.status_code in (200, 201):
                data = response.json()
                return {
                    "success": True,
                    "tweet_id": data.get("data", {}).get("id"),
                    "post_id": data.get("data", {}).get("id"),  # Add post_id for consistency with LinkedInTool
                    "message": "Successfully posted to Twitter"
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to post to Twitter: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error posting to Twitter: {str(e)}"
            }
    
    def _upload_media(self, image_path: str) -> Optional[str]:
        """Upload media to Twitter and return the media ID."""
        try:
            # Twitter v1.1 API for media upload
            upload_url = "https://upload.twitter.com/1.1/media/upload.json"
            
            # Read the image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Encode the image data
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            # Get the file size
            file_size = os.path.getsize(image_path)
            
            # Get the MIME type
            import mimetypes
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/jpeg"  # Default to JPEG if can't determine
            
            # INIT phase
            init_data = {
                "command": "INIT",
                "total_bytes": file_size,
                "media_type": mime_type
            }
            
            headers = self._get_auth_headers("POST", upload_url, params=init_data)
            
            init_response = requests.post(
                upload_url,
                headers=headers,
                data=init_data
            )
            
            if init_response.status_code != 200:
                print(f"Failed to initialize media upload: {init_response.status_code} - {init_response.text}")
                return None
                
            media_id = init_response.json().get("media_id_string")
            
            # APPEND phase
            # Split the image into chunks if it's large
            chunk_size = 5 * 1024 * 1024  # 5MB chunks
            chunks = [image_data[i:i+chunk_size] for i in range(0, len(image_data), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                append_data = {
                    "command": "APPEND",
                    "media_id": media_id,
                    "segment_index": i
                }
                
                files = {
                    "media": chunk
                }
                
                headers = self._get_auth_headers("POST", upload_url, params=append_data)
                
                append_response = requests.post(
                    upload_url,
                    headers=headers,
                    data=append_data,
                    files=files
                )
                
                if append_response.status_code != 200:
                    print(f"Failed to append media chunk: {append_response.status_code} - {append_response.text}")
                    return None
            
            # FINALIZE phase
            finalize_data = {
                "command": "FINALIZE",
                "media_id": media_id
            }
            
            headers = self._get_auth_headers("POST", upload_url, params=finalize_data)
            
            finalize_response = requests.post(
                upload_url,
                headers=headers,
                data=finalize_data
            )
            
            if finalize_response.status_code != 200:
                print(f"Failed to finalize media upload: {finalize_response.status_code} - {finalize_response.text}")
                return None
                
            return media_id
            
        except Exception as e:
            print(f"Error uploading media to Twitter: {str(e)}")
            return None
    
    def _get_auth_headers(self, method: str, url: str, params: Dict[str, Any] = None) -> Dict[str, str]:
        """Generate OAuth 1.0a authentication headers for Twitter API requests."""
        oauth_timestamp = str(int(time.time()))
        oauth_nonce = hashlib.md5(str(time.time()).encode()).hexdigest()
        
        oauth_params = {
            "oauth_consumer_key": self._api_key,
            "oauth_nonce": oauth_nonce,
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": oauth_timestamp,
            "oauth_token": self._access_token,
            "oauth_version": "1.0"
        }
        
        # Combine OAuth params with request params
        all_params = {}
        if params:
            all_params.update(params)
        all_params.update(oauth_params)
        
        # Create the parameter string
        param_string = "&".join([f"{key}={all_params[key]}" for key in sorted(all_params.keys())])
        
        # Create the signature base string
        signature_base = f"{method}&{requests.utils.quote(url, safe='')}&{requests.utils.quote(param_string, safe='')}"
        
        # Create the signing key
        signing_key = f"{requests.utils.quote(self._api_secret, safe='')}&{requests.utils.quote(self._access_token_secret, safe='')}"
        
        # Generate the signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                signature_base.encode(),
                hashlib.sha1
            ).digest()
        ).decode()
        
        # Add the signature to the OAuth params
        oauth_params["oauth_signature"] = signature
        
        # Create the Authorization header
        auth_header = "OAuth " + ", ".join([f'{key}="{requests.utils.quote(oauth_params[key], safe="")}"' for key in oauth_params])
        
        return {
            "Authorization": auth_header
        }
        
    def get_tweet_replies(self, tweet_id: str) -> Dict[str, Any]:
        """Get replies to a tweet."""
        try:
            endpoint = f"{self._api_url}/tweets/search/recent"
            params = {
                "query": f"conversation_id:{tweet_id}",
                "tweet.fields": "in_reply_to_user_id,author_id,created_at,conversation_id"
            }
            
            # Convert params to query string
            query_string = "&".join([f"{key}={params[key]}" for key in params])
            url = f"{endpoint}?{query_string}"
            
            headers = self._get_auth_headers("GET", url)
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "replies": data.get("data", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to get tweet replies: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error getting tweet replies: {str(e)}"
            }
