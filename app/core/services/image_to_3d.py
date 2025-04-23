import logging
from typing import Dict, Any, Optional, Tuple

from core.stub import Stub
from core.utils.resource_handler import ResourceHandler


class ImageTo3DService:
    """
    Service for generating 3D models from images using the Openfabric Image-to-3D app.
    """
    
    # Openfabric Image-to-3D app ID
    APP_ID = "69543f29-4d41-4afc-7f29-3d51591f11eb"
    
    def __init__(self, stub: Stub, resource_handler: ResourceHandler):
        """
        Initialize the Image-to-3D service.
        
        Args:
            stub: The Openfabric SDK Stub instance
            resource_handler: The ResourceHandler for saving 3D models
        """
        self.stub = stub
        self.resource_handler = resource_handler
        
    def generate_3d_model(self, image_data: bytes, user_id: str = 'super-user') -> Tuple[Optional[bytes], Optional[str], Dict[str, Any]]:
        """
        Generate a 3D model from an image.
        
        Args:
            image_data: The image data to generate a 3D model from
            user_id: User ID for the Openfabric API call
            
        Returns:
            Tuple containing:
            - 3D model data (bytes or None if failed)
            - Path to saved model (or None if failed)
            - Metadata about the generation
        """
        try:
            logging.info("Generating 3D model from image")
            
            # Convert binary image to base64 for API transport if needed
            encoded_image = self.resource_handler.encode_binary(image_data)
            
            # Prepare request data based on the app's schema
            # Note: The actual schema may vary, this is a general approach
            request_data = {"image": encoded_image}
            
            # Call the Image-to-3D service
            response = self.stub.call(self.APP_ID, request_data, user_id)
            
            if not response:
                logging.error("Empty response from Image-to-3D service")
                return None, None, {"error": "Empty response"}
                
            logging.info(f"Received response from Image-to-3D service: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            
            # Extract 3D model data from response
            # Note: The actual response structure may vary, this is a general approach
            model_data = None
            
            # Check different possible response formats
            if isinstance(response, dict):
                # Try common response fields
                if 'result' in response and isinstance(response['result'], bytes):
                    model_data = response['result']
                elif 'model' in response and isinstance(response['model'], bytes):
                    model_data = response['model']
                elif 'result' in response and isinstance(response['result'], str):
                    # Might be base64 encoded
                    try:
                        model_data = self.resource_handler.decode_binary(response['result'])
                    except Exception as e:
                        logging.error(f"Error decoding base64 model: {str(e)}")
            
            if not model_data:
                logging.error("Could not extract 3D model data from response")
                return None, None, {"error": "No model data in response"}
                
            # Save the 3D model
            model_path = self.resource_handler.save_model(model_data)
            
            # Prepare metadata
            metadata = {
                "success": True,
                "response_keys": list(response.keys()) if isinstance(response, dict) else []
            }
            
            logging.info(f"3D model generated and saved to {model_path}")
            return model_data, model_path, metadata
            
        except Exception as e:
            logging.error(f"Error generating 3D model: {str(e)}")
            return None, None, {"error": str(e)}
            
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the Image-to-3D app.
        
        Returns:
            Dict containing the input schema
        """
        try:
            return self.stub.schema(self.APP_ID, 'input')
        except Exception as e:
            logging.error(f"Error getting Image-to-3D schema: {str(e)}")
            return {} 