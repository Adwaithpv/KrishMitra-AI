#!/usr/bin/env python3
"""
Test script to verify LangGraph supervisor agent routing
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_supervisor_routing():
    """Test supervisor agent routing for different query types"""
    
    try:
        from app.supervisor import SupervisorAgent
    except ImportError:
        print("❌ Error: Could not import SupervisorAgent")
        print("Make sure you're running from the correct directory and dependencies are installed")
        return
    
    print('🔧 Testing LangGraph Supervisor Agent Routing...')
    print('=' * 70)

    # Initialize supervisor
    print("🔧 Initializing SupervisorAgent...")
    supervisor = SupervisorAgent()
    print("✅ SupervisorAgent initialized successfully")

    # Test cases for different agent routing
    test_cases = [
        {
            'name': 'Policy/Subsidy Query',
            'query': 'What government subsidies are available for farmers in Maharashtra?',
            'location': 'Maharashtra',
            'crop': 'wheat',
            'expected_agent': 'policy'
        },
        {
            'name': 'Weather Query',
            'query': 'Will it rain tomorrow in Punjab?',
            'location': 'Punjab', 
            'crop': 'rice',
            'expected_agent': 'weather'
        },
        {
            'name': 'Crop Management Query',
            'query': 'How much fertilizer should I use for my wheat crop?',
            'location': 'Haryana',
            'crop': 'wheat',
            'expected_agent': 'crop'
        },
        {
            'name': 'Finance/Market Query',
            'query': 'What are the current market prices for rice?',
            'location': 'Karnataka',
            'crop': 'rice', 
            'expected_agent': 'finance'
        },
        {
            'name': 'Multi-Agent Query',
            'query': 'Should I plant wheat now considering weather and market conditions?',
            'location': 'Delhi',
            'crop': 'wheat',
            'expected_agent': 'multiple'
        }
    ]

    routing_results = []

    for i, test in enumerate(test_cases, 1):
        print(f'\n🧪 TEST {i}: {test["name"]}')
        print(f'Query: {test["query"]}')
        print(f'Expected Agent(s): {test["expected_agent"]}')
        print('-' * 50)
        
        try:
            print("🔄 Processing query...")
            result = supervisor.process_query(test['query'], test['location'], test['crop'])
            
            # Extract results
            agents_consulted = result.get('agents_consulted', [])
            agent_used = result.get('agent_used', 'unknown')
            workflow_trace = result.get('workflow_trace', 'unknown')
            answer = result.get('answer', 'No answer')
            confidence = result.get('confidence', 0.0)
            
            print(f'✅ SUCCESS!')
            print(f'🤖 Agent Used: {agent_used}')
            print(f'📋 Agents Consulted: {agents_consulted}')
            print(f'🔄 Workflow Trace: {workflow_trace}')
            print(f'📊 Confidence: {confidence:.3f}')
            print(f'💬 Answer: {answer[:150]}...')
            
            # Check if correct agent was consulted
            routing_success = False
            if test['expected_agent'] == 'multiple':
                if len(agents_consulted) > 1:
                    print('✅ ROUTING SUCCESS: Multiple agents consulted as expected')
                    routing_success = True
                else:
                    print('⚠️ ROUTING ISSUE: Expected multiple agents, got single agent')
            elif test['expected_agent'] in [agent.lower() for agent in agents_consulted]:
                print(f'✅ ROUTING SUCCESS: {test["expected_agent"]} agent was consulted')
                routing_success = True
            else:
                print(f'❌ ROUTING ISSUE: Expected {test["expected_agent"]}, got {agents_consulted}')
            
            routing_results.append({
                'test': test['name'],
                'expected': test['expected_agent'],
                'actual': agents_consulted,
                'success': routing_success,
                'workflow_trace': workflow_trace
            })
                
        except Exception as e:
            print(f'❌ ERROR: {str(e)}')
            routing_results.append({
                'test': test['name'],
                'expected': test['expected_agent'],
                'actual': ['ERROR'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f'\n' + '=' * 70)
    print('🎯 SUPERVISOR ROUTING TEST SUMMARY')
    print('=' * 70)
    
    successful_tests = sum(1 for r in routing_results if r['success'])
    total_tests = len(routing_results)
    
    print(f"📊 Overall Success Rate: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    
    for result in routing_results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['test']}: Expected {result['expected']}, Got {result['actual']}")
    
    print('\n🔍 Key Findings:')
    if successful_tests == total_tests:
        print("✅ All agent routing tests passed!")
        print("✅ LangGraph supervisor is correctly routing queries to appropriate agents")
    else:
        print(f"⚠️ {total_tests - successful_tests} routing issues detected")
        print("🔧 Consider reviewing the query analysis logic in the supervisor")
    
    return routing_results

if __name__ == "__main__":
    test_supervisor_routing()
