#!/usr/bin/env python3
"""
Test script for Phase 6: Advanced Features & Production Readiness
Tests analytics, real-time data, and new API endpoints.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test API health"""
    print("🔍 Testing API health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analytics_endpoints():
    """Test analytics endpoints"""
    print("\n📊 Testing Analytics Endpoints...")
    
    # Test performance stats
    try:
        response = requests.get(f"{BASE_URL}/analytics/performance?hours=24")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Performance stats: {data.get('total_queries', 0)} queries")
        else:
            print(f"❌ Performance stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Performance stats error: {e}")
    
    # Test user insights
    try:
        response = requests.get(f"{BASE_URL}/analytics/insights?hours=24")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User insights retrieved")
        else:
            print(f"❌ User insights failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User insights error: {e}")
    
    # Test analytics export
    try:
        response = requests.get(f"{BASE_URL}/analytics/export?format=json")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics export: {data.get('file', 'unknown')}")
        else:
            print(f"❌ Analytics export failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analytics export error: {e}")

def test_realtime_endpoints():
    """Test real-time data endpoints"""
    print("\n🌤️ Testing Real-time Data Endpoints...")
    
    # Test weather data
    try:
        response = requests.get(f"{BASE_URL}/realtime/weather?location=Punjab")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Weather data for Punjab: {data.get('temperature', 'N/A')}°C")
        else:
            print(f"❌ Weather data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Weather data error: {e}")
    
    # Test market data
    try:
        response = requests.get(f"{BASE_URL}/realtime/market?crop=wheat")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Market data for wheat: {len(data)} locations")
        else:
            print(f"❌ Market data failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Market data error: {e}")
    
    # Test cache update
    try:
        response = requests.post(f"{BASE_URL}/realtime/update-cache")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cache update: {data.get('message', 'success')}")
        else:
            print(f"❌ Cache update failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cache update error: {e}")

def test_enhanced_queries():
    """Test queries with real-time data integration"""
    print("\n🚀 Testing Enhanced Queries with Real-time Data...")
    
    test_queries = [
        {
            "text": "What's the weather like for wheat farming in Punjab?",
            "location": "Punjab",
            "crop": "wheat"
        },
        {
            "text": "What are the current market prices for rice?",
            "location": "Maharashtra",
            "crop": "rice"
        },
        {
            "text": "Should I plant cotton now considering the weather and market conditions?",
            "location": "Maharashtra",
            "crop": "cotton"
        }
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test Query {i}: {query['text']}")
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/query", params=query)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response time: {data.get('response_time', response_time):.3f}s")
                print(f"✅ Agent used: {data.get('agent_used', 'unknown')}")
                print(f"✅ Confidence: {data.get('confidence', 0):.3f}")
                print(f"✅ Real-time insights: {data.get('realtime_insights', 0)}")
                
                # Show first 200 chars of answer
                answer = data.get('answer', '')
                print(f"📄 Answer preview: {answer[:200]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Query error: {e}")

def test_agent_system():
    """Test the enhanced agent system"""
    print("\n🤖 Testing Enhanced Agent System...")
    
    agent_tests = [
        ("weather", "How's the rainfall forecast for next week?", "Punjab", "wheat"),
        ("crop", "What fertilizer should I use for wheat?", "Maharashtra", "wheat"),
        ("finance", "What are the current wheat prices?", "Punjab", "wheat"),
        ("policy", "What government schemes are available for farmers?", "Maharashtra", "rice")
    ]
    
    for agent_type, query, location, crop in agent_tests:
        print(f"\n🔍 Testing {agent_type} agent...")
        try:
            response = requests.get(f"{BASE_URL}/agents", params={
                "text": query,
                "location": location,
                "crop": crop
            })
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {agent_type} agent: {data.get('agent_used', 'unknown')}")
                print(f"✅ Confidence: {data.get('confidence', 0):.3f}")
            else:
                print(f"❌ {agent_type} agent failed: {response.status_code}")
        except Exception as e:
            print(f"❌ {agent_type} agent error: {e}")

def test_performance():
    """Test system performance"""
    print("\n⚡ Testing System Performance...")
    
    # Test multiple concurrent queries
    import concurrent.futures
    
    def make_query(query_data):
        try:
            start_time = time.time()
            response = requests.get(f"{BASE_URL}/query", params=query_data, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "response_time": response_time,
                    "api_response_time": data.get('response_time', 0),
                    "confidence": data.get('confidence', 0)
                }
            else:
                return {"success": False, "error": response.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Prepare test queries
    test_queries = [
        {"text": "wheat farming advice", "location": "Punjab", "crop": "wheat"},
        {"text": "rice market prices", "location": "Maharashtra", "crop": "rice"},
        {"text": "weather forecast", "location": "Karnataka", "crop": "cotton"},
        {"text": "government subsidies", "location": "Tamil Nadu", "crop": "sugarcane"},
        {"text": "pest control methods", "location": "Punjab", "crop": "wheat"}
    ]
    
    print("🔄 Running concurrent performance test...")
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_query, query) for query in test_queries]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    total_time = time.time() - start_time
    
    # Analyze results
    successful_queries = [r for r in results if r["success"]]
    failed_queries = [r for r in results if not r["success"]]
    
    if successful_queries:
        avg_response_time = sum(r["response_time"] for r in successful_queries) / len(successful_queries)
        avg_api_response_time = sum(r["api_response_time"] for r in successful_queries) / len(successful_queries)
        avg_confidence = sum(r["confidence"] for r in successful_queries) / len(successful_queries)
        
        print(f"✅ Performance Results:")
        print(f"   Total time: {total_time:.3f}s")
        print(f"   Successful queries: {len(successful_queries)}/5")
        print(f"   Average response time: {avg_response_time:.3f}s")
        print(f"   Average API response time: {avg_api_response_time:.3f}s")
        print(f"   Average confidence: {avg_confidence:.3f}")
    
    if failed_queries:
        print(f"❌ Failed queries: {len(failed_queries)}")
        for failure in failed_queries:
            print(f"   Error: {failure.get('error', 'unknown')}")

def main():
    """Run all Phase 6 tests"""
    print("🚀 Phase 6: Advanced Features & Production Readiness Test")
    print("=" * 60)
    
    # Check if API is running
    if not test_health():
        print("❌ API is not running. Please start the server first.")
        return
    
    # Run all tests
    test_analytics_endpoints()
    test_realtime_endpoints()
    test_enhanced_queries()
    test_agent_system()
    test_performance()
    
    print("\n" + "=" * 60)
    print("🎉 Phase 6 Testing Complete!")
    print("\n📊 Next Steps:")
    print("1. Check analytics dashboard at /analytics/performance")
    print("2. Monitor real-time data at /realtime/weather and /realtime/market")
    print("3. Deploy with docker-compose.prod.yml for production")
    print("4. Set up monitoring with Prometheus and Grafana")

if __name__ == "__main__":
    main()

