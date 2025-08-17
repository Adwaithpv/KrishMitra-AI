#!/usr/bin/env python3
"""
Example usage of the LangGraph Supervisor Agent
Demonstrates how to use the new supervisor architecture
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def example_supervisor_queries():
    """Example queries demonstrating the supervisor's capabilities"""
    
    print("🚀 LangGraph Supervisor Agent Examples")
    print("=" * 50)
    
    # Example 1: Simple weather query
    print("\n1️⃣ Simple Weather Query")
    print("-" * 30)
    
    weather_query = {
        "text": "What's the weather like for rice farming in Karnataka?",
        "location": "Karnataka",
        "crop": "rice"
    }
    
    response = requests.get(f"{BASE_URL}/supervisor", params=weather_query)
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Answer: {data['response']['answer'][:150]}...")
        print(f"Confidence: {data['response']['confidence']}")
        print(f"Agents: {data['agents_consulted']}")
        print(f"Workflow: {data['workflow_trace']}")
    
    # Example 2: Complex multi-agent query
    print("\n2️⃣ Complex Multi-Agent Query")
    print("-" * 30)
    
    complex_query = {
        "text": "Weather conditions and market prices for rice in Tamil Nadu, plus subsidy information",
        "location": "Tamil Nadu",
        "crop": "rice"
    }
    
    response = requests.get(f"{BASE_URL}/supervisor", params=complex_query)
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Answer: {data['response']['answer'][:150]}...")
        print(f"Confidence: {data['response']['confidence']}")
        print(f"Agents: {data['agents_consulted']}")
        print(f"Workflow: {data['workflow_trace']}")
    
    # Example 3: Policy-focused query
    print("\n3️⃣ Policy-Focused Query")
    print("-" * 30)
    
    policy_query = {
        "text": "How to apply for PM-Kisan scheme and what documents are needed?",
        "location": "Uttar Pradesh",
        "crop": None
    }
    
    response = requests.get(f"{BASE_URL}/supervisor", params=policy_query)
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Answer: {data['response']['answer'][:150]}...")
        print(f"Confidence: {data['response']['confidence']}")
        print(f"Agents: {data['agents_consulted']}")
        print(f"Workflow: {data['workflow_trace']}")
    
    # Example 4: Finance and market query
    print("\n4️⃣ Finance and Market Query")
    print("-" * 30)
    
    finance_query = {
        "text": "Current wheat prices in Punjab and available credit schemes",
        "location": "Punjab",
        "crop": "wheat"
    }
    
    response = requests.get(f"{BASE_URL}/supervisor", params=finance_query)
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {data['query']}")
        print(f"Answer: {data['response']['answer'][:150]}...")
        print(f"Confidence: {data['response']['confidence']}")
        print(f"Agents: {data['agents_consulted']}")
        print(f"Workflow: {data['workflow_trace']}")

def compare_supervisor_vs_legacy():
    """Compare supervisor vs legacy coordinator"""
    
    print("\n🔄 Supervisor vs Legacy Comparison")
    print("=" * 50)
    
    test_query = {
        "text": "Irrigation advice for cotton in Gujarat",
        "location": "Gujarat",
        "crop": "cotton"
    }
    
    # Test supervisor
    print("\n📊 Supervisor Response:")
    supervisor_response = requests.get(f"{BASE_URL}/supervisor", params=test_query)
    if supervisor_response.status_code == 200:
        supervisor_data = supervisor_response.json()
        print(f"  Answer: {supervisor_data['response']['answer'][:100]}...")
        print(f"  Confidence: {supervisor_data['response']['confidence']}")
        print(f"  Agents: {supervisor_data['agents_consulted']}")
        print(f"  Workflow: {supervisor_data['workflow_trace']}")
    
    # Test legacy
    print("\n📊 Legacy Response:")
    legacy_response = requests.get(f"{BASE_URL}/agents", params=test_query)
    if legacy_response.status_code == 200:
        legacy_data = legacy_response.json()
        print(f"  Answer: {legacy_data['answer'][:100]}...")
        print(f"  Confidence: {legacy_data['confidence']}")
        print(f"  Agents: {legacy_data['agents_consulted']}")

def demonstrate_workflow_traces():
    """Demonstrate different workflow traces"""
    
    print("\n🔍 Workflow Trace Examples")
    print("=" * 50)
    
    queries = [
        {
            "name": "Weather Only",
            "params": {
                "text": "Rainfall forecast for tomorrow",
                "location": "Mumbai",
                "crop": None
            }
        },
        {
            "name": "Crop Management",
            "params": {
                "text": "Fertilizer application for wheat",
                "location": "Haryana",
                "crop": "wheat"
            }
        },
        {
            "name": "Multi-Agent Complex",
            "params": {
                "text": "Weather, market prices, and subsidy info for rice farming",
                "location": "Andhra Pradesh",
                "crop": "rice"
            }
        }
    ]
    
    for query_info in queries:
        print(f"\n📋 {query_info['name']}:")
        response = requests.get(f"{BASE_URL}/supervisor", params=query_info['params'])
        if response.status_code == 200:
            data = response.json()
            print(f"  Query: {data['query']}")
            print(f"  Workflow Trace: {data['workflow_trace']}")
            print(f"  Agents Used: {data['agents_consulted']}")
            print(f"  Confidence: {data['response']['confidence']}")

def main():
    """Main function"""
    print("🎯 LangGraph Supervisor Agent Examples")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Check if API is running
        health_response = requests.get(f"{BASE_URL}/health")
        if health_response.status_code != 200:
            print("❌ API is not running. Please start the server first.")
            return
        
        # Run examples
        example_supervisor_queries()
        compare_supervisor_vs_legacy()
        demonstrate_workflow_traces()
        
        print(f"\n✅ Examples completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Please ensure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
