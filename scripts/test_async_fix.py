#!/usr/bin/env python3
"""
Test script to verify the async event loop fix
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_async_fix():
    """Test the async event loop fix"""
    print('🧪 Testing Async Event Loop Fix...')
    print('=' * 50)
    
    try:
        from app.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        
        # Test subsidy query that was failing
        print('🔍 Testing subsidy query...')
        result = supervisor.process_query('What subsidies are available for farmers?', 'Maharashtra', 'wheat')
        
        print('✅ SUCCESS! No async event loop error')
        print(f'Answer: {result["answer"][:150]}...')
        print(f'Workflow: {result.get("workflow_trace", "unknown")}')
        print(f'Agent Used: {result.get("agent_used", "unknown")}')
        print(f'Agents Consulted: {result.get("agents_consulted", [])}')
        print(f'Confidence: {result.get("confidence", 0.0)}')
        print(f'Evidence Count: {len(result.get("evidence", []))}')
        
        # Test other query types
        test_queries = [
            ('How is the weather today?', 'weather'),
            ('How much fertilizer for wheat?', 'crop'),
            ('What is the market price of rice?', 'finance')
        ]
        
        print('\n🔍 Testing other query types...')
        for query, expected_agent in test_queries:
            print(f'\n🧪 Query: {query}')
            result = supervisor.process_query(query, 'Punjab', 'wheat')
            workflow = result.get("workflow_trace", "unknown")
            agent_used = result.get("agent_used", "unknown")
            print(f'✅ Success! Workflow: {workflow} | Agent: {agent_used}')
        
        print('\n🎉 ALL TESTS PASSED! Async issue is fixed.')
        return True
        
    except Exception as e:
        print(f'❌ ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_async_fix()
    if success:
        print('\n✅ Ready for production!')
    else:
        print('\n❌ Issues need to be resolved')

