#!/usr/bin/env python3
"""
Test script for the new session-based finance form system
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_finance_form_workflow():
    """Test the complete finance form workflow"""
    
    print("🧪 Testing Finance Form Workflow")
    print("=" * 60)
    
    # Step 1: Initial finance query (should trigger form)
    print("\n📋 Step 1: Initial Finance Query")
    print("Query: 'I need help optimizing my farm finances'")
    
    response1 = make_query("I need help optimizing my farm finances")
    if response1:
        print("✅ Initial query successful")
        session_id = response1.get("session_id")
        print(f"🔑 Session ID: {session_id}")
        
        # Check if form was generated
        form_data = response1.get("result", {}).get("form_data")
        if form_data:
            print(f"📊 Form generated: {form_data['completion_percentage']}% complete")
            print(f"📝 Missing critical fields: {form_data['missing_critical_fields']}")
        else:
            print("ℹ️ No form data in response")
    else:
        print("❌ Initial query failed")
        return
    
    # Step 2: Provide some information
    print("\n📋 Step 2: Providing Financial Information")
    print("Query: 'My farm is 5 acres and I spend 30000 on fertilizers annually'")
    
    response2 = make_query("My farm is 5 acres and I spend 30000 on fertilizers annually")
    if response2:
        print("✅ Information update successful")
        form_data = response2.get("result", {}).get("form_data")
        if form_data:
            print(f"📊 Form updated: {form_data['completion_percentage']}% complete")
            print(f"📝 Missing critical fields: {form_data['missing_critical_fields']}")
            
            # Show what information was captured
            current_data = form_data.get("current_data", {})
            if current_data:
                print("📋 Information captured:")
                for field, value in current_data.items():
                    print(f"   • {field}: {value}")
        else:
            print("ℹ️ No form data in response")
    else:
        print("❌ Information update failed")
        return
    
    # Step 3: Provide more information
    print("\n📋 Step 3: Providing More Information")
    print("Query: 'I also spend 25000 on water and produce 120 quintals per year'")
    
    response3 = make_query("I also spend 25000 on water and produce 120 quintals per year")
    if response3:
        print("✅ Additional information successful")
        form_data = response3.get("result", {}).get("form_data")
        if form_data:
            print(f"📊 Form updated: {form_data['completion_percentage']}% complete")
            print(f"📝 Missing critical fields: {form_data['missing_critical_fields']}")
            
            # Check if form is now complete
            if form_data['missing_critical_fields'] == 0:
                print("🎉 Critical information complete!")
        else:
            print("📊 Form may be complete - no form data returned")
    else:
        print("❌ Additional information failed")
        return
    
    # Step 4: Ask for advice again (should now provide comprehensive analysis)
    print("\n📋 Step 4: Requesting Comprehensive Advice")
    print("Query: 'Now give me financial optimization advice'")
    
    response4 = make_query("Now give me financial optimization advice")
    if response4:
        print("✅ Comprehensive advice successful")
        
        # Check if we got detailed advice instead of form
        form_data = response4.get("result", {}).get("form_data")
        if form_data:
            print("⚠️ Still showing form - may need more information")
        else:
            print("🎯 Received comprehensive financial advice!")
            answer = response4.get("result", {}).get("advice", "")
            print(f"📝 Advice length: {len(answer)} characters")
    else:
        print("❌ Comprehensive advice failed")
    
    print("\n✅ Finance Form Workflow Test Complete!")

def make_query(query_text):
    """Make a query to the finance agent"""
    try:
        params = {
            'text': query_text,
            'location': 'Karnataka',
            'crop': 'wheat'
        }
        
        response = requests.get(f"{BASE_URL}/supervisor", params=params, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if finance agent was used
            agents_consulted = data.get('agents_consulted', [])
            if any('finance' in str(agent) for agent in agents_consulted):
                print(f"   🤖 Finance agent consulted: {agents_consulted}")
                return data.get('response', {})
            else:
                print(f"   ⚠️ Different agent used: {agents_consulted}")
                return None
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Request failed: {str(e)}")
        return None

def test_session_persistence():
    """Test that session data persists across queries"""
    print("\n🔄 Testing Session Persistence")
    print("=" * 40)
    
    # First query with financial data
    print("Query 1: 'My farm is 3 acres'")
    response1 = make_query("My farm is 3 acres, help me with finances")
    
    if response1:
        session_id = response1.get("session_id")
        print(f"🔑 Session ID: {session_id}")
    
    time.sleep(1)
    
    # Second query - should remember the farm size
    print("\nQuery 2: 'I also spend 20000 on fertilizers'")
    response2 = make_query("I also spend 20000 on fertilizers annually")
    
    if response2:
        form_data = response2.get("result", {}).get("form_data")
        if form_data:
            current_data = form_data.get("current_data", {})
            if "land_size_acres" in current_data and "fertilizer_cost" in current_data:
                print("✅ Session persistence working - both values remembered!")
                print(f"   Farm size: {current_data['land_size_acres']}")
                print(f"   Fertilizer cost: {current_data['fertilizer_cost']}")
            else:
                print("❌ Session persistence issue - data not accumulated")
        else:
            print("ℹ️ No form data to check persistence")

def main():
    """Main test function"""
    print("🚀 Finance Form Session Management Test")
    print("=" * 60)
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ API is not healthy. Please start the server first.")
            return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print("✅ API is healthy. Starting finance form tests...\n")
    
    # Test the complete workflow
    test_finance_form_workflow()
    
    # Test session persistence
    test_session_persistence()
    
    print(f"\n🏁 All tests completed!")

if __name__ == "__main__":
    main()
