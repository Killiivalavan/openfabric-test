import logging
import os
from typing import Dict, Any, Optional, Tuple

from core.llm.ollama_client import OllamaClient
from core.memory.memory_manager import MemoryManager
from core.services.mock_text_to_image import MockTextToImageService
from core.services.mock_image_to_3d import MockImageTo3DService
from core.stub import Stub
from core.utils.resource_handler import ResourceHandler


class MockCreativePipeline:
    """
    Mock implementation of the CreativePipeline that uses mock services for image and 3D model generation.
    
    This class is a drop-in replacement for CreativePipeline when Openfabric services are unavailable.
    It maintains the same interface but uses local mock implementations.
    """
    
    def __init__(self, 
                 stub: Optional[Stub] = None,
                 ollama_host: str = None,
                 ollama_model: str = "deepseek-r1:latest"):
        """
        Initialize the mock pipeline with all required components.
        
        Args:
            stub: The Openfabric SDK Stub instance (can be None for mock pipeline)
            ollama_host: Host address for Ollama
            ollama_model: Model to use for LLM
        """
        # Determine appropriate Ollama host
        if ollama_host is None:
            # Check if running in Docker
            if os.path.exists('/.dockerenv'):
                # Use host.docker.internal to access host machine
                ollama_host = "http://host.docker.internal:11434"
            else:
                # Default for local execution
                ollama_host = "http://localhost:11434"
        
        # Initialize components
        self.stub = stub
        self.llm = OllamaClient(host=ollama_host, model=ollama_model)
        self.resource_handler = ResourceHandler()
        self.memory = MemoryManager()
        
        # Initialize mock services
        self.text_to_image = MockTextToImageService(stub, self.resource_handler)
        self.image_to_3d = MockImageTo3DService(stub, self.resource_handler)
        
        logging.info("Mock creative pipeline initialized")
        logging.warning("Using MOCK implementations - Openfabric services unavailable")
        
    def process(self, user_prompt: str, reference_query: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user prompt through the entire pipeline using mock services.
        
        Args:
            user_prompt: The original user prompt
            reference_query: Optional query to find related past creations
            
        Returns:
            Dictionary containing the results and output paths
        """
        logging.info(f"Processing user prompt: '{user_prompt}' using MOCK pipeline")
        result = {
            "user_prompt": user_prompt,
            "success": False,
            "enhanced_prompt": None,
            "image_path": None,
            "model_path": None,
            "error": None,
            "mock": True
        }
        
        try:
            # Step 1: Get memory context if needed
            memory_context = self.memory.get_memory_context(reference_query) if reference_query else None
            
            # Step 2: Enhance prompt with LLM
            creative_response = self.llm.generate_creative_prompt(user_prompt, memory_context)
            enhanced_prompt = creative_response.get("enhanced_prompt", user_prompt)
            style_tags = creative_response.get("style_tags", [])
            mood = creative_response.get("mood", "unknown")
            
            logging.info(f"Enhanced prompt: '{enhanced_prompt}'")
            result["enhanced_prompt"] = enhanced_prompt
            
            # Step 3: Generate image from enhanced prompt using mock service
            image_data, image_path, image_metadata = self.text_to_image.generate_image(enhanced_prompt)
            
            if not image_data or not image_path:
                result["error"] = "Failed to generate image"
                return result
                
            result["image_path"] = image_path
            logging.info(f"Mock image generated at: {image_path}")
            
            # Step 4: Generate 3D model from image using mock service
            model_data, model_path, model_metadata = self.image_to_3d.generate_3d_model(image_data)
            
            if not model_data or not model_path:
                result["error"] = "Failed to generate 3D model"
                # We'll still return partial success since we got the image
                result["success"] = True
                return result
                
            result["model_path"] = model_path
            logging.info(f"Mock 3D model generated at: {model_path}")
            
            # Step 5: Store in memory
            metadata = {
                "style_tags": style_tags,
                "mood": mood,
                "image_metadata": image_metadata,
                "model_metadata": model_metadata,
                "mock": True
            }
            
            creation_id = self.memory.store_creation(
                user_prompt=user_prompt,
                enhanced_prompt=enhanced_prompt,
                image_path=image_path,
                model_path=model_path,
                metadata=metadata,
                tags=style_tags
            )
            
            result["creation_id"] = creation_id
            result["success"] = True
            
            return result
            
        except Exception as e:
            logging.error(f"Error in mock pipeline processing: {str(e)}")
            import traceback
            logging.debug(traceback.format_exc())
            result["error"] = str(e)
            return result 