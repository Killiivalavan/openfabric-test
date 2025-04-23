import logging
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    """
    Test the mock pipeline implementation.
    """
    # Import here to avoid path issues
    try:
        # Try direct import first (for Docker)
        from app.core.mock_pipeline import MockCreativePipeline
    except ImportError:
        # Add parent directory to path for local development
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from core.mock_pipeline import MockCreativePipeline
    
    # Create a test prompt
    test_prompt = "Generate a futuristic cityscape with flying cars"
    
    # Initialize the mock pipeline
    logging.info("Initializing mock pipeline...")
    pipeline = MockCreativePipeline()
    
    # Process the prompt
    logging.info(f"Processing prompt: '{test_prompt}'")
    result = pipeline.process(test_prompt)
    
    # Output the results
    if result["success"]:
        logging.info("Processing succeeded!")
        logging.info(f"Original prompt: '{test_prompt}'")
        logging.info(f"Enhanced prompt: '{result['enhanced_prompt']}'")
        
        if result["image_path"]:
            logging.info(f"Image generated at: {result['image_path']}")
        else:
            logging.error("Image generation failed")
            
        if result["model_path"]:
            logging.info(f"3D model generated at: {result['model_path']}")
        else:
            logging.error("3D model generation failed")
    else:
        logging.error(f"Processing failed: {result['error']}")


if __name__ == "__main__":
    logging.info("Starting mock pipeline test")
    main()
    logging.info("Test completed") 