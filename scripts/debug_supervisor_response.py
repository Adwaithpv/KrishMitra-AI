#!/usr/bin/env python3
"""
Debug supervisor response structure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.supervisor import SupervisorAgent

def test_supervisor_directly():
    """Test supervisor agent directly"""
    
    print("🔍 TESTING SUPERVISOR AGENT DIRECTLY")
    print("=" * 50)
    
    # Initialize supervisor
    supervisor = SupervisorAgent()
    
    # Test query
    query = "My farm is 5 acres and I spend 30000 on fertilizers annually"
    location = "Karnataka"
    session_id = "test_session_123"
    
    print(f"Query: '{query}'")
    print(f"Location: {location}")
    print(f"Session ID: {session_id}")
    print()
    
    # Process query
    response = supervisor.process_query(query, location, None, session_id)
    
    print("📊 SUPERVISOR RESPONSE:")
    print(f"   Type: {type(response)}")
    print(f"   Keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
    print()
    
    if isinstance(response, dict):
        for key, value in response.items():
            print(f"   {key}: {value}")
    
    print()
    
    # Test specific fields
    critical_fields = ['agents_consulted', 'session_id', 'conversation_context', 'llm_routing']
    
    print("🔍 CRITICAL FIELDS CHECK:")
    for field in critical_fields:
        if field in response:
            print(f"   ✅ {field}: {response[field]}")
        else:
            print(f"   ❌ {field}: MISSING")

def test_with_finance_query():
    """Test with a finance-specific query"""
    
    print("\n💰 TESTING FINANCE QUERY")
    print("=" * 30)
    
    supervisor = SupervisorAgent()
    
    query = "I need financial advice for my farm"
    session_id = "finance_test_456"
    
    response = supervisor.process_query(query, None, None, session_id)
    
    print(f"Query: '{query}'")
    print(f"Response agent: {response.get('agent_used', 'Unknown')}")
    print(f"Agents consulted: {response.get('agents_consulted', [])}")
    print(f"Session ID: {response.get('session_id', 'None')}")
    
    # Check if finance agent was used
    agents = response.get('agents_consulted', [])
    if any('finance' in str(agent) for agent in agents):
        print("✅ Finance agent was consulted")
    else:
        print(f"❌ Finance agent not consulted. Got: {agents}")

def main():
    """Main test function"""
    print("🚀 DIRECT SUPERVISOR TESTING")
    print("=" * 50)
    
    try:
        test_supervisor_directly()
        test_with_finance_query()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
