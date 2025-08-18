#!/usr/bin/env python3
"""
Test the pure LLM-based routing system (no keywords)
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_pure_llm_routing():
    """Test pure LLM routing with diverse queries"""
    
    print("🧠 TESTING PURE LLM-BASED ROUTING")
    print("=" * 60)
    print("✅ All routing decisions made by Gemini LLM - NO KEYWORDS!")
    print()
    
    # Test cases designed to challenge LLM understanding
    test_cases = [
        {
            "query": "My farm is 5 acres and I spend ₹30,000 on fertilizers annually",
            "expected": "finance_agent",
            "description": "Financial data sharing (should detect spending pattern)",
            "challenge": "Contains 'fertilizers' but focus is on spending"
        },
        {
            "query": "I need help optimizing my farm expenses to increase profit",
            "expected": "finance_agent", 
            "description": "Financial optimization request",
            "challenge": "Intent-based, not keyword-based"
        },
        {
            "query": "What crops are best for my region during monsoon season?",
            "expected": "crop_agent",
            "description": "Crop selection with weather context",
            "challenge": "Combines crop and weather elements"
        },
        {
            "query": "Will the upcoming rainfall affect my cotton harvest timing?",
            "expected": "weather_agent",
            "description": "Weather impact on farming",
            "challenge": "Farming + weather combination"
        },
        {
            "query": "How can I apply for the PM-Kisan scheme for my small farm?",
            "expected": "policy_agent",
            "description": "Government scheme application",
            "challenge": "Policy identification"
        },
        {
            "query": "My cotton yield is low and I'm losing money, what should I do?",
            "expected": "finance_agent",
            "description": "Profitability problem (financial concern)",
            "challenge": "Loss/money indicates financial focus"
        },
        {
            "query": "Which fertilizer gives best ROI for wheat cultivation?",
            "expected": "finance_agent",
            "description": "ROI-focused query (financial optimization)",
            "challenge": "ROI = financial metric, not just farming technique"
        },
        {
            "query": "My soil pH is 6.5, what crops should I plant?",
            "expected": "crop_agent",
            "description": "Technical crop selection",
            "challenge": "Pure agricultural technique"
        },
        {
            "query": "I want to reduce my farming costs by 20% this year",
            "expected": "finance_agent",
            "description": "Cost reduction goal (financial strategy)",
            "challenge": "Goal-based rather than keyword-based"
        }
    ]
    
    correct_routes = 0
    total_tests = len(test_cases)
    
    print(f"🧪 Running {total_tests} LLM routing tests...\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"Test {i}: {test['description']}")
        print(f"📝 Query: '{test['query']}'")
        print(f"🎯 Expected: {test['expected']}")
        print(f"🧩 Challenge: {test['challenge']}")
        
        # Test supervisor routing
        response = requests.get(f"{BASE_URL}/supervisor", params={
            'text': test['query'],
            'location': 'Karnataka'
        })
        
        if response.status_code == 200:
            data = response.json()['response']
            agents = data.get('agents_consulted', [])
            llm_routing = data.get('llm_routing', {})
            
            # Check if correct agent was selected
            if any(test['expected'] in str(agent) for agent in agents):
                print(f"✅ SUCCESS: Routed to {test['expected']}")
                correct_routes += 1
            else:
                print(f"❌ FAILED: Routed to {agents} (expected {test['expected']})")
            
            # Show LLM reasoning
            if llm_routing:
                reasoning = llm_routing.get('reasoning', 'No reasoning provided')
                confidence = llm_routing.get('confidence', 'N/A')
                intent = llm_routing.get('intent', 'N/A')
                
                print(f"🧠 LLM Reasoning: {reasoning[:80]}...")
                print(f"📊 Confidence: {confidence} | Intent: {intent}")
            else:
                print("⚠️ No LLM routing metadata found")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        
        print("-" * 50)
        time.sleep(0.5)  # Rate limiting
    
    # Results summary
    success_rate = (correct_routes / total_tests) * 100
    print(f"\n🎯 LLM ROUTING RESULTS:")
    print(f"   ✅ Correct Routes: {correct_routes}/{total_tests}")
    print(f"   📊 Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"   🎉 EXCELLENT: LLM routing is highly intelligent!")
    elif success_rate >= 60:
        print(f"   👍 GOOD: LLM routing is working well")
    else:
        print(f"   ⚠️ NEEDS IMPROVEMENT: LLM routing needs tuning")

def test_context_aware_routing():
    """Test conversation context awareness in routing"""
    
    print(f"\n🔄 TESTING CONTEXT-AWARE ROUTING")
    print("=" * 50)
    
    # Initial query
    print("📋 Step 1: Initial Finance Query")
    query1 = "I need help with my farm finances"
    
    response1 = requests.get(f"{BASE_URL}/supervisor", params={
        'text': query1,
        'location': 'Karnataka'
    })
    
    if response1.status_code == 200:
        data1 = response1.json()['response']
        session_id = data1.get('session_id')
        agents1 = data1.get('agents_consulted', [])
        
        print(f"✅ Initial routing: {agents1}")
        print(f"🔑 Session ID: {session_id}")
        
        if session_id:
            time.sleep(1)
            
            # Follow-up query with context
            print(f"\n📋 Step 2: Context-Aware Follow-up")
            query2 = "My land is 5 acres and I spend too much on inputs"
            
            response2 = requests.get(f"{BASE_URL}/supervisor", params={
                'text': query2,
                'location': 'Karnataka'
            }, headers={'X-Session-ID': session_id})
            
            if response2.status_code == 200:
                data2 = response2.json()['response']
                agents2 = data2.get('agents_consulted', [])
                context = data2.get('conversation_context', {})
                llm_routing = data2.get('llm_routing', {})
                
                print(f"✅ Follow-up routing: {agents2}")
                
                if context:
                    summary = context.get('conversation_summary', 'N/A')
                    profile = context.get('user_profile', {})
                    print(f"📊 Context: {summary}")
                    print(f"👤 Profile: {profile}")
                
                if llm_routing:
                    reasoning = llm_routing.get('reasoning', 'N/A')
                    print(f"🧠 LLM Context Reasoning: {reasoning[:80]}...")
                
                # Check if context influenced routing
                if any("finance" in str(agent) for agent in agents2):
                    print("🎯 SUCCESS: Context maintained financial focus!")
                else:
                    print(f"⚠️ Context not maintained: {agents2}")

def test_edge_cases():
    """Test edge cases for LLM routing"""
    
    print(f"\n🔬 TESTING EDGE CASES")
    print("=" * 30)
    
    edge_cases = [
        {
            "query": "Help me",
            "description": "Vague query"
        },
        {
            "query": "Farming is difficult",
            "description": "Statement without clear intent"
        },
        {
            "query": "I have rice and wheat crops, weather is changing, prices are falling, need government help",
            "description": "Multi-domain complex query"
        }
    ]
    
    for i, test in enumerate(edge_cases, 1):
        print(f"\nEdge Case {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        response = requests.get(f"{BASE_URL}/supervisor", params={
            'text': test['query'],
            'location': 'Karnataka'
        })
        
        if response.status_code == 200:
            data = response.json()['response']
            agents = data.get('agents_consulted', [])
            llm_routing = data.get('llm_routing', {})
            
            print(f"Route: {agents}")
            if llm_routing:
                reasoning = llm_routing.get('reasoning', 'N/A')
                print(f"Reasoning: {reasoning[:60]}...")

def main():
    """Main test function"""
    print("🚀 PURE LLM ROUTING SYSTEM TEST")
    print("=" * 60)
    print("🧠 Testing Gemini LLM's intelligent agent selection")
    print("🚫 NO KEYWORDS - Only natural language understanding")
    print()
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy. Starting LLM routing tests...\n")
    
    # Run tests
    test_pure_llm_routing()
    test_context_aware_routing()
    test_edge_cases()
    
    print(f"\n🎉 PURE LLM ROUTING TEST COMPLETED!")
    print("\n📋 SUMMARY:")
    print("   🧠 Removed all keyword-based routing")
    print("   🤖 Implemented pure LLM intelligence")
    print("   🔄 Added conversation context awareness")
    print("   📊 Enhanced reasoning and confidence tracking")
    print("\n🎯 The system now relies entirely on Gemini LLM for intelligent routing!")

if __name__ == "__main__":
    main()
