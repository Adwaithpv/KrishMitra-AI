#!/usr/bin/env python3
"""
Test script for the new LangGraph-based Supervisor Agent
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_supervisor_health():
    """Test if the supervisor endpoint is available"""
    print("🔍 Testing Supervisor Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_supervisor_workflow():
    """Test the supervisor workflow with different query types"""
    print("\n🤖 Testing Supervisor Workflow...")
    
    test_cases = [
        {
            "category": "Weather Queries",
            "tests": [
                {
                    "query": "What's the weather like for rice farming in Karnataka?",
                    "location": "Karnataka",
                    "crop": "rice",
                    "description": "Weather + crop specific query"
                },
                {
                    "query": "Heavy rainfall alert for wheat fields",
                    "location": "Punjab",
                    "crop": "wheat",
                    "description": "Weather alert query"
                }
            ]
        },
        {
            "category": "Crop Management Queries",
            "tests": [
                {
                    "query": "Irrigation schedule for cotton in Gujarat",
                    "location": "Gujarat",
                    "crop": "cotton",
                    "description": "Irrigation query"
                },
                {
                    "query": "Fertilizer application for pulses",
                    "location": "Madhya Pradesh",
                    "crop": "pulses",
                    "description": "Fertilizer query"
                }
            ]
        },
        {
            "category": "Finance Queries",
            "tests": [
                {
                    "query": "Market prices for wheat in Punjab",
                    "location": "Punjab",
                    "crop": "wheat",
                    "description": "Market price query"
                },
                {
                    "query": "Subsidy schemes for farmers",
                    "location": "Maharashtra",
                    "crop": None,
                    "description": "Subsidy query"
                }
            ]
        },
        {
            "category": "Policy Queries",
            "tests": [
                {
                    "query": "PM-Kisan eligibility criteria",
                    "location": "Uttar Pradesh",
                    "crop": None,
                    "description": "Policy eligibility query"
                },
                {
                    "query": "How to apply for crop insurance?",
                    "location": "Rajasthan",
                    "crop": "bajra",
                    "description": "Insurance application query"
                }
            ]
        },
        {
            "category": "Complex Multi-Agent Queries",
            "tests": [
                {
                    "query": "Weather conditions and market prices for rice in Tamil Nadu",
                    "location": "Tamil Nadu",
                    "crop": "rice",
                    "description": "Weather + market query"
                },
                {
                    "query": "Irrigation advice and subsidy schemes for wheat farming",
                    "location": "Haryana",
                    "crop": "wheat",
                    "description": "Irrigation + policy query"
                }
            ]
        }
    ]
    
    results = []
    
    for category in test_cases:
        print(f"\n📋 {category['category']}")
        print("=" * 50)
        
        for test in category['tests']:
            print(f"\n🔍 Testing: {test['description']}")
            print(f"Query: {test['query']}")
            print(f"Location: {test['location']}")
            print(f"Crop: {test['crop']}")
            
            try:
                # Test supervisor endpoint
                params = {
                    'text': test['query'],
                    'location': test['location'],
                    'crop': test['crop']
                }
                
                response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract key information
                    supervisor_response = data.get('response', {})
                    answer = supervisor_response.get('answer', 'No answer')
                    confidence = supervisor_response.get('confidence', 0.0)
                    agents_consulted = data.get('agents_consulted', [])
                    workflow_trace = data.get('workflow_trace', 'unknown')
                    
                    print(f"✅ Success!")
                    print(f"   Answer: {answer[:100]}...")
                    print(f"   Confidence: {confidence}")
                    print(f"   Agents Consulted: {agents_consulted}")
                    print(f"   Workflow Trace: {workflow_trace}")
                    
                    results.append({
                        'test': test['description'],
                        'status': 'success',
                        'confidence': confidence,
                        'agents_consulted': agents_consulted,
                        'workflow_trace': workflow_trace,
                        'answer_length': len(answer)
                    })
                    
                else:
                    print(f"❌ HTTP Error: {response.status_code}")
                    print(f"   Response: {response.text}")
                    
                    results.append({
                        'test': test['description'],
                        'status': 'http_error',
                        'error': f"HTTP {response.status_code}"
                    })
                    
            except requests.exceptions.Timeout:
                print("❌ Timeout - request took too long")
                results.append({
                    'test': test['description'],
                    'status': 'timeout'
                })
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append({
                    'test': test['description'],
                    'status': 'error',
                    'error': str(e)
                })
            
            # Small delay between requests
            time.sleep(1)
    
    return results

def test_supervisor_vs_legacy():
    """Compare supervisor vs legacy coordinator"""
    print("\n🔄 Comparing Supervisor vs Legacy Coordinator...")
    
    test_query = "Weather conditions and irrigation advice for rice in Karnataka"
    location = "Karnataka"
    crop = "rice"
    
    try:
        # Test supervisor
        print("Testing Supervisor...")
        supervisor_params = {
            'text': test_query,
            'location': location,
            'crop': crop
        }
        
        supervisor_response = requests.get(f"{BASE_URL}/supervisor", params=supervisor_params, timeout=30)
        
        if supervisor_response.status_code == 200:
            supervisor_data = supervisor_response.json()
            supervisor_answer = supervisor_data.get('response', {}).get('answer', '')
            supervisor_confidence = supervisor_data.get('response', {}).get('confidence', 0.0)
            supervisor_agents = supervisor_data.get('agents_consulted', [])
            
            print(f"   Supervisor Answer: {supervisor_answer[:100]}...")
            print(f"   Supervisor Confidence: {supervisor_confidence}")
            print(f"   Supervisor Agents: {supervisor_agents}")
        
        # Test legacy agents endpoint
        print("\nTesting Legacy Agents...")
        legacy_params = {
            'text': test_query,
            'location': location,
            'crop': crop
        }
        
        legacy_response = requests.get(f"{BASE_URL}/agents", params=legacy_params, timeout=30)
        
        if legacy_response.status_code == 200:
            legacy_data = legacy_response.json()
            legacy_answer = legacy_data.get('answer', '')
            legacy_confidence = legacy_data.get('confidence', 0.0)
            legacy_agents = legacy_data.get('agents_consulted', [])
            
            print(f"   Legacy Answer: {legacy_answer[:100]}...")
            print(f"   Legacy Confidence: {legacy_confidence}")
            print(f"   Legacy Agents: {legacy_agents}")
        
        print("\n✅ Comparison completed")
        
    except Exception as e:
        print(f"❌ Comparison failed: {str(e)}")

def generate_report(results):
    """Generate a summary report"""
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    total_tests = len(results)
    successful_tests = len([r for r in results if r['status'] == 'success'])
    failed_tests = total_tests - successful_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_confidence = sum([r['confidence'] for r in results if r['status'] == 'success']) / successful_tests
        print(f"Average Confidence: {avg_confidence:.3f}")
        
        # Agent usage statistics
        all_agents = []
        for r in results:
            if r['status'] == 'success':
                all_agents.extend(r['agents_consulted'])
        
        agent_counts = {}
        for agent in all_agents:
            agent_counts[agent] = agent_counts.get(agent, 0) + 1
        
        print(f"\nAgent Usage:")
        for agent, count in agent_counts.items():
            print(f"  {agent}: {count} times")
    
    # Failed tests
    if failed_tests > 0:
        print(f"\nFailed Tests:")
        for r in results:
            if r['status'] != 'success':
                print(f"  - {r['test']}: {r['status']}")

def main():
    """Main test function"""
    print("🚀 LangGraph Supervisor Agent Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test health
    if not test_supervisor_health():
        print("❌ Health check failed. Exiting.")
        return
    
    # Test supervisor workflow
    results = test_supervisor_workflow()
    
    # Compare with legacy
    test_supervisor_vs_legacy()
    
    # Generate report
    generate_report(results)
    
    print(f"\n🏁 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
