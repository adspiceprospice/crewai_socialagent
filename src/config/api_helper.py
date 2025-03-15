"""
API helper functions for social media platforms.
"""

from typing import Dict, Any, Optional

def normalize_post_response(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize post response from different platforms to ensure consistency.
    
    Args:
        result: The response from the platform API
        
    Returns:
        Normalized response with consistent keys
    """
    if not result:
        return {"success": False, "error": "Empty result"}
        
    # Make a copy of the result to avoid modifying the original
    normalized = result.copy()
    
    # Handle tweet_id for Twitter
    if "tweet_id" in result and "post_id" not in result:
        normalized["post_id"] = result["tweet_id"]
        
    # Ensure there's a message field
    if "message" not in normalized:
        if normalized.get("success", False):
            platform = "the platform"
            normalized["message"] = f"Successfully posted to {platform}"
        else:
            normalized["message"] = normalized.get("error", "Unknown error")
            
    return normalized
