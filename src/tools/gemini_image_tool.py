import os
import base64
import google.generativeai as genai
from crewai.tools import BaseTool
from typing import Dict, Any, Optional
from src.config.config import GEMINI_API_KEY

class GeminiImageTool(BaseTool):
    """Tool that generates images using Google's Gemini 2.0 Flash model."""
    
    name: str = "Gemini Image Generator"
    description: str = "Generate images based on text descriptions using Google's Gemini 2.0 Flash model."
    
    def __init__(self):
        super().__init__()
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = "gemini-2.0-flash-exp-image-generation"
        
    def _save_binary_file(self, file_name: str, data: bytes) -> str:
        """Save binary data to a file."""
        os.makedirs("generated_images", exist_ok=True)
        file_path = os.path.join("generated_images", file_name)
        with open(file_path, "wb") as f:
            f.write(data)
        return file_path
    
    def _execute(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an image based on the provided prompt.
        
        Args:
            prompt: Text description of the image to generate
            reference_image_path: Optional path to a reference image
            
        Returns:
            Dictionary containing the path to the generated image
        """
        try:
            client = genai.Client()
            contents = []
            
            # Add reference image if provided
            if reference_image_path and os.path.exists(reference_image_path):
                file = client.files.upload(file=reference_image_path)
                contents.append({
                    "role": "user",
                    "parts": [
                        {"file_uri": file.uri, "mime_type": file.mime_type},
                        {"text": prompt}
                    ]
                })
            else:
                contents.append({
                    "role": "user",
                    "parts": [{"text": prompt}]
                })
            
            # Generate the image
            response = client.models.generate_content(
                model=self.model,
                contents=contents,
                generation_config={
                    "temperature": 1,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "response_modalities": ["image", "text"],
                    "response_mime_type": "text/plain",
                }
            )
            
            # Process the response
            if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Generate a unique filename
                    import time
                    timestamp = int(time.time())
                    file_name = f"gemini_image_{timestamp}.png"
                    
                    # Save the image
                    file_path = self._save_binary_file(file_name, part.inline_data.data)
                    
                    return {
                        "success": True,
                        "image_path": file_path,
                        "mime_type": part.inline_data.mime_type
                    }
                else:
                    return {
                        "success": False,
                        "error": "No image data in response",
                        "text_response": part.text if hasattr(part, 'text') else "No text response"
                    }
            
            return {
                "success": False,
                "error": "Failed to generate image"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 