import requests

def test_ollama_connection():
    """Test if Ollama is running and phi3:mini is available."""
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("❌ Ollama server not running. Start with: ollama serve")
            return False
            
        models = response.json().get("models", [])
        model_names = [m["name"] for m in models]
        
        if "phi3:mini" not in model_names:
            print("❌ phi3:mini model not found. Pull with: ollama pull phi3:mini")
            return False
            
        print("✅ Ollama server running and phi3:mini model available")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

if __name__ == "__main__":
    test_ollama_connection()
