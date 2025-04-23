import base64
import logging
import os
import uuid
from datetime import datetime
from typing import Optional, Tuple

# Configure detailed logging
logger = logging.getLogger('resource_handler')

class ResourceHandler:
    """
    Utility class for handling resource files like images and 3D models.
    
    This class provides methods for:
    - Saving binary data to files
    - Loading files as binary data
    - Encoding/decoding binary data for API transport
    """
    
    def __init__(self, base_dir: str = "datastore"):
        """
        Initialize the resource handler.
        
        Args:
            base_dir: Base directory for storing resources
        """
        self.base_dir = base_dir
        self.image_dir = os.path.join(base_dir, "images")
        self.model_dir = os.path.join(base_dir, "models")
        
        # Ensure directories exist
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.info(f"ResourceHandler initialized with base directory: {self.base_dir}")
        logger.info(f"Image directory: {self.image_dir}")
        logger.info(f"Model directory: {self.model_dir}")
        
    def save_image(self, image_data: bytes, filename: Optional[str] = None) -> str:
        """
        Save image data to a file.
        
        Args:
            image_data: Binary image data
            filename: Optional filename, will be generated if not provided
            
        Returns:
            Path to the saved image file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"image_{timestamp}_{unique_id}.png"
        
        file_path = os.path.join(self.image_dir, filename)
        
        try:
            logger.info(f"Saving image ({len(image_data)} bytes) to {file_path}")
            
            # Check if the directory exists and is writable
            if not os.path.exists(self.image_dir):
                logger.warning(f"Image directory {self.image_dir} does not exist, creating it")
                os.makedirs(self.image_dir, exist_ok=True)
                
            # Verify image data looks valid (contains at least some image header bytes)
            if len(image_data) < 100:
                logger.warning(f"Image data seems unusually small ({len(image_data)} bytes)")
                
            with open(file_path, "wb") as f:
                f.write(image_data)
                
            # Verify the file was created successfully
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"Image saved successfully. File size: {file_size} bytes")
            else:
                logger.error(f"File was not created at {file_path}")
                return ""
                
            return file_path
        except Exception as e:
            logger.error(f"Error saving image: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return ""
            
    def save_model(self, model_data: bytes, filename: Optional[str] = None) -> str:
        """
        Save 3D model data to a file.
        
        Args:
            model_data: Binary model data
            filename: Optional filename, will be generated if not provided
            
        Returns:
            Path to the saved model file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"model_{timestamp}_{unique_id}.glb"  # Using .glb as default 3D format
            
        file_path = os.path.join(self.model_dir, filename)
        
        try:
            logger.info(f"Saving 3D model ({len(model_data)} bytes) to {file_path}")
            
            # Check if the directory exists and is writable
            if not os.path.exists(self.model_dir):
                logger.warning(f"Model directory {self.model_dir} does not exist, creating it")
                os.makedirs(self.model_dir, exist_ok=True)
                
            with open(file_path, "wb") as f:
                f.write(model_data)
                
            # Verify the file was created successfully
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                logger.info(f"3D model saved successfully. File size: {file_size} bytes")
            else:
                logger.error(f"File was not created at {file_path}")
                return ""
                
            return file_path
        except Exception as e:
            logger.error(f"Error saving 3D model: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return ""
            
    def load_file(self, file_path: str) -> Optional[bytes]:
        """
        Load a file as binary data.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Binary file data or None if file not found
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        try:
            logger.info(f"Loading file: {file_path}")
            with open(file_path, "rb") as f:
                data = f.read()
            logger.info(f"File loaded successfully. Size: {len(data)} bytes")
            return data
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return None
            
    @staticmethod
    def encode_binary(data: bytes) -> str:
        """
        Encode binary data as base64 string for API transport.
        
        Args:
            data: Binary data to encode
            
        Returns:
            Base64 encoded string
        """
        logger.debug(f"Encoding {len(data)} bytes to base64")
        encoded = base64.b64encode(data).decode('utf-8')
        logger.debug(f"Encoded data length: {len(encoded)} characters")
        return encoded
        
    @staticmethod
    def decode_binary(encoded_data: str) -> bytes:
        """
        Decode base64 string to binary data.
        
        Args:
            encoded_data: Base64 encoded string
            
        Returns:
            Binary data
        """
        logger.debug(f"Decoding base64 string of length {len(encoded_data)}")
        try:
            decoded = base64.b64decode(encoded_data)
            logger.debug(f"Decoded data length: {len(decoded)} bytes")
            return decoded
        except Exception as e:
            logger.error(f"Error decoding base64 data: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            raise 