import logging
import sys
import os
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from core.memory.memory_manager import MemoryManager

def test_memory_storage_and_retrieval():
    """Test basic memory storage and retrieval functionality"""
    # Use a test database file
    test_db_path = "datastore/test_memory.db"
    
    # Remove the test database if it exists
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        logging.info(f"Removed existing test database: {test_db_path}")
    
    # Create memory manager with test database
    memory = MemoryManager(db_path=test_db_path)
    
    # Test data
    test_creations = [
        {
            "user_prompt": "A cyberpunk cityscape",
            "enhanced_prompt": "A futuristic metropolis bathed in neon lights, with towering skyscrapers and flying vehicles",
            "image_path": "/path/to/cyberpunk_city.png",
            "model_path": "/path/to/cyberpunk_city.obj",
            "metadata": {
                "style_tags": ["cyberpunk", "futuristic", "sci-fi"],
                "mood": "dark"
            },
            "tags": ["city", "cyberpunk", "night"]
        },
        {
            "user_prompt": "A dragon on a mountain",
            "enhanced_prompt": "A majestic dragon perched on a craggy mountain peak, with scales glistening in the sunlight",
            "image_path": "/path/to/dragon.png",
            "model_path": "/path/to/dragon.obj",
            "metadata": {
                "style_tags": ["fantasy", "realistic"],
                "mood": "epic"
            },
            "tags": ["dragon", "mountain", "fantasy"]
        },
        {
            "user_prompt": "A peaceful beach at sunset",
            "enhanced_prompt": "A tranquil beach scene with golden sand, gentle waves, and a vivid sunset painting the sky in orange and pink hues",
            "image_path": "/path/to/beach_sunset.png",
            "model_path": "/path/to/beach_sunset.obj",
            "metadata": {
                "style_tags": ["realistic", "serene"],
                "mood": "peaceful"
            },
            "tags": ["beach", "sunset", "nature"]
        }
    ]
    
    # Store test creations in memory
    logging.info("Storing test creations in memory...")
    creation_ids = []
    for creation in test_creations:
        creation_id = memory.store_creation(
            user_prompt=creation["user_prompt"],
            enhanced_prompt=creation["enhanced_prompt"],
            image_path=creation["image_path"],
            model_path=creation["model_path"],
            metadata=creation["metadata"],
            tags=creation["tags"]
        )
        creation_ids.append(creation_id)
        logging.info(f"Stored creation with ID: {creation_id}")
        
        # Small delay to ensure different timestamps
        time.sleep(0.1)
    
    # Test retrieval by ID
    logging.info("\nTesting retrieval by ID:")
    for creation_id in creation_ids:
        creation = memory.get_creation_by_id(creation_id)
        logging.info(f"Retrieved creation {creation_id}: '{creation['user_prompt']}'")
        assert creation is not None, f"Failed to retrieve creation with ID {creation_id}"
    
    # Test recent creations
    logging.info("\nTesting recent creations:")
    recent = memory.get_recent_creations(limit=2)
    logging.info(f"Retrieved {len(recent)} recent creations")
    for creation in recent:
        logging.info(f"Recent creation: '{creation['user_prompt']}'")
    assert len(recent) == 2, "Expected 2 recent creations"
    
    # Test search functionality
    logging.info("\nTesting search functionality:")
    search_terms = ["dragon", "city", "sunset"]
    for term in search_terms:
        results = memory.search_creations(term)
        logging.info(f"Search for '{term}' returned {len(results)} results")
        for result in results:
            logging.info(f"Found: '{result['user_prompt']}'")
    
    # Test memory context generation
    logging.info("\nTesting memory context generation:")
    context = memory.get_memory_context("dragon")
    logging.info(f"Generated context for 'dragon':\n{context}")
    
    context = memory.get_memory_context()  # Recent creations context
    logging.info(f"Generated context from recent creations:\n{context}")

if __name__ == "__main__":
    logging.info("Starting memory functionality tests")
    test_memory_storage_and_retrieval()
    logging.info("Memory functionality tests completed") 