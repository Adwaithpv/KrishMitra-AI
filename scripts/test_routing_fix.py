#!/usr/bin/env python3
"""
Test script to verify the routing fix for crop-related queries
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_routing_queries():
    """Test various queries that should route to different agents"""
    
    test_cases = [
        {
            "query": "what crop would be suitable for my location",
            "expected_agent": "crop_agent",
            "description": "Crop suitability query"
        },
        {
            "query": "which crops can I grow in Karnataka",
            "expected_agent": "crop_agent", 
            "description": "Crop selection query"
        },
        {
            "query": "suitable varieties for rice farming",
            "expected_agent": "crop_agent",
            "description": "Variety selection query"
        },
        {
            "query": "how to cultivate wheat",
            "expected_agent": "crop_agent",
            "description": "Cultivation guidance query"
        },
        {
            "query": "PM-Kisan scheme details",
            "expected_agent": "policy_agent",
            "description": "Policy scheme query"
        },
        {
            "query": "weather forecast for farming",
            "expected_agent": "weather_agent",
            "description": "Weather query"
        },
        {
            "query": "market prices for wheat",
            "expected_agent": "finance_agent",
            "description": "Market price query"
        },
        {
            "query": "general farming advice",
            "expected_agent": "crop_agent",
            "description": "General agricultural query"
        }
    ]
    
    print("🔍 Testing Agent Routing Fix...")
    print("=" * 60)
    
    results = []
    
    for test in test_cases:
        print(f"\n🧪 Testing: {test['description']}")
        print(f"Query: '{test['query']}'")
        print(f"Expected Agent: {test['expected_agent']}")
        
        try:
            # Test the supervisor endpoint
            params = {
                'text': test['query'],
                'location': 'Karnataka',
                'crop': 'general'
            }
            
            response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                agents_consulted = data.get('agents_consulted', [])
                workflow_trace = data.get('workflow_trace', 'unknown')
                
                # Check if the expected agent was consulted
                agent_match = any(test['expected_agent'] in str(agent) for agent in agents_consulted)
                
                if agent_match:
                    print(f"✅ CORRECT ROUTING: {agents_consulted}")
                    status = "✅ PASS"
                else:
                    print(f"❌ WRONG ROUTING: Expected {test['expected_agent']}, got {agents_consulted}")
                    status = "❌ FAIL"
                
                print(f"   Workflow: {workflow_trace}")
                
                results.append({
                    'query': test['query'],
                    'expected': test['expected_agent'],
                    'actual': agents_consulted,
                    'status': status,
                    'workflow': workflow_trace
                })
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                results.append({
                    'query': test['query'],
                    'expected': test['expected_agent'],
                    'actual': f"HTTP {response.status_code}",
                    'status': "❌ ERROR",
                    'workflow': 'error'
                })
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'query': test['query'],
                'expected': test['expected_agent'],
                'actual': f"Error: {str(e)}",
                'status': "❌ ERROR",
                'workflow': 'error'
            })
        
        time.sleep(1)  # Rate limiting
    
    # Summary
    print(f"\n📊 ROUTING TEST SUMMARY")
    print("=" * 60)
    
    passed = len([r for r in results if "✅" in r['status']])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        print(f"{result['status']} {result['query'][:50]}...")
        print(f"    Expected: {result['expected']}")
        print(f"    Actual: {result['actual']}")
        print()

def main():
    """Main test function"""
    print("🚀 Agent Routing Fix Verification")
    print("=" * 60)
    
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
    
    print("✅ API is healthy. Starting routing tests...\n")
    test_routing_queries()

if __name__ == "__main__":
    main()

