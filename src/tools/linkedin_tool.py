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
        
    def _run(
        self, 
        text: str, 
        image_path: Optional[str] = None,
        schedule_time: Optional[str] = None
    ) -> str:
        """
        Required method from BaseTool. Executes the LinkedIn posting operation.
        
        Args:
            text: The text content to post
            image_path: Optional path to an image to include in the post
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            str: Result message of the posting operation
        """
        result = self._execute(text, image_path, schedule_time)
        if result.get("success", False):
            return f"Successfully posted to LinkedIn. Post ID: {result.get('post_id', 'N/A')}"
        else:
            return f"Error posting to LinkedIn: {result.get('error', 'Unknown error')}"
    
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
                # Try to post as an organization if user info fails
                import os
                org_id = os.getenv("LINKEDIN_ORGANIZATION_ID")
                if org_id:
                    return self._post_as_organization(text, image_path, org_id, schedule_time)
                else:
                    return user_info
                
            user_urn = user_info.get("user_urn")
            
            # Check if this is an organization URN
            is_org = "organization" in user_urn
            
            # Try using the Shares endpoint first (more reliable)
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # Create the shares payload
            shares_data = {
                "content": {
                    "contentEntities": [],
                    "title": "Post",
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": user_urn
            }
            
            # Add scheduling if provided
            if schedule_time:
                shares_data["scheduledAt"] = schedule_time
            
            # Add image if provided
            if image_path:
                # First, upload the image to LinkedIn
                image_upload_result = self._upload_image(image_path)
                if not image_upload_result.get("success", False):
                    return image_upload_result
                
                # Add the image to the post
                media_asset = image_upload_result.get("asset")
                
                # Update the shares data with the image
                shares_data["content"]["shareMediaCategory"] = "IMAGE"
                shares_data["content"]["contentEntities"] = [
                    {
                        "entity": media_asset
                    }
                ]
            
            # Try posting with the shares endpoint
            shares_response = requests.post(
                f"{self._api_url}/shares",
                headers=headers,
                json=shares_data,
                allow_redirects=True
            )
            
            if shares_response.status_code in [200, 201]:
                post_id = shares_response.headers.get("x-restli-id") or shares_response.json().get("id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Successfully posted to LinkedIn using shares endpoint"
                }
            
            # If shares endpoint fails, fall back to UGC Posts endpoint
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
                # We already uploaded the image above
                # Update the post data with the image
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
            
            # Post to LinkedIn
            response = requests.post(
                f"{self._api_url}/ugcPosts",
                headers=headers,
                json=post_data,
                allow_redirects=True  # Allow redirects for 302 responses
            )
            
            if response.status_code in [200, 201]:
                post_id = response.headers.get("x-restli-id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Successfully posted to LinkedIn"
                }
            elif response.status_code == 302:
                # Handle redirect - this is common with LinkedIn API
                redirect_url = response.headers.get('Location')
                if redirect_url:
                    redirect_response = requests.post(
                        redirect_url,
                        headers=headers,
                        json=post_data,
                        allow_redirects=True
                    )
                    
                    if redirect_response.status_code in [200, 201]:
                        post_id = redirect_response.headers.get("x-restli-id") or redirect_response.json().get("id")
                        return {
                            "success": True,
                            "post_id": post_id,
                            "message": "Successfully posted to LinkedIn (after redirect)"
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"Failed to post to LinkedIn after redirect: {redirect_response.status_code} - {redirect_response.text}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Received redirect without Location header: {response.status_code} - {response.text}"
                    }
            elif response.status_code == 403 and "ACCESS_DENIED" in response.text:
                # If both methods fail with ACCESS_DENIED, provide a detailed error message
                return {
                    "success": False,
                    "error": f"""
LinkedIn API permission error: Your access token doesn't have the necessary permissions.
Error details: {response.status_code} - {response.text}

To fix this issue:
1. Make sure your LinkedIn access token has the following permissions:
   - w_member_social (for posting as yourself)
   - r_liteprofile (for accessing your profile)
   - w_organization_social (for posting as an organization)
2. Generate a new access token with the correct permissions using the LinkedIn Developer Console
3. If you want to post as an organization, make sure you've added LINKEDIN_ORGANIZATION_ID to your .env file

For more information, see the LinkedIn API documentation:
https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
"""
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
            
    def _post_as_organization(
        self,
        text: str,
        image_path: Optional[str] = None,
        org_id: str = None,
        schedule_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post content as an organization.
        
        Args:
            text: The text content to post
            image_path: Optional path to an image to include in the post
            org_id: LinkedIn organization ID
            schedule_time: Optional ISO-8601 timestamp for scheduling the post
            
        Returns:
            Dictionary containing the result of the posting operation
        """
        try:
            if not org_id:
                return {
                    "success": False,
                    "error": "Organization ID is required for organization posting"
                }
                
            # Create the organization URN
            org_urn = f"urn:li:organization:{org_id}"
            
            # First, check if we have permission to post as this organization
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            # Try to get organization info to verify permissions
            org_check_response = requests.get(
                f"{self._api_url}/organizations/{org_id}",
                headers=headers,
                allow_redirects=True  # Allow redirects for 302 responses
            )
            
            if org_check_response.status_code != 200:
                return {
                    "success": False,
                    "error": f"""
LinkedIn API permission error: Your access token doesn't have the necessary permissions.
Error details: {org_check_response.status_code} - {org_check_response.text}

To fix this issue:
1. Make sure your LinkedIn access token has the following permissions:
   - w_member_social (for posting as yourself)
   - r_liteprofile (for accessing your profile)
   - w_organization_social (for posting as an organization)
2. Generate a new access token with the correct permissions using the LinkedIn Developer Console
3. If you want to post as an organization, make sure you've added LINKEDIN_ORGANIZATION_ID to your .env file

For more information, see the LinkedIn API documentation:
https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
"""
                }
                
            # Add image if provided
            if image_path:
                # For organization posts, we need to use a different endpoint for image upload
                # This is a simplified version - in a real implementation, you'd need to handle
                # the organization asset upload properly
                return {
                    "success": False,
                    "error": "Image upload for organization posts is not supported in this version. Please post text only."
                }
            
            # Try multiple approaches for posting as an organization
            
            # Approach 1: Try the organization shares endpoint
            shares_data = {
                "content": {
                    "contentEntities": [],
                    "title": "Post",
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": org_urn
            }
            
            # Add scheduling if provided
            if schedule_time:
                shares_data["scheduledAt"] = schedule_time
            
            shares_response = requests.post(
                f"{self._api_url}/shares",
                headers=headers,
                json=shares_data,
                allow_redirects=True
            )
            
            if shares_response.status_code in [200, 201]:
                post_id = shares_response.headers.get("x-restli-id") or shares_response.json().get("id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Successfully posted to LinkedIn as organization using shares endpoint"
                }
            
            # Approach 2: Try the UGC Posts endpoint
            ugc_post_data = {
                "author": org_urn,
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
            
            # Add scheduling if provided
            if schedule_time:
                ugc_post_data["distribution"] = {
                    "linkedInDistributionTarget": {
                        "visibleToGuest": True
                    }
                }
                ugc_post_data["scheduledTime"] = schedule_time
                ugc_post_data["lifecycleState"] = "SCHEDULED"
            
            ugc_response = requests.post(
                f"{self._api_url}/ugcPosts",
                headers=headers,
                json=ugc_post_data,
                allow_redirects=True
            )
            
            if ugc_response.status_code in [200, 201]:
                post_id = ugc_response.headers.get("x-restli-id")
                return {
                    "success": True,
                    "post_id": post_id,
                    "message": "Successfully posted to LinkedIn as organization using UGC Posts endpoint"
                }
            
            # Approach 3: Try the organization assets endpoint
            try:
                # This is a newer approach that some organizations might have access to
                assets_data = {
                    "registerUploadRequest": {
                        "recipes": ["urn:li:digitalmediaRecipe:feedshare-text"],
                        "owner": org_urn,
                        "serviceRelationships": [
                            {
                                "relationshipType": "OWNER",
                                "identifier": "urn:li:userGeneratedContent"
                            }
                        ],
                        "text": text
                    }
                }
                
                assets_response = requests.post(
                    f"{self._api_url}/assets?action=registerUpload",
                    headers=headers,
                    json=assets_data,
                    allow_redirects=True
                )
                
                if assets_response.status_code in [200, 201]:
                    asset_data = assets_response.json()
                    asset_id = asset_data.get("value", {}).get("asset")
                    
                    if asset_id:
                        return {
                            "success": True,
                            "post_id": asset_id,
                            "message": "Successfully posted to LinkedIn as organization using assets endpoint"
                        }
                
            except Exception as e:
                # Just continue to the next approach if this fails
                pass
            
            # If all approaches fail, return a detailed error message
            return {
                "success": False,
                "error": f"""
LinkedIn API permission error: Your access token doesn't have permission to post as this organization.
Error details from shares endpoint: {shares_response.status_code} - {shares_response.text}
Error details from UGC Posts endpoint: {ugc_response.status_code} - {ugc_response.text}

To fix this issue:
1. Make sure you've added the correct organization ID to your .env file (current: {org_id})
2. Ensure your LinkedIn access token has the following permissions:
   - w_organization_social
   - r_organization_social
   - rw_organization_admin
3. The user who generated the access token must be an admin of the organization
4. Generate a new access token with the correct permissions using the LinkedIn Developer Console

For more information, see the LinkedIn API documentation:
https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
"""
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error posting to LinkedIn as organization: {str(e)}"
            }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get the user's LinkedIn information."""
        try:
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            # First try to get the profile using /v2/me
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
            elif response.status_code == 403 and "ACCESS_DENIED" in response.text:
                # If we get an access denied error, try the /v2/userinfo endpoint instead
                # This endpoint is available with the r_liteprofile permission
                response = requests.get(
                    f"{self._api_url}/userinfo",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "user_urn": f"urn:li:person:{data.get('sub')}"
                    }
                else:
                    # If both endpoints fail, try to use the organization URN instead
                    # This requires the organization ID to be set in the environment
                    import os
                    org_id = os.getenv("LINKEDIN_ORGANIZATION_ID")
                    if org_id:
                        return {
                            "success": True,
                            "user_urn": f"urn:li:organization:{org_id}"
                        }
                    else:
                        # As a last resort, try to extract the person ID from the access token
                        # This is a fallback and may not work in all cases
                        return {
                            "success": False,
                            "error": "LinkedIn API permission error: Your access token doesn't have the necessary permissions. Please update your LinkedIn API permissions to include r_liteprofile or provide an organization ID."
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
                data=json.dumps(register_data),
                allow_redirects=True  # Allow redirects for 302 responses
            )
            
            if register_response.status_code == 302:
                # Handle redirect
                redirect_url = register_response.headers.get('Location')
                if redirect_url:
                    register_response = requests.post(
                        redirect_url,
                        headers=headers,
                        data=json.dumps(register_data),
                        allow_redirects=True
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
                data=image_data,
                allow_redirects=True  # Allow redirects for 302 responses
            )
            
            if upload_response.status_code == 302:
                # Handle redirect
                redirect_url = upload_response.headers.get('Location')
                if redirect_url:
                    upload_response = requests.put(
                        redirect_url,
                        headers=upload_headers,
                        data=image_data,
                        allow_redirects=True
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
    
    def check_permissions(self) -> Dict[str, Any]:
        """
        Check the permissions of the LinkedIn access token.
        
        Returns:
            Dictionary containing the result of the permission check
        """
        try:
            results = {
                "success": True,
                "permissions": {},
                "message": "LinkedIn API permission check completed",
                "recommendations": []
            }
            
            # Check if we can access the /me endpoint (requires r_liteprofile)
            me_response = requests.get(
                f"{self._api_url}/me",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
            )
            
            results["permissions"]["r_liteprofile"] = me_response.status_code == 200
            
            if me_response.status_code != 200:
                results["recommendations"].append(
                    "Add r_liteprofile permission to access your LinkedIn profile"
                )
            
            # Check if we can access the /userinfo endpoint
            userinfo_response = requests.get(
                f"{self._api_url}/userinfo",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
            )
            
            results["permissions"]["userinfo"] = userinfo_response.status_code == 200
            
            # Check if we can post as a member (requires w_member_social)
            # We don't actually post, just check the permissions
            member_post_check = requests.get(
                f"{self._api_url}/socialActions",
                headers={
                    "Authorization": f"Bearer {self._access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }
            )
            
            results["permissions"]["w_member_social"] = "w_member_social" in member_post_check.text or member_post_check.status_code == 200
            
            if not results["permissions"]["w_member_social"]:
                results["recommendations"].append(
                    "Add w_member_social permission to post content as yourself"
                )
            
            # Check if we have an organization ID
            import os
            org_id = os.getenv("LINKEDIN_ORGANIZATION_ID")
            results["permissions"]["has_organization_id"] = bool(org_id)
            
            if not results["permissions"]["has_organization_id"]:
                results["recommendations"].append(
                    "Add LINKEDIN_ORGANIZATION_ID to your .env file to post as an organization"
                )
            
            # If we have an organization ID, check if we can access it
            if org_id:
                org_response = requests.get(
                    f"{self._api_url}/organizations/{org_id}",
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                
                results["permissions"]["organization_access"] = org_response.status_code == 200
                
                if org_response.status_code != 200:
                    results["recommendations"].append(
                        "Make sure your access token has permission to access the organization or check if the organization ID is correct"
                    )
                
                # Check if we can post as the organization
                org_post_check = requests.get(
                    f"{self._api_url}/organizations/{org_id}/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "X-Restli-Protocol-Version": "2.0.0"
                    }
                )
                
                results["permissions"]["w_organization_social"] = "w_organization_social" in org_post_check.text or org_post_check.status_code == 200
                
                if not results["permissions"]["w_organization_social"]:
                    results["recommendations"].append(
                        "Add w_organization_social permission to post content as your organization"
                    )
            
            # Add overall recommendations
            if not any(results["permissions"].values()):
                results["recommendations"].append(
                    "Your access token appears to have no valid permissions. Generate a new token with the required permissions."
                )
            
            if results["recommendations"]:
                results["message"] = "LinkedIn API permission issues detected. See recommendations."
            
            return results
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error checking LinkedIn permissions: {str(e)}"
            }
    
    def debug_post(self, text: str, org_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Debug LinkedIn posting by trying different methods.
        
        Args:
            text: The text content to post
            org_id: Optional organization ID to post as
            
        Returns:
            Dictionary containing the results of all posting attempts
        """
        results = {
            "success": False,
            "attempts": [],
            "recommendations": []
        }
        
        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # 1. Get user info
        user_info = self._get_user_info()
        results["user_info"] = {
            "success": user_info.get("success", False),
            "user_urn": user_info.get("user_urn", "Not available"),
            "error": user_info.get("error", None)
        }
        
        # 2. Try to post as user if we have user info
        if user_info.get("success", False) and "person" in user_info.get("user_urn", ""):
            user_urn = user_info.get("user_urn")
            
            # Try ugcPosts endpoint
            ugc_post_data = {
                "author": user_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{text} (UGC test)"
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            try:
                ugc_response = requests.post(
                    f"{self._api_url}/ugcPosts",
                    headers=headers,
                    json=ugc_post_data,
                    allow_redirects=True
                )
                
                results["attempts"].append({
                    "method": "ugcPosts_as_user",
                    "success": ugc_response.status_code in [200, 201],
                    "status_code": ugc_response.status_code,
                    "response": ugc_response.text[:500] if ugc_response.text else None
                })
                
                if ugc_response.status_code in [200, 201]:
                    results["success"] = True
                    results["recommendations"].append("Use ugcPosts endpoint for user posting")
            except Exception as e:
                results["attempts"].append({
                    "method": "ugcPosts_as_user",
                    "success": False,
                    "error": str(e)
                })
        
        # 3. Try to post as organization if org_id is provided
        if org_id:
            org_urn = f"urn:li:organization:{org_id}"
            
            # Try ugcPosts endpoint for organization
            org_ugc_post_data = {
                "author": org_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": f"{text} (Org UGC test)"
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            try:
                org_ugc_response = requests.post(
                    f"{self._api_url}/ugcPosts",
                    headers=headers,
                    json=org_ugc_post_data,
                    allow_redirects=True
                )
                
                results["attempts"].append({
                    "method": "ugcPosts_as_organization",
                    "success": org_ugc_response.status_code in [200, 201],
                    "status_code": org_ugc_response.status_code,
                    "response": org_ugc_response.text[:500] if org_ugc_response.text else None
                })
                
                if org_ugc_response.status_code in [200, 201]:
                    results["success"] = True
                    results["recommendations"].append("Use ugcPosts endpoint for organization posting")
            except Exception as e:
                results["attempts"].append({
                    "method": "ugcPosts_as_organization",
                    "success": False,
                    "error": str(e)
                })
            
            # Try shares endpoint for organization
            org_shares_post_data = {
                "content": {
                    "contentEntities": [],
                    "title": "Test Post",
                    "shareCommentary": {
                        "text": f"{text} (Org shares test)"
                    },
                    "shareMediaCategory": "NONE"
                },
                "distribution": {
                    "linkedInDistributionTarget": {}
                },
                "owner": org_urn
            }
            
            try:
                org_shares_response = requests.post(
                    f"{self._api_url}/shares",
                    headers=headers,
                    json=org_shares_post_data,
                    allow_redirects=True
                )
                
                results["attempts"].append({
                    "method": "shares_as_organization",
                    "success": org_shares_response.status_code in [200, 201],
                    "status_code": org_shares_response.status_code,
                    "response": org_shares_response.text[:500] if org_shares_response.text else None
                })
                
                if org_shares_response.status_code in [200, 201]:
                    results["success"] = True
                    results["recommendations"].append("Use shares endpoint for organization posting")
            except Exception as e:
                results["attempts"].append({
                    "method": "shares_as_organization",
                    "success": False,
                    "error": str(e)
                })
        
        # 4. Add recommendations based on results
        if not results["success"]:
            results["recommendations"].append("Check your LinkedIn access token permissions")
            results["recommendations"].append("Make sure your token has w_member_social and w_organization_social permissions")
            
            if org_id:
                results["recommendations"].append("Verify that you have admin access to the organization")
        
        return results 