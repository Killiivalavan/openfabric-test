import logging
import os
import sys
from unittest.mock import MagicMock, patch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import components
from core.pipeline import CreativePipeline
from core.llm.ollama_client import OllamaClient
from core.memory.memory_manager import MemoryManager
from core.utils.resource_handler import ResourceHandler

def mock_stub():
    """Create a mock Stub for testing"""
    stub = MagicMock()
    
    # Mock call method to return a simple response
    def mock_call(app_id, data, user_id):
        if app_id == "f0997a01-d6d3-a5fe-53d8-561300318557":  # Text-to-Image
            return {"result": b"fake_image_data"}
        elif app_id == "69543f29-4d41-4afc-7f29-3d51591f11eb":  # Image-to-3D
            return {"result": b"fake_model_data"}
        return None
        
    stub.call = mock_call
    return stub

def test_pipeline():
    """Test the entire pipeline with mocked Openfabric services"""
    print("\n=== Testing Creative Pipeline ===\n")
    
    # Create directories
    os.makedirs("datastore/images", exist_ok=True)
    os.makedirs("datastore/models", exist_ok=True)
    
    # Mock the Stub
    stub = mock_stub()
    
    # Create the pipeline
    pipeline = CreativePipeline(stub)
    
    # Test the pipeline with a simple prompt
    print("Processing prompt: 'Create a dragon on a mountain'\n")
    result = pipeline.process("Create a dragon on a mountain")
    
    if result["success"]:
        print("✓ Pipeline execution succeeded")
        print(f"  - Enhanced prompt: \"{result['enhanced_prompt']}\"")
        print(f"  - Image path: {result['image_path']}")
        print(f"  - Model path: {result['model_path']}")
        if "creation_id" in result:
            print(f"  - Creation ID: {result['creation_id']}")
    else:
        print("✗ Pipeline execution failed")
        print(f"  - Error: {result['error']}")
        return False
    
    # Test with a reference query
    print("\nProcessing prompt with reference: 'Create another dragon like the one before'\n")
    result = pipeline.process("Create another dragon like the one before", "dragon")
    
    if result["success"]:
        print("✓ Pipeline execution with reference succeeded")
        print(f"  - Enhanced prompt: \"{result['enhanced_prompt']}\"")
    else:
        print("✗ Pipeline execution with reference failed")
        print(f"  - Error: {result['error']}")
        return False
    
    print("\n=== Pipeline Test Complete ===")
    return True

if __name__ == "__main__":
    print("=== Testing Pipeline ===")
    success = test_pipeline()
    
    if success:
        print("\n✓ Pipeline test passed!")
        sys.exit(0)
    else:
        print("\n✗ Pipeline test failed!")
        sys.exit(1) 