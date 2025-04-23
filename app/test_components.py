import logging
import os
import sys
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Import components
from core.memory.memory_manager import MemoryManager
from core.utils.resource_handler import ResourceHandler
from core.llm.ollama_client import OllamaClient

def test_memory_system():
    """Test the memory system functionality"""
    print("\n=== Testing Memory System ===\n")
    
    # Create memory manager
    memory = MemoryManager(db_path="datastore/test_memory.db")
    
    print("Testing creation storage...\n")
    
    # Test storing creations
    creation_id = memory.store_creation(
        user_prompt="Make a dragon",
        enhanced_prompt="Create a majestic dragon with red scales, breathing fire, against a sunset sky",
        image_path="datastore/images/test_image.png",
        model_path="datastore/models/test_model.glb",
        metadata={"style_tags": ["fantasy", "dragon"], "mood": "epic"},
        tags=["dragon", "fantasy", "epic"]
    )
    
    print(f"✓ Creation stored with ID: {creation_id}")
    
    # Test retrieving a creation
    creation = memory.get_creation_by_id(creation_id)
    if creation:
        print(f"✓ Retrieved creation by ID")
        print(f"  - Original prompt: {creation['user_prompt']}")
        print(f"  - Enhanced prompt: {creation['enhanced_prompt']}")
    else:
        print("✗ Failed to retrieve creation by ID")
        return False
        
    # Test storing another creation
    memory.store_creation(
        user_prompt="Create a robot",
        enhanced_prompt="Design a sleek, futuristic robot with glowing blue eyes and metallic silver body",
        image_path="datastore/images/test_robot.png",
        model_path="datastore/models/test_robot.glb",
        metadata={"style_tags": ["sci-fi", "robot"], "mood": "futuristic"},
        tags=["robot", "sci-fi", "futuristic"]
    )
    
    # Test searching
    print("\nTesting search functionality...\n")
    
    dragon_results = memory.search_creations("dragon")
    if dragon_results and len(dragon_results) > 0:
        print(f"✓ Found {len(dragon_results)} results for 'dragon'")
    else:
        print("✗ Search for 'dragon' failed")
        
    robot_results = memory.search_creations("robot")
    if robot_results and len(robot_results) > 0:
        print(f"✓ Found {len(robot_results)} results for 'robot'")
    else:
        print("✗ Search for 'robot' failed")
        
    # Test memory context
    print("\nTesting memory context generation...\n")
    
    context = memory.get_memory_context()
    if context:
        print(f"✓ Generated memory context:")
        print(f"{context}")
    else:
        print("✗ Failed to generate memory context")
        
    # Test specific memory context
    dragon_context = memory.get_memory_context("dragon")
    if dragon_context and "dragon" in dragon_context.lower():
        print(f"✓ Generated specific memory context for 'dragon'")
    else:
        print("✗ Failed to generate specific memory context for 'dragon'")
        
    print("\n=== Memory System Test Complete ===")
    return True

def test_resource_handler():
    """Test the resource handler functionality"""
    print("\n=== Testing Resource Handler ===\n")
    
    # Create resource handler
    resource_handler = ResourceHandler()
    
    # Create test data
    test_data = b"This is test binary data"
    encoded_data = resource_handler.encode_binary(test_data)
    
    print(f"✓ Encoded test data: {encoded_data[:20]}...")
    
    # Test decode
    decoded_data = resource_handler.decode_binary(encoded_data)
    if decoded_data == test_data:
        print(f"✓ Decoded data matches original")
    else:
        print(f"✗ Decoded data does not match original")
        return False
    
    # Test save image
    image_path = resource_handler.save_image(test_data, "test_image.png")
    if os.path.exists(image_path):
        print(f"✓ Saved test image to {image_path}")
    else:
        print(f"✗ Failed to save test image")
        return False
        
    # Test save model
    model_path = resource_handler.save_model(test_data, "test_model.glb")
    if os.path.exists(model_path):
        print(f"✓ Saved test model to {model_path}")
    else:
        print(f"✗ Failed to save test model")
        return False
        
    # Test load file
    loaded_data = resource_handler.load_file(image_path)
    if loaded_data == test_data:
        print(f"✓ Loaded data matches original")
    else:
        print(f"✗ Loaded data does not match original")
        return False
        
    print("\n=== Resource Handler Test Complete ===")
    return True
    
def test_ollama_client():
    """Test the Ollama client functionality"""
    print("\n=== Testing Ollama Client ===\n")
    
    try:
        # Create Ollama client
        ollama = OllamaClient()
        
        print("Testing prompt enhancement...\n")
        test_prompt = "Make a picture of a cat"
        
        # Test enhance_prompt
        enhanced = ollama.enhance_prompt(test_prompt)
        if enhanced and enhanced != test_prompt:
            print(f"✓ Enhanced prompt: \"{enhanced}\"")
        else:
            print(f"✗ Failed to enhance prompt")
            return False
            
        # Test generate_creative_prompt
        print("\nTesting creative prompt generation...\n")
        
        creative_response = ollama.generate_creative_prompt(test_prompt)
        if creative_response and "enhanced_prompt" in creative_response:
            print(f"✓ Generated creative prompt response")
            print(f"  - Enhanced prompt: \"{creative_response['enhanced_prompt']}\"")
            if "style_tags" in creative_response:
                print(f"  - Style tags: {creative_response['style_tags']}")
            if "mood" in creative_response:
                print(f"  - Mood: {creative_response['mood']}")
        else:
            print(f"✗ Failed to generate creative prompt")
            return False
            
        print("\n=== Ollama Client Test Complete ===")
        return True
        
    except Exception as e:
        print(f"✗ Error testing Ollama client: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Components ===")
    
    # Make sure datastore directories exist
    os.makedirs("datastore/images", exist_ok=True)
    os.makedirs("datastore/models", exist_ok=True)
    
    # Run tests
    memory_result = test_memory_system()
    resource_result = test_resource_handler()
    ollama_result = test_ollama_client()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Memory System: {'✓ PASS' if memory_result else '✗ FAIL'}")
    print(f"Resource Handler: {'✓ PASS' if resource_result else '✗ FAIL'}")
    print(f"Ollama Client: {'✓ PASS' if ollama_result else '✗ FAIL'}")
    
    if memory_result and resource_result and ollama_result:
        print("\nAll components are working correctly!")
        sys.exit(0)
    else:
        print("\nSome components failed. Please check the logs.")
        sys.exit(1) 