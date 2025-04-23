import logging
import json
from typing import Dict, Any, Optional, Tuple

from core.stub import Stub
from core.utils.resource_handler import ResourceHandler

# Configure detailed logging
logger = logging.getLogger('text_to_image_service')

class TextToImageService:
    """
    Service for generating images from text prompts using the Openfabric Text-to-Image app.
    """
    
    # Openfabric Text-to-Image app ID with domain
    APP_ID = "f0997a01-d6d3-a5fe-53d8-561300318557"
    
    def __init__(self, stub: Stub, resource_handler: ResourceHandler):
        """
        Initialize the Text-to-Image service.
        
        Args:
            stub: The Openfabric SDK Stub instance
            resource_handler: The ResourceHandler for saving images
        """
        self.stub = stub
        self.resource_handler = resource_handler
        logger.info(f"Text-to-Image service initialized with APP_ID: {self.APP_ID}")
        
        # Try to get schema information to verify connection
        try:
            schema = self.get_schema()
            logger.info(f"Successfully retrieved Text-to-Image schema with {len(schema)} properties")
            logger.debug(f"Schema: {json.dumps(schema, indent=2)}")
        except Exception as e:
            logger.error(f"Failed to retrieve Text-to-Image schema: {str(e)}")
        
    def generate_image(self, prompt: str, user_id: str = 'super-user') -> Tuple[Optional[bytes], Optional[str], Dict[str, Any]]:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: The text prompt to generate an image from
            user_id: User ID for the Openfabric API call
            
        Returns:
            Tuple containing:
            - Image data (bytes or None if failed)
            - Path to saved image (or None if failed)
            - Metadata about the generation
        """
        try:
            logger.info(f"Generating image for prompt: '{prompt}'")
            
            # Prepare request data based on the app's schema
            request_data = {"prompt": prompt}
            logger.debug(f"Request data: {request_data}")
            
            # Call the Text-to-Image service
            logger.info(f"Calling Text-to-Image service with APP_ID: {self.APP_ID}")
            response = self.stub.call(self.APP_ID, request_data, user_id)
            
            if not response:
                logger.error("Empty response from Text-to-Image service")
                return None, None, {"error": "Empty response"}
                
            logger.info(f"Received response from Text-to-Image service: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            
            # Extract image data from response
            # Note: The actual response structure may vary, this is a general approach
            image_data = None
            
            # Check different possible response formats
            if isinstance(response, dict):
                # Log available keys for debugging
                logger.debug(f"Response keys: {list(response.keys())}")
                
                # Try common response fields
                if 'result' in response and isinstance(response['result'], bytes):
                    logger.info("Found image data in 'result' field (bytes)")
                    image_data = response['result']
                elif 'image' in response and isinstance(response['image'], bytes):
                    logger.info("Found image data in 'image' field (bytes)")
                    image_data = response['image']
                elif 'result' in response and isinstance(response['result'], str):
                    # Might be base64 encoded
                    logger.info("Found potential base64 image data in 'result' field (string)")
                    try:
                        image_data = self.resource_handler.decode_binary(response['result'])
                        logger.info("Successfully decoded base64 image data")
                    except Exception as e:
                        logger.error(f"Error decoding base64 image: {str(e)}")
            
            if not image_data:
                logger.error("Could not extract image data from response")
                if isinstance(response, dict):
                    for key, value in response.items():
                        logger.debug(f"Response['{key}']: {type(value)}")
                        if isinstance(value, str) and len(value) > 100:
                            logger.debug(f"    Truncated value: {value[:100]}...")
                        else:
                            logger.debug(f"    Value: {value}")
                return None, None, {"error": "No image data in response"}
                
            # Log image data type and size
            logger.info(f"Image data type: {type(image_data)}, size: {len(image_data)} bytes")
                
            # Save the image
            image_path = self.resource_handler.save_image(image_data)
            logger.info(f"Image saved to: {image_path}")
            
            # Prepare metadata
            metadata = {
                "prompt": prompt,
                "success": True,
                "response_keys": list(response.keys()) if isinstance(response, dict) else []
            }
            
            logger.info(f"Image generation successful")
            return image_data, image_path, metadata
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None, None, {"error": str(e)}
            
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the Text-to-Image app.
        
        Returns:
            Dict containing the input schema
        """
        try:
            schema = self.stub.schema(self.APP_ID, 'input')
            return schema
        except Exception as e:
            logger.error(f"Error getting Text-to-Image schema: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return {} 