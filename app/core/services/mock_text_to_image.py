import os
import base64
import io
import random
import logging
from typing import Dict, Any, Optional, Tuple
import json

from core.utils.resource_handler import ResourceHandler

class MockTextToImageService:
    """
    Mock implementation of TextToImageService that generates a simple text-based image
    instead of calling the external Openfabric service.
    """
    
    # Mock app ID to match the real service
    APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
    
    def __init__(self, stub=None, resource_handler: ResourceHandler=None):
        """
        Initialize the Mock Text-to-Image service.
        
        Args:
            stub: Not used in mock, but included for interface compatibility
            resource_handler: The ResourceHandler for saving images
        """
        self.stub = stub
        self.resource_handler = resource_handler or ResourceHandler()
        self.logger = logging.getLogger("mock_text_to_image_service")
        self.logger.info("Initialized Mock Text-to-Image Service")
    
    def generate_image(self, prompt: str, user_id: str = 'mock-user') -> Tuple[Optional[bytes], Optional[str], Dict[str, Any]]:
        """
        Generate a simple text file containing the prompt instead of an actual image
        
        Args:
            prompt: Text prompt to visualize
            user_id: User ID (not used in mock)
            
        Returns:
            Tuple containing:
            - Text file data (bytes)
            - Path to saved file
            - Metadata about the generation
        """
        self.logger.info(f"Mock generating text file from prompt: {prompt}")
        
        try:
            # Create a simple text representation as a placeholder for an image
            mock_data = {
                "mock": True,
                "prompt": prompt,
                "description": "Mock image data - Openfabric services unavailable",
                "timestamp": str(random.randint(1000000, 9999999))
            }
            
            # Convert to JSON
            text_content = json.dumps(mock_data, indent=2)
            
            # Convert to bytes
            image_data = text_content.encode('utf-8')
            
            # Save the data using the resource handler
            # Use .txt extension for the mock file but store as image
            image_path = self.resource_handler.save_image(image_data)
            self.logger.info(f"Mock image (text file) saved to: {image_path}")
            
            # Return the same tuple structure as the real service
            metadata = {
                "prompt": prompt,
                "success": True,
                "mock": True,
                "format": "text"
            }
            
            return image_data, image_path, metadata
            
        except Exception as e:
            self.logger.error(f"Error generating mock text representation: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None, None, {"error": str(e)}
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get a mock schema for the Text-to-Image app.
        
        Returns:
            Dict containing a simple mock input schema
        """
        return {
            "prompt": {
                "type": "string",
                "description": "Text prompt to generate an image from"
            }
        } 