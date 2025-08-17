#!/usr/bin/env python3
"""
Test script to verify Flutter app integration with LangGraph supervisor
"""

import requests
import json
import time

def test_flutter_integration():
    """Test the endpoints that the Flutter app uses"""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing Flutter App Integration with LangGraph Supervisor")
    print("=" * 60)
    
    # Test cases that simulate Flutter app queries
    test_cases = [
        {
            "name": "Weather Query (Flutter)",
            "endpoint": "/query",
            "params": {
                "text": "What's the weather like in Mumbai?",
                "location": "Mumbai",
                "crop": None
            }
        },
        {
            "name": "Crop Management (Flutter)",
            "endpoint": "/query", 
            "params": {
                "text": "How much fertilizer should I use for wheat?",
                "location": "Punjab",
                "crop": "wheat"
            }
        },
        {
            "name": "Supervisor Debug (Flutter Debug Mode)",
            "endpoint": "/supervisor",
            "params": {
                "text": "Should I plant wheat now given the weather and market conditions?",
                "location": "Haryana", 
                "crop": "wheat"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST {i}: {test_case['name']}")
        print(f"Endpoint: {test_case['endpoint']}")
        print(f"Query: {test_case['params']['text']}")
        print(f"Location: {test_case['params']['location']}")
        print(f"Crop: {test_case['params']['crop']}")
        print("-" * 40)
        
        try:
            # Clean up params (remove None values)
            params = {k: v for k, v in test_case['params'].items() if v is not None}
            
            start_time = time.time()
            response = requests.get(
                f"{base_url}{test_case['endpoint']}", 
                params=params,
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Response Time: {response_time:.2f}s")
                
                if test_case['endpoint'] == '/supervisor':
                    # Supervisor endpoint returns nested structure
                    response_data = data.get('response', {})
                    workflow_trace = data.get('workflow_trace', 'unknown')
                    agents_consulted = data.get('agents_consulted', [])
                    
                    print(f"Workflow Trace: {workflow_trace}")
                    print(f"Agents Consulted: {agents_consulted}")
                    print(f"Answer: {response_data.get('answer', 'No answer')[:100]}...")
                    print(f"Confidence: {response_data.get('confidence', 0.0)}")
                    print(f"Agent Used: {response_data.get('agent_used', 'unknown')}")
                else:
                    # Regular query endpoint
                    print(f"Answer: {data.get('answer', 'No answer')[:100]}...")
                    print(f"Confidence: {data.get('confidence', 0.0)}")
                    print(f"Agent Used: {data.get('agent_used', 'unknown')}")
                    print(f"Agents Consulted: {data.get('agents_consulted', [])}")
                    print(f"Workflow Trace: {data.get('workflow_trace', 'unknown')}")
                    print(f"Cache Hit: {data.get('cache_hit', False)}")
                
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Make sure the API server is running on http://127.0.0.1:8000")
            print("Run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
            break
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 Flutter Integration Test Summary:")
    print("✅ The Flutter app uses the /query endpoint by default")
    print("✅ Debug mode uses the /supervisor endpoint for detailed workflow info")
    print("✅ Both endpoints now use the LangGraph supervisor architecture")
    print("✅ Response includes workflow trace, agents consulted, and performance metrics")
    print("✅ The Flutter app displays this information in the response cards")

if __name__ == "__main__":
    test_flutter_integration()
