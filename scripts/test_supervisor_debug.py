#!/usr/bin/env python3
"""
Test script for Supervisor Agent with debugging enabled
"""

import sys
import os
import requests
import json

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_supervisor_endpoint():
    """Test the supervisor endpoint directly"""
    print("🧪 Testing Supervisor Endpoint...")
    
    # Test cases
    test_cases = [
        {
            "name": "Weather Query",
            "text": "What's the weather like in Mumbai?",
            "location": "Mumbai",
            "crop": None
        },
        {
            "name": "Crop Management Query", 
            "text": "How much fertilizer should I use for wheat?",
            "location": "Punjab",
            "crop": "wheat"
        },
        {
            "name": "Finance Query",
            "text": "What are the current market prices for rice?",
            "location": "Karnataka",
            "crop": "rice"
        },
        {
            "name": "Policy Query",
            "text": "What government schemes are available for farmers?",
            "location": "Maharashtra",
            "crop": None
        },
        {
            "name": "Complex Multi-Agent Query",
            "text": "Should I plant wheat now given the weather and market conditions?",
            "location": "Haryana",
            "crop": "wheat"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}: {test_case['name']}")
        print(f"Query: {test_case['text']}")
        print(f"Location: {test_case['location']}")
        print(f"Crop: {test_case['crop']}")
        print(f"{'='*60}")
        
        try:
            # Make request to supervisor endpoint
            url = "http://127.0.0.1:8000/supervisor"
            params = {
                "text": test_case["text"],
                "location": test_case["location"],
                "crop": test_case["crop"]
            }
            
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ SUCCESS!")
                print(f"Workflow Trace: {result.get('workflow_trace', 'unknown')}")
                print(f"Agents Consulted: {result.get('agents_consulted', [])}")
                print(f"Answer: {result.get('response', {}).get('answer', 'No answer')[:200]}...")
                print(f"Confidence: {result.get('response', {}).get('confidence', 0.0)}")
            else:
                print(f"❌ FAILED: HTTP {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR: Make sure the API server is running on http://127.0.0.1:8000")
            print("Run: python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
            break
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")

def test_supervisor_direct():
    """Test the supervisor directly (if API is not running)"""
    print("🧪 Testing Supervisor Directly...")
    
    try:
        from app.supervisor import SupervisorAgent
        
        supervisor = SupervisorAgent()
        
        test_query = "What's the weather like in Delhi and should I plant wheat?"
        print(f"Query: {test_query}")
        
        result = supervisor.process_query(test_query, "Delhi", "wheat")
        
        print("✅ SUCCESS!")
        print(f"Workflow Trace: {result.get('workflow_trace', 'unknown')}")
        print(f"Agents Consulted: {result.get('agents_consulted', [])}")
        print(f"Answer: {result.get('answer', 'No answer')[:200]}...")
        print(f"Confidence: {result.get('confidence', 0.0)}")
        
    except ImportError as e:
        print(f"❌ IMPORT ERROR: {e}")
        print("Make sure you're running from the correct directory")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    print("🔍 SUPERVISOR DEBUG TEST")
    print("This script will test the supervisor agent with comprehensive debugging")
    
    # Try API endpoint first, then direct import
    try:
        test_supervisor_endpoint()
    except:
        print("\n🔄 API endpoint failed, trying direct import...")
        test_supervisor_direct()
    
    print("\n✅ Debug test completed!")
    print("Check the console output above for detailed workflow traces and agent execution logs.")
