#!/usr/bin/env python3
"""
Debug the main endpoint vs supervisor endpoint discrepancy
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint_comparison():
    """Compare main endpoint vs supervisor endpoint"""
    
    test_query = "My farm is 5 acres and I spend 30000 on fertilizers annually"
    
    print("🔍 COMPARING MAIN vs SUPERVISOR ENDPOINT")
    print("=" * 60)
    print(f"Test Query: '{test_query}'")
    print()
    
    # Test supervisor endpoint directly
    print("📊 SUPERVISOR ENDPOINT:")
    supervisor_resp = requests.get(f"{BASE_URL}/supervisor", params={
        'text': test_query,
        'location': 'Karnataka'
    })
    
    if supervisor_resp.status_code == 200:
        supervisor_data = supervisor_resp.json()
        supervisor_response = supervisor_data.get('response', {})
        
        print(f"   ✅ Status: {supervisor_resp.status_code}")
        print(f"   🤖 Agent Used: {supervisor_response.get('agent_used', 'Unknown')}")
        print(f"   👥 Agents Consulted: {supervisor_response.get('agents_consulted', [])}")
        print(f"   🎯 Confidence: {supervisor_response.get('confidence', 0.0)}")
        print(f"   🔑 Session ID: {supervisor_response.get('session_id', 'None')}")
        
        context = supervisor_response.get('conversation_context')
        if context:
            print(f"   📝 Context Active Agent: {context.get('active_agent', 'None')}")
            print(f"   📝 Context Summary: {context.get('conversation_summary', 'None')}")
        
        llm_routing = supervisor_response.get('llm_routing')
        if llm_routing:
            print(f"   🧠 LLM Reasoning: {llm_routing.get('reasoning', 'N/A')[:100]}...")
    else:
        print(f"   ❌ Status: {supervisor_resp.status_code}")
    
    print()
    
    # Test main endpoint
    print("📊 MAIN ENDPOINT:")
    main_resp = requests.get(f"{BASE_URL}/query", params={
        'text': test_query,
        'location': 'Karnataka'
    })
    
    if main_resp.status_code == 200:
        main_data = main_resp.json()
        
        print(f"   ✅ Status: {main_resp.status_code}")
        print(f"   🤖 Agent Used: {main_data.get('agent_used', 'Unknown')}")
        print(f"   👥 Agents Consulted: {main_data.get('agents_consulted', [])}")
        print(f"   🎯 Confidence: {main_data.get('confidence', 0.0)}")
        print(f"   🔑 Session ID: {main_data.get('session_id', 'None')}")
        
        context = main_data.get('conversation_context')
        if context:
            print(f"   📝 Context Active Agent: {context.get('active_agent', 'None')}")
            print(f"   📝 Context Summary: {context.get('conversation_summary', 'None')}")
        
        llm_routing = main_data.get('llm_routing')
        if llm_routing:
            print(f"   🧠 LLM Reasoning: {llm_routing.get('reasoning', 'N/A')[:100]}...")
        
        print(f"   📄 Answer Length: {len(main_data.get('answer', ''))} chars")
        print(f"   📄 Answer Preview: {main_data.get('answer', '')[:100]}...")
    else:
        print(f"   ❌ Status: {main_resp.status_code}")
    
    print()
    
    # Compare results
    print("🔍 COMPARISON ANALYSIS:")
    if supervisor_resp.status_code == 200 and main_resp.status_code == 200:
        supervisor_response = supervisor_data.get('response', {})
        
        sup_agents = supervisor_response.get('agents_consulted', [])
        main_agents = main_data.get('agents_consulted', [])
        
        sup_session = supervisor_response.get('session_id')
        main_session = main_data.get('session_id')
        
        sup_agent_used = supervisor_response.get('agent_used')
        main_agent_used = main_data.get('agent_used')
        
        if sup_agents == main_agents:
            print("   ✅ Agents Consulted: MATCH")
        else:
            print(f"   ❌ Agents Consulted: MISMATCH (Supervisor: {sup_agents} vs Main: {main_agents})")
        
        if sup_session and main_session:
            print("   ✅ Session IDs: Both present")
        elif sup_session:
            print("   ⚠️ Session IDs: Only supervisor has session ID")
        elif main_session:
            print("   ⚠️ Session IDs: Only main has session ID")
        else:
            print("   ❌ Session IDs: Both missing")
        
        if sup_agent_used == main_agent_used:
            print("   ✅ Agent Used: MATCH")
        else:
            print(f"   ❌ Agent Used: MISMATCH (Supervisor: {sup_agent_used} vs Main: {main_agent_used})")
    
    print()

def test_multiple_queries():
    """Test with different types of queries"""
    
    test_cases = [
        {
            "query": "I need financial advice for my farm",
            "expected": "finance_agent",
            "description": "Direct finance request"
        },
        {
            "query": "My farm is 5 acres, I spend ₹30,000 on fertilizers",
            "expected": "finance_agent",
            "description": "Financial data sharing"
        },
        {
            "query": "What crops are suitable for Karnataka?",
            "expected": "crop_agent", 
            "description": "Crop selection query"
        },
        {
            "query": "Will it rain this week?",
            "expected": "weather_agent",
            "description": "Weather query"
        }
    ]
    
    print("🧪 MULTI-QUERY ENDPOINT COMPARISON")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Query: '{test['query']}'")
        print(f"   Expected: {test['expected']}")
        
        # Test both endpoints
        supervisor_resp = requests.get(f"{BASE_URL}/supervisor", params={'text': test['query']})
        main_resp = requests.get(f"{BASE_URL}/query", params={'text': test['query']})
        
        if supervisor_resp.status_code == 200:
            sup_data = supervisor_resp.json()['response']
            sup_agents = sup_data.get('agents_consulted', [])
            sup_correct = any(test['expected'] in str(agent) for agent in sup_agents)
            print(f"   📊 Supervisor: {sup_agents} {'✅' if sup_correct else '❌'}")
        
        if main_resp.status_code == 200:
            main_data = main_resp.json()
            main_agents = main_data.get('agents_consulted', [])
            main_correct = any(test['expected'] in str(agent) for agent in main_agents)
            print(f"   📊 Main: {main_agents} {'✅' if main_correct else '❌'}")

def main():
    """Main debug function"""
    print("🚀 MAIN vs SUPERVISOR ENDPOINT DEBUG")
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
    
    print("✅ API is healthy. Starting debug tests...\n")
    
    # Test single query comparison
    test_endpoint_comparison()
    
    # Test multiple queries
    test_multiple_queries()
    
    print(f"\n🏁 Debug completed!")

if __name__ == "__main__":
    main()
