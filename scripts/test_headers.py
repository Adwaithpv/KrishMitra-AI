#!/usr/bin/env python3
"""
Test session headers handling
"""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_headers():
    """Test if headers are being passed correctly"""
    
    print("🔍 TESTING SESSION HEADERS")
    print("=" * 40)
    
    # Test 1: No session header
    print("\n1. No session header:")
    response1 = requests.get(f"{BASE_URL}/query", params={
        'text': 'test query',
        'location': 'Karnataka'
    })
    
    if response1.status_code == 200:
        data1 = response1.json()
        session_id1 = data1.get('session_id')
        print(f"   Session ID: {session_id1}")
    
    # Test 2: With session header
    print("\n2. With session header:")
    test_session = "test_session_123"
    headers = {"X-Session-ID": test_session}
    
    response2 = requests.get(f"{BASE_URL}/query", params={
        'text': 'My farm is 5 acres and I spend 30000 on fertilizers',
        'location': 'Karnataka'
    }, headers=headers)
    
    if response2.status_code == 200:
        data2 = response2.json()
        session_id2 = data2.get('session_id')
        agents2 = data2.get('agents_consulted', [])
        context2 = data2.get('conversation_context')
        
        print(f"   Session ID: {session_id2}")
        print(f"   Agents: {agents2}")
        print(f"   Context: {'Present' if context2 else 'Missing'}")
        
        if session_id2 == test_session:
            print("   ✅ Session header correctly processed")
        else:
            print("   ❌ Session header not processed correctly")

def main():
    """Main test function"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    test_headers()

if __name__ == "__main__":
    main()
