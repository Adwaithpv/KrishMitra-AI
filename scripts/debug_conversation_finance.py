#!/usr/bin/env python3
"""
Debug script for conversation context and finance agent issues
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def debug_conversation_flow():
    """Debug the conversation flow step by step"""
    
    print("🔍 DEBUGGING Conversation Context & Finance Agent")
    print("=" * 70)
    
    session_headers = {}
    
    # Step 1: Initial finance query
    print("\n📋 Step 1: Initial Finance Query")
    query1 = "I need help optimizing my farm finances"
    print(f"Query: '{query1}'")
    
    response1 = make_debug_query(query1, session_headers)
    if response1:
        print_debug_info("Step 1 Response", response1)
        
        # Extract session ID for continuity
        session_id = response1.get("session_id")
        if session_id:
            session_headers["X-Session-ID"] = session_id
            print(f"🔑 SESSION ID CAPTURED: {session_id}")
        else:
            print("⚠️ NO SESSION ID RETURNED")
    else:
        print("❌ Step 1 failed")
        return
    
    time.sleep(2)
    
    # Step 2: Provide financial information (should continue with finance agent)
    print("\n📋 Step 2: Providing Financial Information")
    query2 = "My farm is 5 acres and I spend 30000 on fertilizers annually"
    print(f"Query: '{query2}'")
    print(f"Session Headers: {session_headers}")
    
    response2 = make_debug_query(query2, session_headers)
    if response2:
        print_debug_info("Step 2 Response", response2)
        
        # Check if this was routed correctly
        agents_consulted = response2.get("agents_consulted", [])
        if any("finance" in str(agent) for agent in agents_consulted):
            print("✅ CORRECT: Finance agent continued conversation")
        else:
            print(f"❌ WRONG ROUTING: Expected finance agent, got {agents_consulted}")
    else:
        print("❌ Step 2 failed")
        return
    
    time.sleep(2)
    
    # Step 3: Provide more financial information
    print("\n📋 Step 3: More Financial Information")
    query3 = "I also spend 25000 on water and produce 120 quintals per year"
    print(f"Query: '{query3}'")
    
    response3 = make_debug_query(query3, session_headers)
    if response3:
        print_debug_info("Step 3 Response", response3)
        
        # Check conversation context accumulation
        context = response3.get("conversation_context")
        if context:
            print("📊 CONVERSATION CONTEXT:")
            print(f"   Summary: {context.get('conversation_summary', 'N/A')}")
            print(f"   Active Agent: {context.get('active_agent', 'None')}")
            print(f"   User Profile: {context.get('user_profile', {})}")
    else:
        print("❌ Step 3 failed")
        return
    
    time.sleep(2)
    
    # Step 4: Ask for comprehensive advice
    print("\n📋 Step 4: Request Comprehensive Financial Advice")
    query4 = "Now give me comprehensive financial optimization advice"
    print(f"Query: '{query4}'")
    
    response4 = make_debug_query(query4, session_headers)
    if response4:
        print_debug_info("Step 4 Response", response4)
        
        # Check if we got detailed advice instead of questions
        answer = response4.get("answer", "")
        if len(answer) > 500 and "optimization" in answer.lower():
            print("✅ SUCCESS: Got comprehensive financial advice")
        elif "form" in answer.lower() or "information" in answer.lower():
            print("⚠️ STILL ASKING FOR INFO: Finance agent may not be accumulating data")
        else:
            print("❓ UNCLEAR RESPONSE: Check answer content")
    else:
        print("❌ Step 4 failed")

def test_direct_supervisor():
    """Test supervisor endpoint directly"""
    print("\n🤖 Testing Direct Supervisor Routing")
    print("=" * 50)
    
    test_queries = [
        {
            "query": "I need financial advice for my farm",
            "expected": "finance_agent",
            "description": "Finance query routing"
        },
        {
            "query": "My farm is 5 acres, I spend ₹30,000 on fertilizers",
            "expected": "finance_agent", 
            "description": "Financial data continuation"
        }
    ]
    
    session_headers = {}
    
    for i, test in enumerate(test_queries, 1):
        print(f"\nTest {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        response = make_supervisor_query(test['query'], session_headers)
        if response:
            agents_consulted = response.get("agents_consulted", [])
            expected = test["expected"]
            
            if any(expected in str(agent) for agent in agents_consulted):
                print(f"✅ Correct routing to {expected}")
            else:
                print(f"❌ Wrong routing: {agents_consulted} (expected {expected})")
            
            # Capture session ID for continuity
            session_id = response.get("session_id")
            if session_id and not session_headers.get("X-Session-ID"):
                session_headers["X-Session-ID"] = session_id
                print(f"🔑 Session ID: {session_id}")
            
            # Check for context information
            context = response.get("conversation_context")
            if context:
                print(f"📊 Context: {context.get('conversation_summary', 'N/A')}")
        else:
            print("❌ Query failed")

def test_finance_agent_responses():
    """Test finance agent response quality"""
    print("\n💰 Testing Finance Agent Response Quality")
    print("=" * 50)
    
    # Direct finance queries
    finance_queries = [
        "How can I reduce my farming costs?",
        "I have 5 acres, spend ₹30,000 on fertilizers, ₹25,000 on water. How to optimize?",
        "What's the best investment for my farm?",
        "Help me increase profit from my cotton farm"
    ]
    
    for i, query in enumerate(finance_queries, 1):
        print(f"\nFinance Query {i}: '{query}'")
        
        response = make_supervisor_query(query)
        if response:
            agents_consulted = response.get("agents_consulted", [])
            if any("finance" in str(agent) for agent in agents_consulted):
                print("✅ Routed to finance agent")
                
                answer = response.get("answer", "")
                if len(answer) > 200:
                    print(f"📝 Response length: {len(answer)} chars (Good)")
                    
                    # Check for key finance terms
                    finance_terms = ["cost", "profit", "optimization", "investment", "₹", "strategy"]
                    terms_found = [term for term in finance_terms if term.lower() in answer.lower()]
                    print(f"💡 Finance terms found: {terms_found}")
                    
                    # Check if asking for more info
                    if any(phrase in answer.lower() for phrase in ["need more", "please provide", "information"]):
                        print("📝 Agent asking for more information")
                    else:
                        print("💬 Agent providing direct advice")
                else:
                    print(f"⚠️ Short response: {len(answer)} chars")
            else:
                print(f"❌ Wrong routing: {agents_consulted}")
        else:
            print("❌ Query failed")

def make_debug_query(query_text, headers=None):
    """Make a query with debug information"""
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
            print(f"   Response: {response.text[:200]}...")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def make_supervisor_query(query_text, headers=None):
    """Make a query to supervisor endpoint directly"""
    try:
        params = {
            'text': query_text,
            'location': 'Karnataka',
            'crop': 'wheat'
        }
        
        response = requests.get(f"{BASE_URL}/supervisor", params=params, headers=headers or {}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("response", {})
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def print_debug_info(step_name, response):
    """Print detailed debug information"""
    print(f"\n🔍 DEBUG INFO for {step_name}:")
    print(f"   Agents Consulted: {response.get('agents_consulted', [])}")
    print(f"   Agent Used: {response.get('agent_used', 'Unknown')}")
    print(f"   Session ID: {response.get('session_id', 'None')}")
    print(f"   Response Length: {len(response.get('answer', ''))} chars")
    
    # Check for conversation context
    context = response.get("conversation_context")
    if context:
        print(f"   Active Agent: {context.get('active_agent', 'None')}")
        print(f"   Expecting Response: {context.get('expecting_response', False)}")
        print(f"   Context Summary: {context.get('conversation_summary', 'N/A')}")
    else:
        print("   ⚠️ No conversation context")
    
    # Check for LLM routing info
    llm_routing = response.get("llm_routing")
    if llm_routing:
        print(f"   LLM Reasoning: {llm_routing.get('reasoning', 'N/A')}")
    
    # Show first 150 chars of answer
    answer = response.get("answer", "")
    if answer:
        print(f"   Answer Preview: {answer[:150]}...")
    
    print()

def main():
    """Main debug function"""
    print("🚀 Conversation Context & Finance Agent Debug")
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
    
    print("✅ API is healthy. Starting debug tests...\n")
    
    # Debug conversation flow
    debug_conversation_flow()
    
    # Test direct supervisor
    test_direct_supervisor()
    
    # Test finance agent responses
    test_finance_agent_responses()
    
    print(f"\n🏁 Debug session completed!")

if __name__ == "__main__":
    main()
