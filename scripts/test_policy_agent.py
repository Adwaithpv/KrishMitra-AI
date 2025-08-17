#!/usr/bin/env python3
"""
Test script to verify Policy Agent functionality
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_policy_agent():
    """Test the policy agent directly"""
    
    try:
        from app.agents.policy_agent import PolicyAgent
    except ImportError as e:
        print(f"❌ Error: Could not import PolicyAgent: {e}")
        return
    
    print('🧪 Testing Policy Agent Directly...')
    print('=' * 60)

    # Initialize policy agent
    try:
        policy_agent = PolicyAgent()
        print('✅ Policy agent initialized')
        schemes_count = len(policy_agent.schemes_data.get("schemes", []))
        print(f'📄 Loaded {schemes_count} schemes')
        
        if schemes_count == 0:
            print('❌ No schemes data loaded! Check policy_schemes_data.json')
            return
            
    except Exception as e:
        print(f'❌ Error initializing policy agent: {e}')
        return

    # Test different policy queries
    test_queries = [
        {
            'query': 'What government subsidies are available for farmers in Maharashtra?',
            'location': 'Maharashtra',
            'crop': 'wheat'
        },
        {
            'query': 'How to apply for PM-KISAN scheme?',
            'location': 'Delhi',
            'crop': 'rice'
        },
        {
            'query': 'What is the eligibility for crop insurance?',
            'location': 'Punjab',
            'crop': 'wheat'
        },
        {
            'query': 'Are there any schemes for organic farming?',
            'location': 'Tamil Nadu',
            'crop': 'rice'
        },
        {
            'query': 'I need a loan for my tractor',
            'location': 'Karnataka',
            'crop': 'cotton'
        }
    ]

    results = []
    
    for i, test in enumerate(test_queries, 1):
        print(f'\n🧪 Test {i}: {test["query"]}')
        print(f'📍 Location: {test["location"]} | Crop: {test["crop"]}')
        print('-' * 50)
        
        try:
            result = policy_agent.process_query(test['query'], test['location'], test['crop'])
            
            agent = result.get("agent", "unknown")
            confidence = result.get("confidence", 0.0)
            evidence_count = len(result.get("evidence", []))
            advice = result.get('result', {}).get('advice', 'No advice')
            urgency = result.get('result', {}).get('urgency', 'unknown')
            
            print(f'✅ SUCCESS!')
            print(f'🤖 Agent: {agent}')
            print(f'📊 Confidence: {confidence}')
            print(f'📄 Evidence count: {evidence_count}')
            print(f'⚡ Urgency: {urgency}')
            print(f'💬 Advice: {advice[:200]}...')
            
            results.append({
                'test': test['query'],
                'success': True,
                'confidence': confidence,
                'evidence_count': evidence_count
            })
            
        except Exception as e:
            print(f'❌ ERROR: {str(e)}')
            results.append({
                'test': test['query'],
                'success': False,
                'error': str(e)
            })

    # Summary
    print(f'\n' + '=' * 60)
    print('🎯 POLICY AGENT TEST SUMMARY')
    print('=' * 60)
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"📊 Overall Success Rate: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"{status} {result['test'][:50]}... - Confidence: {result['confidence']}")
        else:
            print(f"{status} {result['test'][:50]}... - Error: {result.get('error', 'Unknown')}")
    
    if successful_tests == total_tests:
        print("✅ All policy agent tests passed!")
        print("✅ Policy agent is working correctly")
    else:
        print(f"⚠️ {total_tests - successful_tests} policy agent issues detected")
    
    return results

if __name__ == "__main__":
    test_policy_agent()
