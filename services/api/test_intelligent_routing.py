#!/usr/bin/env python3
"""
Test script for the new intelligent agent routing system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from agent_router import AgentRouter
from coordinator import Coordinator

def test_intelligent_routing():
    """Test the new intelligent routing system"""
    
    print("🧠 Testing Intelligent Agent Routing System")
    print("=" * 60)
    
    router = AgentRouter()
    coordinator = Coordinator()
    
    # Comprehensive test cases with expected agent mappings
    test_cases = [
        # POLICY AGENT TESTS
        {
            "query": "What subsidies can I avail?",
            "expected": ["policy"],
            "category": "POLICY - Subsidies"
        },
        {
            "query": "How to apply for PM-KISAN scheme?",
            "expected": ["policy"],
            "category": "POLICY - Government Schemes"
        },
        {
            "query": "I need a loan for farming",
            "expected": ["policy"],
            "category": "POLICY - Agricultural Loans"
        },
        {
            "query": "Kisan Credit Card eligibility criteria",
            "expected": ["policy"],
            "category": "POLICY - Credit Schemes"
        },
        {
            "query": "Crop insurance application process",
            "expected": ["policy"],
            "category": "POLICY - Insurance"
        },
        {
            "query": "Organic farming subsidies in Tamil Nadu",
            "expected": ["policy"],
            "category": "POLICY - State Subsidies"
        },
        {
            "query": "Government assistance for farmers",
            "expected": ["policy"],
            "category": "POLICY - Government Assistance"
        },
        
        # FINANCE AGENT TESTS
        {
            "query": "Current wheat market price",
            "expected": ["finance"],
            "category": "FINANCE - Market Prices"
        },
        {
            "query": "MSP for paddy this season",
            "expected": ["finance"],
            "category": "FINANCE - MSP"
        },
        {
            "query": "Mandi rates for cotton today",
            "expected": ["finance"],
            "category": "FINANCE - Commodity Rates"
        },
        {
            "query": "Trading prices for sugarcane",
            "expected": ["finance"],
            "category": "FINANCE - Trading"
        },
        
        # WEATHER AGENT TESTS
        {
            "query": "Weather forecast for next week",
            "expected": ["weather"],
            "category": "WEATHER - Forecast"
        },
        {
            "query": "When should I irrigate my crops?",
            "expected": ["weather"],
            "category": "WEATHER - Irrigation Timing"
        },
        {
            "query": "Rainfall predictions for farming",
            "expected": ["weather"],
            "category": "WEATHER - Rainfall"
        },
        
        # CROP AGENT TESTS
        {
            "query": "NPK fertilizer recommendations for wheat",
            "expected": ["crop"],
            "category": "CROP - Fertilizers"
        },
        {
            "query": "Pest control methods for cotton",
            "expected": ["crop"],
            "category": "CROP - Pest Management"
        },
        {
            "query": "Disease management in tomatoes",
            "expected": ["crop"],
            "category": "CROP - Disease Control"
        },
        
        # MIXED QUERIES
        {
            "query": "Best time to plant based on weather",
            "expected": ["weather", "crop"],
            "category": "MIXED - Weather + Crop"
        }
    ]
    
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        query = test_case["query"]
        expected = test_case["expected"]
        category = test_case["category"]
        
        # Test router directly
        actual = router.route_query(query)
        
        # Check if all expected agents are in actual results
        match = all(agent in actual for agent in expected)
        
        # Also check that no unwanted agents are included for single-agent expectations
        if len(expected) == 1 and len(actual) > 1:
            # For single-agent expectations, prefer exact match
            match = actual == expected
        
        status = "✅ PASS" if match else "❌ FAIL"
        
        if match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {category}")
        print(f"      | Query: '{query}'")
        print(f"      | Expected: {expected}")
        print(f"      | Actual: {actual}")
        
        # Show routing explanation for failed cases
        if not match:
            explanation = router.get_routing_explanation(query, actual)
            print(f"      | Explanation: {explanation.split('Selected agents:')[1].strip()}")
        
        print()
    
    # Test full coordinator integration
    print("🔗 Testing Coordinator Integration")
    print("-" * 40)
    
    # Test a policy query through the full coordinator
    try:
        response = coordinator.process_query("What subsidies can I avail for organic farming?")
        agents_consulted = response.get('agents_consulted', [])
        confidence = response.get('confidence', 0.0)
        
        print(f"✅ Coordinator integration working")
        print(f"   Agents consulted: {agents_consulted}")
        print(f"   Confidence: {confidence}")
        print(f"   Response preview: {response.get('answer', '')[:100]}...")
        
    except Exception as e:
        print(f"❌ Coordinator integration failed: {e}")
        failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Intelligent routing is working perfectly.")
    else:
        print(f"💥 {failed} tests failed. Review the routing logic.")
    
    return failed == 0

if __name__ == "__main__":
    test_intelligent_routing()
