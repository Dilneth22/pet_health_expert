import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key loaded: {api_key[:10]}..." if api_key else "No API key found")

genai.configure(api_key=api_key)

try:
    # List all available models
    print("\nAvailable models:")
    for model in genai.list_models():
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Supports: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")

# Test a simple generation
try:
    print("\nTesting model access...")
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello")
    print("✓ Model works!")
except Exception as e:
    print(f"✗ Model test failed: {e}")