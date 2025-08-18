#!/usr/bin/env python3
"""
Test script to verify LLM-based routing vs keyword-based routing
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_llm_routing():
    """Test LLM-based routing with various queries"""
    
    test_cases = [
        {
            "query": "what crop would be suitable for my location",
            "expected_agent": "crop_agent",
            "description": "Crop suitability - should use LLM intelligence"
        },
        {
            "query": "I want to maximize my farm profit with limited water",
            "expected_reasoning": "complex optimization",
            "description": "Complex multi-domain query"
        },
        {
            "query": "PM-Kisan scheme application process",
            "expected_agent": "policy_agent",
            "description": "Clear policy query"
        },
        {
            "query": "Should I plant rice considering the upcoming monsoon?",
            "expected_reasoning": "weather and crop decision",
            "description": "Weather + crop decision making"
        },
        {
            "query": "Best time to sell wheat to get maximum price",
            "expected_agent": "finance_agent", 
            "description": "Market timing query"
        },
        {
            "query": "How to improve soil fertility organically",
            "expected_agent": "crop_agent",
            "description": "Soil management query"
        },
        {
            "query": "Climate change impact on agriculture",
            "expected_reasoning": "weather and crop impacts",
            "description": "Broad agricultural topic"
        }
    ]
    
    print("🤖 Testing LLM-Based Agent Routing")
    print("=" * 70)
    
    results = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['description']}")
        print(f"Query: '{test['query']}'")
        
        try:
            # Test the supervisor endpoint (which should use LLM routing)
            params = {
                'text': test['query'],
                'location': 'Karnataka',
                'crop': 'general'
            }
            
            response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                supervisor_response = data.get('response', {})
                agents_consulted = data.get('agents_consulted', [])
                workflow_trace = data.get('workflow_trace', 'unknown')
                
                # Check for LLM routing metadata
                llm_routing = None
                if 'llm_routing' in supervisor_response:
                    llm_routing = supervisor_response['llm_routing']
                
                print(f"✅ Response received")
                print(f"   🤖 Agents Consulted: {agents_consulted}")
                print(f"   🔍 Workflow: {workflow_trace}")
                
                if llm_routing:
                    print(f"   🧠 LLM Reasoning: {llm_routing.get('reasoning', 'N/A')}")
                    print(f"   📊 LLM Confidence: {llm_routing.get('confidence', 'N/A')}")
                    print(f"   📝 Query Type: {llm_routing.get('query_type', 'N/A')}")
                    routing_method = "🤖 LLM-based"
                else:
                    print(f"   ⚠️ No LLM routing metadata found - likely fallback used")
                    routing_method = "🔄 Fallback"
                
                # Check if expected agent was used (if specified)
                if 'expected_agent' in test:
                    agent_match = any(test['expected_agent'] in str(agent) for agent in agents_consulted)
                    if agent_match:
                        result_status = "✅ AGENT MATCH"
                    else:
                        result_status = f"❓ Different agent: {agents_consulted}"
                else:
                    result_status = "ℹ️ No specific agent expected"
                
                print(f"   🎯 Result: {result_status}")
                print(f"   🛠️ Routing Method: {routing_method}")
                
                results.append({
                    'test': test['description'],
                    'query': test['query'],
                    'agents': agents_consulted,
                    'llm_routing': llm_routing is not None,
                    'status': result_status,
                    'workflow': workflow_trace
                })
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
                results.append({
                    'test': test['description'],
                    'query': test['query'],
                    'agents': [],
                    'llm_routing': False,
                    'status': f"❌ HTTP {response.status_code}",
                    'workflow': 'error'
                })
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'test': test['description'],
                'query': test['query'],
                'agents': [],
                'llm_routing': False,
                'status': f"❌ Error: {str(e)}",
                'workflow': 'error'
            })
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n📊 LLM ROUTING TEST SUMMARY")
    print("=" * 70)
    
    total_tests = len(results)
    llm_routing_used = len([r for r in results if r['llm_routing']])
    successful_tests = len([r for r in results if "✅" in r['status'] or "ℹ️" in r['status']])
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"LLM Routing Used: {llm_routing_used}/{total_tests}")
    print(f"LLM Usage Rate: {(llm_routing_used/total_tests)*100:.1f}%")
    
    # Detailed analysis
    print(f"\n📋 DETAILED ANALYSIS:")
    for result in results:
        routing_indicator = "🤖" if result['llm_routing'] else "🔄"
        print(f"{routing_indicator} {result['status']} - {result['test']}")
        print(f"    Query: {result['query'][:60]}...")
        print(f"    Agents: {result['agents']}")
        print()

def compare_routing_methods():
    """Compare LLM routing vs traditional routing"""
    print("\n🔄 Comparing Routing Methods")
    print("=" * 50)
    
    test_query = "what crop would be suitable for my location"
    
    try:
        # Test supervisor (LLM routing)
        print("Testing Supervisor (LLM routing)...")
        supervisor_response = requests.get(f"{BASE_URL}/supervisor", 
                                          params={'text': test_query, 'location': 'Karnataka'}, 
                                          timeout=15)
        
        if supervisor_response.status_code == 200:
            supervisor_data = supervisor_response.json()
            supervisor_agents = supervisor_data.get('agents_consulted', [])
            supervisor_routing = supervisor_data.get('response', {}).get('llm_routing')
            
            print(f"   Agents: {supervisor_agents}")
            if supervisor_routing:
                print(f"   LLM Reasoning: {supervisor_routing.get('reasoning', 'N/A')}")
            else:
                print(f"   No LLM routing metadata (fallback used)")
        
        print(f"\n✅ Comparison completed")
        
    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")

def main():
    """Main test function"""
    print("🚀 LLM-Based Routing Test Suite")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("Please ensure the server is running at http://127.0.0.1:8000")
        return
    
    print("✅ API is healthy. Starting LLM routing tests...\n")
    
    # Test LLM routing
    test_llm_routing()
    
    # Compare methods
    compare_routing_methods()
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()

