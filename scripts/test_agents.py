#!/usr/bin/env python3
"""
Test script for Agri Advisor Agents
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_agents():
    """Test agent responses"""
    print("Testing Agent System")
    print("=" * 50)
    
    test_cases = [
        {
            "text": "irrigation for wheat",
            "location": "Punjab",
            "crop": "wheat",
            "description": "Wheat irrigation query"
        },
        {
            "text": "heavy rainfall alert",
            "location": "Karnataka",
            "crop": "rice",
            "description": "Weather alert query"
        },
        {
            "text": "fertilizer application for pulses",
            "location": "Madhya Pradesh",
            "crop": "pulses",
            "description": "Fertilizer query"
        },
        {
            "text": "pest control in cotton",
            "location": "Gujarat",
            "crop": "cotton",
            "description": "Pest control query"
        },
        {
            "text": "drought conditions",
            "location": "Maharashtra",
            "crop": None,
            "description": "Drought query"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['description']}")
        print(f"Query: {test_case['text']}")
        
        params = {"text": test_case["text"]}
        if test_case["location"]:
            params["location"] = test_case["location"]
        if test_case["crop"]:
            params["crop"] = test_case["crop"]
        
        try:
            response = requests.get(f"{BASE_URL}/agents", params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Answer: {result['answer']}")
                print(f"Confidence: {result['confidence']}")
                print(f"Agents consulted: {result.get('agents_consulted', [])}")
                print(f"Evidence count: {len(result.get('evidence', []))}")
            else:
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("Error: Could not connect to API. Make sure it's running on http://127.0.0.1:8000")
            break
        except Exception as e:
            print(f"Error: {e}")
        
        print("-" * 50)
        time.sleep(1)  # Rate limiting

def test_coordinator_vs_rag():
    """Compare coordinator vs RAG responses"""
    print("\n\nComparing Coordinator vs RAG")
    print("=" * 50)
    
    test_query = "irrigation for wheat in Punjab"
    
    print(f"Query: {test_query}")
    
    # Test coordinator
    try:
        response = requests.get(f"{BASE_URL}/agents", params={"text": test_query, "location": "Punjab", "crop": "wheat"})
        if response.status_code == 200:
            coordinator_result = response.json()
            print(f"\nCoordinator Response:")
            print(f"Answer: {coordinator_result['answer']}")
            print(f"Confidence: {coordinator_result['confidence']}")
            print(f"Agents: {coordinator_result.get('agents_consulted', [])}")
    except Exception as e:
        print(f"Coordinator error: {e}")
    
    # Test RAG
    try:
        response = requests.get(f"{BASE_URL}/query", params={"text": test_query, "location": "Punjab", "crop": "wheat"})
        if response.status_code == 200:
            rag_result = response.json()
            print(f"\nRAG Response:")
            print(f"Answer: {rag_result['answer']}")
            print(f"Confidence: {rag_result['confidence']}")
    except Exception as e:
        print(f"RAG error: {e}")

def main():
    print("Agri Advisor Agent Test Suite")
    print("=" * 50)
    
    try:
        test_agents()
        test_coordinator_vs_rag()
        
        print("\nAll tests completed!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
