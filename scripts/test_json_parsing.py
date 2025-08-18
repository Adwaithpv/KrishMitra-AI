#!/usr/bin/env python3
"""
Test script to verify JSON parsing in LLM routing
"""

import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_json_parsing():
    """Test a simple query to see if JSON parsing works"""
    
    test_query = "what crop would be suitable for my location"
    
    print("🧪 Testing JSON Parsing Fix")
    print("=" * 50)
    print(f"Query: '{test_query}'")
    
    try:
        params = {
            'text': test_query,
            'location': '12.9647799,80.2355988',  # Same coordinates from logs
            'crop': 'general'
        }
        
        print("\n🔄 Sending request...")
        response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful!")
            
            # Check for LLM routing metadata
            supervisor_response = data.get('response', {})
            agents_consulted = data.get('agents_consulted', [])
            
            print(f"🤖 Agents consulted: {agents_consulted}")
            
            if 'llm_routing' in supervisor_response:
                llm_routing = supervisor_response['llm_routing']
                print("🎉 LLM routing metadata found!")
                print(f"   🧠 Reasoning: {llm_routing.get('reasoning', 'N/A')}")
                print(f"   📊 Confidence: {llm_routing.get('confidence', 'N/A')}")
                print(f"   📝 Query Type: {llm_routing.get('query_type', 'N/A')}")
                print("\n✅ LLM routing is working correctly!")
            else:
                print("⚠️ No LLM routing metadata - likely fell back to keyword analysis")
                print("   Check server logs for JSON parsing details")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main test function"""
    print("🚀 JSON Parsing Test")
    print("=" * 50)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy. Testing JSON parsing...\n")
    test_json_parsing()

if __name__ == "__main__":
    main()

