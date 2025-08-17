#!/usr/bin/env python3
"""
Test script to simulate calling supervisor from async context (like FastAPI)
"""

import asyncio
import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

async def test_in_async_context():
    """Test supervisor when called from within an async function"""
    print('🧪 Testing Supervisor in Async Context (like FastAPI)...')
    print('=' * 60)
    
    try:
        from app.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        
        # This simulates what happens when FastAPI calls the supervisor
        print('🔍 Testing subsidy query in async context...')
        result = supervisor.process_query('What subsidies are available for farmers?', 'Maharashtra', 'wheat')
        
        print('✅ SUCCESS! No asyncio.run() error in async context')
        print(f'Answer: {result["answer"][:150]}...')
        print(f'Workflow: {result.get("workflow_trace", "unknown")}')
        print(f'Agent Used: {result.get("agent_used", "unknown")}')
        print(f'Agents Consulted: {result.get("agents_consulted", [])}')
        
        # Test other queries
        test_queries = [
            'What is the weather forecast?',
            'How to apply fertilizer?',
            'What are the market prices?'
        ]
        
        print('\n🔍 Testing multiple queries in sequence...')
        for i, query in enumerate(test_queries, 1):
            print(f'\n🧪 Query {i}: {query}')
            result = supervisor.process_query(query, 'Punjab', 'wheat')
            workflow = result.get("workflow_trace", "unknown")
            print(f'✅ Success! Workflow: {workflow}')
        
        print('\n🎉 ALL ASYNC CONTEXT TESTS PASSED!')
        return True
        
    except Exception as e:
        print(f'❌ ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the async test"""
    print('🚀 Starting async context test...')
    success = asyncio.run(test_in_async_context())
    
    if success:
        print('\n✅ Ready for FastAPI production!')
        print('🎯 The async event loop issue is completely resolved.')
    else:
        print('\n❌ Issues still need to be resolved')

if __name__ == "__main__":
    main()

