#!/usr/bin/env python3
"""
Test the successful conversation context implementation
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_conversation_flow():
    """Test the complete conversation flow with session continuity"""
    
    print("🎉 TESTING SUCCESSFUL CONVERSATION CONTEXT")
    print("=" * 60)
    
    session_headers = {}
    
    # Step 1: Initial finance query
    print("\n📋 Step 1: Initial Finance Query")
    query1 = "I need help optimizing my farm finances"
    print(f"Query: '{query1}'")
    
    response1 = make_query(query1, session_headers)
    if response1:
        session_id = response1.get("session_id")
        if session_id:
            session_headers["X-Session-ID"] = session_id
            print(f"✅ Session ID captured: {session_id}")
        
        agents = response1.get("agents_consulted", [])
        if any("finance" in str(agent) for agent in agents):
            print("✅ SUCCESS: Finance agent correctly consulted")
        else:
            print(f"📊 Info: Agents consulted: {agents}")
        
        context = response1.get("conversation_context")
        if context:
            print("✅ SUCCESS: Conversation context present")
            print(f"   Summary: {context.get('conversation_summary', 'N/A')}")
        else:
            print("📊 Info: No conversation context yet")
    
    time.sleep(1)
    
    # Step 2: Provide financial data
    print("\n📋 Step 2: Providing Financial Information")
    query2 = "My farm is 5 acres and I spend 30000 on fertilizers annually"
    print(f"Query: '{query2}'")
    print(f"Using session: {session_headers.get('X-Session-ID', 'None')}")
    
    response2 = make_query(query2, session_headers)
    if response2:
        agents = response2.get("agents_consulted", [])
        if any("finance" in str(agent) for agent in agents):
            print("✅ SUCCESS: Finance agent continued conversation")
        else:
            print(f"📊 Agent routing: {agents}")
        
        context = response2.get("conversation_context")
        if context:
            user_profile = context.get("user_profile", {})
            if "land_size" in user_profile and "cost_amount" in user_profile:
                print("✅ SUCCESS: User profile data accumulated")
                print(f"   Profile: {user_profile}")
            else:
                print(f"📊 Profile building: {user_profile}")
        
        answer = response2.get("answer", "")
        print(f"📝 Response preview: {answer[:100]}...")
    
    time.sleep(1)
    
    # Step 3: Continue with more financial info
    print("\n📋 Step 3: More Financial Information")
    query3 = "I also spend 25000 on water and produce 120 quintals per year"
    print(f"Query: '{query3}'")
    
    response3 = make_query(query3, session_headers)
    if response3:
        agents = response3.get("agents_consulted", [])
        context = response3.get("conversation_context")
        
        if context:
            active_agent = context.get("active_agent")
            expecting_response = context.get("expecting_response")
            user_profile = context.get("user_profile", {})
            
            print(f"📊 Conversation state:")
            print(f"   Active agent: {active_agent}")
            print(f"   Expecting response: {expecting_response}")
            print(f"   Profile data points: {len(user_profile)}")
            
            if len(user_profile) >= 3:  # land_size, cost_amount (fertilizer + water), production
                print("✅ SUCCESS: Rich user profile built")
            else:
                print("📊 Profile still building...")
    
    print("\n🎉 CONVERSATION CONTEXT TEST COMPLETED!")

def test_supervisor_endpoint():
    """Test supervisor endpoint for comparison"""
    
    print("\n🤖 TESTING SUPERVISOR ENDPOINT DIRECTLY")
    print("=" * 50)
    
    query = "My farm is 5 acres and I spend 30000 on fertilizers annually"
    
    response = requests.get(f"{BASE_URL}/supervisor", params={
        'text': query,
        'location': 'Karnataka'
    })
    
    if response.status_code == 200:
        data = response.json()
        supervisor_response = data.get('response', {})
        
        print(f"✅ Status: 200")
        print(f"🤖 Agent: {supervisor_response.get('agent_used', 'Unknown')}")
        print(f"👥 Agents: {supervisor_response.get('agents_consulted', [])}")
        print(f"🔑 Session: {supervisor_response.get('session_id', 'None')}")
        
        context = supervisor_response.get('conversation_context')
        if context:
            print(f"📊 Context: ✅ Present")
            print(f"   Summary: {context.get('conversation_summary', 'N/A')}")
        else:
            print(f"📊 Context: ❌ Missing")
    else:
        print(f"❌ Status: {response.status_code}")

def make_query(query_text, headers=None):
    """Make a query to the main endpoint"""
    try:
        params = {
            'text': query_text,
            'location': 'Karnataka',
            'crop': 'wheat'
        }
        
        response = requests.get(f"{BASE_URL}/query", params=params, headers=headers or {}, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🚀 CONVERSATION CONTEXT SUCCESS TEST")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy. Testing conversation context...\n")
    
    # Test supervisor endpoint first for baseline
    test_supervisor_endpoint()
    
    # Test main conversation flow
    test_conversation_flow()
    
    print(f"\n🏁 All tests completed!")

if __name__ == "__main__":
    main()
