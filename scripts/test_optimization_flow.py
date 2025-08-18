#!/usr/bin/env python3
"""
Test the complete optimization flow with user providing data
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.agents.finance_agent import FinanceAgent

def test_optimization_flow():
    """Test the complete flow from query to optimization advice"""
    
    print("🔬 TESTING COMPLETE OPTIMIZATION FLOW")
    print("=" * 50)
    
    finance_agent = FinanceAgent()
    session_id = "test_optimization"
    
    # Step 1: Initial optimization query
    print("📋 Step 1: Initial Optimization Request")
    query1 = "I need help optimizing my spendings and improving profits"
    
    response1 = finance_agent.process_query(query1, "Karnataka", "wheat", session_id)
    
    print(f"Query: '{query1}'")
    print(f"Response type: {type(response1)}")
    
    if isinstance(response1, dict):
        result1 = response1.get('result', {})
        if 'form_data' in result1:
            print("✅ Step 1: Finance form generated (asking for data)")
            print(f"   Form completion: {result1['form_data'].get('completion_percentage', 0)}%")
        else:
            print("❓ Step 1: Unexpected response format")
    
    print()
    
    # Step 2: User provides financial data
    print("📋 Step 2: User Provides Financial Information")
    query2 = "My farm is 5 acres, I spend ₹30,000 on fertilizers annually, ₹25,000 on water, and produce 120 quintals per year"
    
    response2 = finance_agent.process_query(query2, "Karnataka", "wheat", session_id)
    
    print(f"Query: '{query2}'")
    
    if isinstance(response2, dict):
        result2 = response2.get('result', {})
        if 'form_data' in result2:
            completion = result2['form_data'].get('completion_percentage', 0)
            print(f"✅ Step 2: Data captured, form {completion}% complete")
            if completion < 100:
                missing = result2['form_data'].get('missing_critical_fields', 0)
                print(f"   Still need: {missing} critical fields")
            else:
                print("🎉 Step 2: All data collected!")
        elif 'advice' in result2:
            advice = result2['advice']
            print(f"🎯 Step 2: Optimization advice provided!")
            print(f"   Advice length: {len(advice)} characters")
            print(f"   Preview: {advice[:100]}...")
    
    print()
    
    # Step 3: Request final optimization advice
    print("📋 Step 3: Request Comprehensive Optimization")
    query3 = "Now give me comprehensive financial optimization advice"
    
    response3 = finance_agent.process_query(query3, "Karnataka", "wheat", session_id)
    
    print(f"Query: '{query3}'")
    
    if isinstance(response3, dict):
        result3 = response3.get('result', {})
        if 'advice' in result3:
            advice = result3['advice']
            print(f"🎉 Step 3: Final optimization advice provided!")
            print(f"   Advice length: {len(advice)} characters")
            
            # Check if it contains optimization content
            if any(term in advice.lower() for term in ['optimize', 'cost', 'profit', 'reduce', 'improve']):
                print("✅ Contains optimization content")
            else:
                print("⚠️ May not contain optimization content")
            
            print(f"   Preview: {advice[:150]}...")
        else:
            print("❓ Step 3: No advice in response")

def test_immediate_optimization():
    """Test what happens when we provide optimization without sufficient data"""
    
    print("\n🚀 TESTING IMMEDIATE OPTIMIZATION (No Data)")
    print("=" * 50)
    
    finance_agent = FinanceAgent()
    
    # Test if we can bypass the form by modifying the query
    queries = [
        "Give me general tips to optimize my farm spendings and improve profits",
        "I want to reduce my farming costs, what are some general strategies?",
        "How can I improve my farm profitability without sharing specific data?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nTest {i}: '{query}'")
        
        response = finance_agent.process_query(query, "Karnataka", "wheat", f"immediate_{i}")
        
        if isinstance(response, dict):
            result = response.get('result', {})
            if 'form_data' in result:
                print("📝 Response: Form generated (asking for data)")
            elif 'advice' in result:
                advice = result['advice']
                print(f"💡 Response: Direct advice provided!")
                print(f"   Length: {len(advice)} chars")
                print(f"   Preview: {advice[:80]}...")

def main():
    """Main test function"""
    print("🧪 FINANCE AGENT OPTIMIZATION FLOW TEST")
    print("=" * 60)
    
    test_optimization_flow()
    test_immediate_optimization()
    
    print(f"\n🏁 Test completed!")

if __name__ == "__main__":
    main()
