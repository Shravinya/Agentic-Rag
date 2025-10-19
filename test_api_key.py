"""Test script to verify Groq API key is working"""
import os
from dotenv import load_dotenv
from groq import Groq

def test_groq_api():
    """Test Groq API connection"""
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in .env file")
        return False
    
    print(f"✅ API Key loaded: {api_key[:20]}...")
    
    try:
        client = Groq(api_key=api_key)
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'API is working!' if you can read this."}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        print("✅ Groq API is working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        return False

if __name__ == "__main__":
    test_groq_api()
