import requests
import json
import sys

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✓ Ollama is running and accessible")
            models = response.json().get("models", [])
            if models:
                print(f"Available models: {', '.join([m['name'] for m in models])}")
            return True
        else:
            print(f"✗ Ollama returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Could not connect to Ollama. Is it running at http://localhost:11434?")
        return False

def test_deepseek_model():
    """Test if the DeepSeek model is available and can generate responses"""
    try:
        data = {
            "model": "deepseek-r1:latest",
            "prompt": "Generate a simple hello world program in Python",
            "stream": False
        }
        
        print("Testing DeepSeek model...")
        response = requests.post("http://localhost:11434/api/generate", json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "response" in result:
                print("✓ DeepSeek model is working")
                print("\nSample output:")
                print("-------------")
                print(result["response"])
                return True
            else:
                print("✗ DeepSeek model response format unexpected")
                return False
        else:
            print(f"✗ DeepSeek model request failed with status {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"✗ Error testing DeepSeek model: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Ollama Integration ===\n")
    
    if not test_ollama_connection():
        print("\nPlease make sure Ollama is installed and running.")
        print("Installation instructions: https://ollama.com/download")
        print("Run: 'ollama serve' to start the service")
        sys.exit(1)
    
    print()
    
    if not test_deepseek_model():
        print("\nThe DeepSeek model is not available.")
        print("Run: 'ollama pull deepseek-r1:latest' to download it")
        sys.exit(1)
        
    print("\n=== All tests passed! ===")
    print("The Ollama integration should work with the application.") 