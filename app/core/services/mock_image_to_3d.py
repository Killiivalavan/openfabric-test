import logging
import os
import json
import random
from typing import Dict, Any, Optional, Tuple

from core.stub import Stub
from core.utils.resource_handler import ResourceHandler


class MockImageTo3DService:
    """
    Mock implementation of ImageTo3DService that generates a simple text file
    instead of calling the external Openfabric service.
    """
    
    # Mock app ID to match the real service
    APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"
    
    def __init__(self, stub: Stub = None, resource_handler: ResourceHandler = None):
        """
        Initialize the Mock Image-to-3D service.
        
        Args:
            stub: Not used in mock, but included for interface compatibility
            resource_handler: The ResourceHandler for saving 3D models
        """
        self.stub = stub
        self.resource_handler = resource_handler or ResourceHandler()
        self.logger = logging.getLogger("mock_image_to_3d_service")
        self.logger.info("Initialized Mock Image-to-3D Service")
        
    def generate_3d_model(self, image_data: bytes, user_id: str = 'mock-user') -> Tuple[Optional[bytes], Optional[str], Dict[str, Any]]:
        """
        Generate a simple text file instead of a 3D model.
        
        Args:
            image_data: The image data (not used in the mock)
            user_id: User ID (not used in mock)
            
        Returns:
            Tuple containing:
            - Text file data (bytes)
            - Path to saved file
            - Metadata about the generation
        """
        try:
            self.logger.info("Generating mock 3D model (text file)")
            
            # Create a simple text representation
            mock_data = {
                "mock": True,
                "description": "Mock 3D model data - Openfabric services unavailable",
                "timestamp": str(random.randint(1000000, 9999999)),
                "model_type": "cube"
            }
            
            # Convert to bytes
            model_data = json.dumps(mock_data, indent=2).encode('utf-8')
            
            # Save the 3D model
            model_path = self.resource_handler.save_model(model_data)
            self.logger.info(f"Mock 3D model (text file) saved to {model_path}")
            
            # Prepare metadata
            metadata = {
                "success": True,
                "mock": True,
                "format": "text"
            }
            
            return model_data, model_path, metadata
            
        except Exception as e:
            self.logger.error(f"Error generating mock 3D model: {str(e)}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None, None, {"error": str(e)}
            
    def get_schema(self) -> Dict[str, Any]:
        """
        Get a mock schema for the Image-to-3D app.
        
        Returns:
            Dict containing a simple mock input schema
        """
        return {
            "image": {
                "type": "string",
                "description": "Base64 encoded image to generate a 3D model from"
            }
        } 