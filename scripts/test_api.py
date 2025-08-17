#!/usr/bin/env python3
"""
Test script for Agri Advisor API
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_ingest():
    """Test data ingestion"""
    print("Testing data ingestion...")
    response = requests.post(f"{BASE_URL}/ingest")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_queries():
    """Test various queries"""
    test_cases = [
        {
            "text": "irrigation for wheat",
            "location": "Punjab",
            "crop": "wheat",
            "description": "Wheat irrigation query"
        },
        {
            "text": "fertilizer application for rice",
            "location": "Karnataka",
            "crop": "rice",
            "description": "Rice fertilizer query"
        },
        {
            "text": "pest control in cotton",
            "location": "Gujarat",
            "crop": "cotton",
            "description": "Cotton pest control query"
        },
        {
            "text": "weather alert",
            "location": "Karnataka",
            "crop": None,
            "description": "Weather alert query"
        },
        {
            "text": "market prices for wheat",
            "location": "Punjab",
            "crop": "wheat",
            "description": "Market prices query"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Query: {test_case['text']}")
        
        params = {"text": test_case["text"]}
        if test_case["location"]:
            params["location"] = test_case["location"]
        if test_case["crop"]:
            params["crop"] = test_case["crop"]
        
        response = requests.get(f"{BASE_URL}/query", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Confidence: {result['confidence']}")
            print(f"Evidence count: {len(result['evidence'])}")
        else:
            print(f"Error: {response.text}")
        
        print("-" * 50)
        time.sleep(1)  # Rate limiting

def main():
    print("Agri Advisor API Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_ingest()
        test_queries()
        
        print("All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to API. Make sure it's running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
