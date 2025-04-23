import json
import requests
import sys
import time

def test_app_endpoint():
    """Test the main application endpoint with a simple prompt"""
    print("=== Testing Application API ===\n")
    
    base_url = "http://localhost:8888"
    endpoint = f"{base_url}/execution"
    
    # Test data
    data = {
        "prompt": "Create a small glowing dragon on a cliff at sunset"
    }
    
    try:
        print(f"Sending prompt: '{data['prompt']}'")
        response = requests.post(endpoint, json=data)
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {response.headers}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print("\n✓ API call succeeded")
                print(f"Response: {json.dumps(result, indent=2)}")
                return True
            except json.JSONDecodeError as e:
                print(f"\n✗ Could not decode JSON response: {e}")
                print(f"Raw response text: {response.text[:500]}...")
                return False
        else:
            print(f"\n✗ API call failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("\n✗ Could not connect to the application. Is it running on http://localhost:8888?")
        print("  Start the application using 'docker run -p 8888:8888 creative-ai-pipeline' or 'sh start.sh'")
        return False
    except Exception as e:
        print(f"\n✗ Error testing application: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_swagger_ui():
    """Test if the Swagger UI is accessible"""
    print("\n=== Testing Swagger UI ===\n")
    
    url = "http://localhost:8888/swagger-ui/"
    
    try:
        print(f"Checking Swagger UI at: {url}")
        response = requests.get(url)
        
        if response.status_code == 200:
            print("✓ Swagger UI is accessible")
            return True
        else:
            print(f"✗ Swagger UI returned status code {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error accessing Swagger UI: {str(e)}")
        return False

if __name__ == "__main__":
    print("This test assumes the application is already running on http://localhost:8888")
    print("Press Ctrl+C to cancel or Enter to continue...")
    try:
        input()
    except KeyboardInterrupt:
        sys.exit(0)
    
    # First test if Swagger UI is accessible
    swagger_result = test_swagger_ui()
    
    # Then test the API endpoint
    api_result = test_app_endpoint()
    
    if swagger_result and api_result:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1) 