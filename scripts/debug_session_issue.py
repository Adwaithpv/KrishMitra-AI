#!/usr/bin/env python3
"""
Debug the session issue between supervisor and finance agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.agents.finance_agent import FinanceAgent
import requests

def test_session_flow():
    """Test the complete session flow"""
    
    print("🔍 DEBUGGING SESSION ISSUE")
    print("=" * 40)
    
    # Step 1: Get session ID from supervisor
    print("📋 Step 1: Get session from supervisor")
    resp = requests.get('http://127.0.0.1:8000/supervisor', params={
        'text': 'I need help optimizing my spendings and improving profits',
        'location': 'Karnataka'
    })
    
    if resp.status_code == 200:
        data = resp.json()['response']
        session_id = data.get('session_id')
        agents = data.get('agents_consulted', [])
        answer = data.get('answer', '')
        
        print(f"✅ Supervisor response:")
        print(f"   Session ID: {session_id}")
        print(f"   Agents: {agents}")
        print(f"   Answer: {answer[:100]}...")
        
        # Step 2: Test finance agent directly with same session ID
        print(f"\n📋 Step 2: Test finance agent with session ID: {session_id}")
        
        finance_agent = FinanceAgent()
        fa_response = finance_agent.process_query(
            'I need help optimizing my spendings and improving profits',
            'Karnataka', 
            'wheat', 
            session_id
        )
        
        if isinstance(fa_response, dict):
            result = fa_response.get('result', {})
            advice = result.get('advice', 'No advice')
            print(f"✅ Finance agent response:")
            print(f"   Advice: {advice[:100]}...")
            
            if 'Error: Session not found' in advice:
                print("❌ Still getting session error!")
                
                # Step 3: Check if session exists in finance session manager
                print(f"\n📋 Step 3: Check session in finance session manager")
                from app.finance_session import finance_session_manager
                
                session_data = finance_session_manager.get_session_data(session_id)
                if session_data:
                    print(f"✅ Session exists in manager")
                    print(f"   Data: {session_data}")
                else:
                    print(f"❌ Session NOT found in manager")
                    print(f"   Available sessions: {list(finance_session_manager.sessions.keys())}")
                    
                    # Try creating the session manually
                    print(f"\n📋 Step 4: Try creating session manually")
                    created_id = finance_session_manager.get_or_create_session(session_id)
                    print(f"   Created session ID: {created_id}")
                    
                    # Test again
                    fa_response2 = finance_agent.process_query(
                        'I need help optimizing my spendings and improving profits',
                        'Karnataka', 
                        'wheat', 
                        created_id
                    )
                    
                    if isinstance(fa_response2, dict):
                        result2 = fa_response2.get('result', {})
                        advice2 = result2.get('advice', 'No advice')
                        print(f"✅ After manual creation:")
                        print(f"   Advice: {advice2[:100]}...")
        else:
            print(f"❌ Unexpected finance agent response type: {type(fa_response)}")
    else:
        print(f"❌ Supervisor request failed: {resp.status_code}")

if __name__ == "__main__":
    test_session_flow()
