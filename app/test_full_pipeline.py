import logging
import sys
import os
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add parent directory to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our components
from core.mock_pipeline import MockCreativePipeline
from core.memory.memory_manager import MemoryManager

def test_full_pipeline():
    """
    Test the full creative pipeline using mock services.
    This demonstrates the entire flow from prompt to 3D model with memory.
    """
    # Set up
    logging.info("Setting up test environment...")
    
    # Use a test database for memory
    test_db_path = "datastore/test_full_pipeline.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Initialize the pipeline
    logging.info("Initializing mock creative pipeline...")
    pipeline = MockCreativePipeline()
    
    # Define test prompts
    test_prompts = [
        "A majestic dragon perched on a mountain at sunset",
        "A futuristic city with flying cars and neon lights",
        "An underwater kingdom with mermaids and coral reefs"
    ]
    
    # Process each prompt
    results = []
    for i, prompt in enumerate(test_prompts):
        logging.info(f"\n{'='*20} Processing Prompt {i+1}/{len(test_prompts)} {'='*20}")
        logging.info(f"Prompt: '{prompt}'")
        
        # Process the prompt
        result = pipeline.process(prompt)
        results.append(result)
        
        if result["success"]:
            logging.info(f"✅ Successfully processed prompt")
            logging.info(f"Enhanced prompt: '{result['enhanced_prompt']}'")
            logging.info(f"Image path: {result['image_path']}")
            
            if result["model_path"]:
                logging.info(f"3D model path: {result['model_path']}")
                
                # Verify the files exist
                assert os.path.exists(result["image_path"]), f"Image file does not exist: {result['image_path']}"
                assert os.path.exists(result["model_path"]), f"Model file does not exist: {result['model_path']}"
                
                # Read and display mock image content
                try:
                    with open(result["image_path"], "rb") as f:
                        content = f.read().decode('utf-8')
                        logging.info(f"Image content (mock): {content[:100]}...")
                except:
                    logging.warning("Could not read mock image content")
                
                # Read and display mock model content
                try:
                    with open(result["model_path"], "rb") as f:
                        content = f.read().decode('utf-8')
                        logging.info(f"Model content (mock): {content[:100]}...")
                except:
                    logging.warning("Could not read mock model content")
            else:
                logging.warning("⚠️ 3D model generation failed")
        else:
            logging.error(f"❌ Failed to process prompt: {result['error']}")
    
    # Test memory context for the next generation
    logging.info("\n" + "="*20 + " Testing Memory Context " + "="*20)
    memory_prompt = "Create something similar to the dragon I made before"
    logging.info(f"Prompt with memory reference: '{memory_prompt}'")
    
    memory_result = pipeline.process(memory_prompt)
    
    if memory_result["success"]:
        logging.info(f"✅ Successfully processed memory-referencing prompt")
        logging.info(f"Enhanced prompt: '{memory_result['enhanced_prompt']}'")
        logging.info(f"Image path: {memory_result['image_path']}")
        logging.info(f"3D model path: {memory_result['model_path']}")
    else:
        logging.error(f"❌ Failed to process memory-referencing prompt: {memory_result['error']}")
    
    # Summary
    logging.info("\n" + "="*20 + " Test Summary " + "="*20)
    logging.info(f"Processed {len(test_prompts) + 1} prompts")
    successful = sum(1 for r in results + [memory_result] if r["success"])
    logging.info(f"Success rate: {successful}/{len(test_prompts) + 1}")
    
    # Create a simple summary file
    summary_dir = Path("datastore/test_results")
    summary_dir.mkdir(exist_ok=True, parents=True)
    summary_file = summary_dir / "pipeline_test_summary.json"
    
    summary_data = {
        "test_time": str(import_time := __import__("datetime").datetime.now()),
        "num_prompts": len(test_prompts) + 1,
        "successful": successful,
        "prompts": test_prompts + [memory_prompt],
        "image_paths": [r.get("image_path") for r in results + [memory_result] if r.get("image_path")],
        "model_paths": [r.get("model_path") for r in results + [memory_result] if r.get("model_path")]
    }
    
    with open(summary_file, "w") as f:
        json.dump(summary_data, f, indent=2)
    
    logging.info(f"Test summary written to {summary_file}")

if __name__ == "__main__":
    logging.info("Starting full pipeline test with mock services")
    test_full_pipeline()
    logging.info("Full pipeline test completed") 