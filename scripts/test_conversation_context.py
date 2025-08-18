#!/usr/bin/env python3
"""
Test script for conversation context and intelligent routing
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_conversation_flow():
    """Test intelligent conversation flow with context awareness"""
    
    print("🧪 Testing Conversation Context System")
    print("=" * 70)
    
    session_id = None
    
    # Step 1: Initial finance query (should create session and ask for info)
    print("\n📋 Step 1: Initial Finance Query")
    print("Query: 'I need help optimizing my farm finances'")
    
    response1 = make_query("I need help optimizing my farm finances")
    if response1:
        session_id = response1.get("session_id")
        conversation_context = response1.get("conversation_context")
        
        print("✅ Initial query successful")
        print(f"🔑 Session ID: {session_id}")
        
        if conversation_context:
            print(f"📊 Context Summary: {conversation_context.get('conversation_summary', 'N/A')}")
            print(f"🤖 Active Agent: {conversation_context.get('active_agent', 'None')}")
            print(f"⏳ Expecting Response: {conversation_context.get('expecting_response', False)}")
        
        # Check if this generated a form or follow-up questions
        answer = response1.get("answer", "")
        if "form" in answer.lower() or "information" in answer.lower():
            print("📝 Agent is asking for information - conversation started")
        
    else:
        print("❌ Initial query failed")
        return
    
    time.sleep(1)
    
    # Step 2: Provide financial information (should continue with same agent)
    print("\n📋 Step 2: Providing Financial Information")
    print("Query: 'My farm is 5 acres and I spend 30000 on fertilizers annually'")
    
    response2 = make_query("My farm is 5 acres and I spend 30000 on fertilizers annually")
    if response2:
        print("✅ Information update successful")
        
        # Check conversation context
        conversation_context = response2.get("conversation_context")
        if conversation_context:
            print(f"📊 Context Summary: {conversation_context.get('conversation_summary', 'N/A')}")
            print(f"🤖 Active Agent: {conversation_context.get('active_agent', 'None')}")
            
            # Check if supervisor recognized this as continuation
            agents_consulted = response2.get("agents_consulted", [])
            if any("finance" in str(agent) for agent in agents_consulted):
                print("🎯 SUCCESS: Finance agent continued conversation (no re-routing)")
            else:
                print(f"⚠️ Unexpected routing: {agents_consulted}")
        
        # Check if conversation progressed
        answer = response2.get("answer", "")
        if "information" in answer.lower() and len(answer) > 100:
            print("💬 Conversation progressing - agent building profile")
    
    time.sleep(1)
    
    # Step 3: Ask a different type of question (should route to different agent)
    print("\n📋 Step 3: Topic Switch - Weather Query")
    print("Query: 'What's the weather forecast for farming this week?'")
    
    response3 = make_query("What's the weather forecast for farming this week?")
    if response3:
        print("✅ Topic switch successful")
        
        agents_consulted = response3.get("agents_consulted", [])
        if any("weather" in str(agent) for agent in agents_consulted):
            print("🌤️ SUCCESS: Correctly routed to weather agent (new topic)")
        else:
            print(f"⚠️ Unexpected routing for weather query: {agents_consulted}")
        
        # Check conversation context reset
        conversation_context = response3.get("conversation_context")
        if conversation_context:
            print(f"📊 New Context: {conversation_context.get('conversation_summary', 'N/A')}")
    
    time.sleep(1)
    
    # Step 4: Continue with finance info (should return to finance agent)
    print("\n📋 Step 4: Return to Finance Context")
    print("Query: 'I also spend 25000 on water and produce 120 quintals per year'")
    
    response4 = make_query("I also spend 25000 on water and produce 120 quintals per year")
    if response4:
        print("✅ Finance context return successful")
        
        agents_consulted = response4.get("agents_consulted", [])
        if any("finance" in str(agent) for agent in agents_consulted):
            print("💰 SUCCESS: Returned to finance agent with remembered context")
            
            # Check if information was accumulated
            conversation_context = response4.get("conversation_context")
            if conversation_context:
                user_profile = conversation_context.get("user_profile", {})
                if user_profile:
                    print(f"📋 Accumulated Profile: {user_profile}")
        else:
            print(f"⚠️ Failed to return to finance context: {agents_consulted}")
    
    print("\n✅ Conversation Context Flow Test Complete!")

def test_context_persistence():
    """Test that conversation context persists across queries"""
    print("\n🔄 Testing Context Persistence")
    print("=" * 50)
    
    # Finance query 1
    print("Query 1: 'I need financial advice for my 3-acre farm'")
    response1 = make_query("I need financial advice for my 3-acre farm")
    
    if response1:
        session_id = response1.get("session_id")
        print(f"🔑 Session created: {session_id}")
    
    time.sleep(1)
    
    # Finance query 2 - should remember previous context
    print("\nQuery 2: 'I also spend 20000 on fertilizers'")
    response2 = make_query("I also spend 20000 on fertilizers")
    
    if response2:
        conversation_context = response2.get("conversation_context")
        if conversation_context:
            print("✅ Context persistence working:")
            print(f"   Summary: {conversation_context.get('conversation_summary', 'N/A')}")
            
            user_profile = conversation_context.get("user_profile", {})
            if user_profile:
                print(f"   Profile: {user_profile}")

def test_intelligent_routing_decision():
    """Test the intelligent routing decision-making"""
    print("\n🤖 Testing Intelligent Routing Decisions")
    print("=" * 50)
    
    test_cases = [
        {
            "description": "Finance optimization query",
            "query": "How can I reduce my farming costs?",
            "expected_agent": "finance"
        },
        {
            "description": "Crop selection query", 
            "query": "What crops are suitable for my region?",
            "expected_agent": "crop"
        },
        {
            "description": "Weather query",
            "query": "Will it rain this week?",
            "expected_agent": "weather"
        },
        {
            "description": "Policy query",
            "query": "How to apply for PM-Kisan scheme?",
            "expected_agent": "policy"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        response = make_query(test['query'])
        if response:
            agents_consulted = response.get("agents_consulted", [])
            expected = test["expected_agent"]
            
            if any(expected in str(agent) for agent in agents_consulted):
                print(f"✅ Correct routing to {expected} agent")
            else:
                print(f"❌ Unexpected routing: {agents_consulted} (expected {expected})")
            
            # Check for LLM routing metadata
            llm_routing = response.get("llm_routing")
            if llm_routing:
                print(f"   🧠 LLM Reasoning: {llm_routing.get('reasoning', 'N/A')}")
        else:
            print("❌ Query failed")
        
        time.sleep(0.5)

def make_query(query_text):
    """Make a query to the supervisor"""
    try:
        params = {
            'text': query_text,
            'location': 'Karnataka',
            'crop': 'general'
        }
        
        response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=25)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('response', {})
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def main():
    """Main test function"""
    print("🚀 Conversation Context & Intelligent Routing Test")
    print("=" * 70)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy. Starting conversation context tests...\n")
    
    # Test conversation flow
    test_conversation_flow()
    
    # Test context persistence
    test_context_persistence()
    
    # Test intelligent routing
    test_intelligent_routing_decision()
    
    print(f"\n🏁 All conversation context tests completed!")

if __name__ == "__main__":
    main()
