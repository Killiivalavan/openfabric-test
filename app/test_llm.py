import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from core.llm.ollama_client import OllamaClient

def test_prompt_enhancement():
    """Test the basic prompt enhancement functionality"""
    client = OllamaClient()
    
    test_prompts = [
        "A dragon on a mountain",
        "Space station orbiting Earth",
        "Underwater city with mermaids"
    ]
    
    logging.info("Testing basic prompt enhancement:")
    for prompt in test_prompts:
        logging.info(f"\nOriginal prompt: '{prompt}'")
        enhanced = client.enhance_prompt(prompt)
        logging.info(f"Enhanced prompt: '{enhanced}'")
        logging.info("-" * 50)

def test_creative_prompt_with_memory():
    """Test the creative prompt generation with memory context"""
    client = OllamaClient()
    
    user_prompt = "A futuristic car racing through a city"
    memory_context = "Previous creation: A cyberpunk cityscape with neon lights and tall skyscrapers"
    
    logging.info("\nTesting creative prompt with memory context:")
    logging.info(f"User prompt: '{user_prompt}'")
    logging.info(f"Memory context: '{memory_context}'")
    
    result = client.generate_creative_prompt(user_prompt, memory_context)
    
    logging.info(f"Enhanced prompt: '{result['enhanced_prompt']}'")
    logging.info(f"Detected style tags: {result['style_tags']}")
    logging.info(f"Detected mood: {result['mood']}")

if __name__ == "__main__":
    logging.info("Starting LLM functionality tests")
    
    test_prompt_enhancement()
    test_creative_prompt_with_memory()
    
    logging.info("LLM functionality tests completed") 