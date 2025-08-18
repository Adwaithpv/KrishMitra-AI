#!/usr/bin/env python3
"""
Debug finance agent directly to see what it returns
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.agents.finance_agent import FinanceAgent

def test_finance_agent_direct():
    """Test finance agent directly to see what it returns"""
    
    print("🔍 DEBUGGING FINANCE AGENT DIRECTLY")
    print("=" * 50)
    
    # Initialize finance agent
    finance_agent = FinanceAgent()
    
    # Test the exact query
    query = "I need help optimizing my spendings and improving profits"
    location = "Karnataka"
    crop = "wheat"
    session_id = "debug_session"
    
    print(f"Query: '{query}'")
    print(f"Location: {location}")
    print(f"Crop: {crop}")
    print(f"Session ID: {session_id}")
    print()
    
    # Process query
    try:
        response = finance_agent.process_query(query, location, crop, session_id)
        
        print("📊 FINANCE AGENT RESPONSE:")
        print(f"   Type: {type(response)}")
        print(f"   Keys: {list(response.keys()) if isinstance(response, dict) else 'Not a dict'}")
        print()
        
        if isinstance(response, dict):
            # Check result structure
            result = response.get('result', {})
            if result:
                print("📋 RESULT STRUCTURE:")
                for key, value in result.items():
                    if key == 'advice' and isinstance(value, str):
                        print(f"   {key}: {value[:100]}...")
                    else:
                        print(f"   {key}: {value}")
                print()
            
            # Check form data if present
            if 'form_data' in result:
                print("📝 FORM DATA PRESENT:")
                form_data = result['form_data']
                print(f"   Form type: {form_data.get('form_type', 'Unknown')}")
                print(f"   Title: {form_data.get('title', 'No title')}")
                print(f"   Fields count: {len(form_data.get('fields', []))}")
                print()
            
            # Show full response keys
            print("🔍 FULL RESPONSE STRUCTURE:")
            for key, value in response.items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"   {key}: {value[:100]}...")
                else:
                    print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_different_queries():
    """Test different financial queries"""
    
    print("\n🧪 TESTING DIFFERENT FINANCE QUERIES")
    print("=" * 40)
    
    finance_agent = FinanceAgent()
    
    queries = [
        "I need help optimizing my spendings and improving profits",
        "How can I reduce my farming costs?",
        "I want to improve my farm profitability",
        "Help me with financial planning for my farm"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nTest {i}: '{query}'")
        
        try:
            response = finance_agent.process_query(query, "Karnataka", "wheat", f"test_{i}")
            
            if isinstance(response, dict):
                result = response.get('result', {})
                if 'form_data' in result:
                    print("   📝 Response: Finance form generated")
                    form_title = result['form_data'].get('title', 'Form')
                    print(f"   Form: {form_title}")
                elif 'advice' in result:
                    advice = result['advice']
                    print(f"   💡 Response: {advice[:80]}...")
                else:
                    print(f"   📊 Response keys: {list(result.keys())}")
            else:
                print(f"   ⚠️ Unexpected response type: {type(response)}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main debug function"""
    print("🚀 FINANCE AGENT DIRECT DEBUG")
    print("=" * 50)
    
    try:
        test_finance_agent_direct()
        test_different_queries()
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
