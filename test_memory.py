import os
import sys

# Add the app directory to the Python path to allow importing
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.core.memory.memory_manager import MemoryManager

def test_memory_system():
    """Test the memory system functionality"""
    print("=== Testing Memory System ===\n")
    
    # Make sure datastore directory exists
    os.makedirs("datastore", exist_ok=True)
    
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
        
    print("\n=== Memory System Tests Complete ===")
    return True
    
if __name__ == "__main__":
    test_memory_system() 