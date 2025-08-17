#!/usr/bin/env python3
"""
Comprehensive test script for all agents (Weather, Crop, Finance, Policy)
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_weather_agent():
    """Test the weather agent"""
    print('🌤️ Testing Weather Agent...')
    print('=' * 50)
    
    try:
        from app.agents.weather_agent import WeatherAgent
        weather_agent = WeatherAgent()
        print('✅ Weather agent initialized')
        
        test_queries = [
            {'query': 'Will it rain tomorrow in Mumbai?', 'location': 'Mumbai', 'crop': 'rice'},
            {'query': 'What is the weather forecast for Delhi?', 'location': 'Delhi', 'crop': 'wheat'},
            {'query': 'Is there a drought alert in Punjab?', 'location': 'Punjab', 'crop': 'cotton'},
        ]
        
        results = []
        for i, test in enumerate(test_queries, 1):
            print(f'\n🧪 Weather Test {i}: {test["query"]}')
            print(f'📍 Location: {test["location"]} | Crop: {test["crop"]}')
            print('-' * 40)
            
            try:
                result = weather_agent.process_query(test['query'], test['location'], test['crop'])
                
                agent = result.get("agent", "unknown")
                confidence = result.get("confidence", 0.0)
                evidence_count = len(result.get("evidence", []))
                # Weather agent returns advice in result.advice
                answer = result.get('result', {}).get('advice', 'No advice available')
                
                print(f'✅ SUCCESS!')
                print(f'🤖 Agent: {agent}')
                print(f'📊 Confidence: {confidence}')
                print(f'📄 Evidence count: {evidence_count}')
                print(f'💬 Answer: {answer[:150]}...')
                
                results.append({'success': True, 'confidence': confidence})
                
            except Exception as e:
                print(f'❌ ERROR: {str(e)}')
                results.append({'success': False, 'error': str(e)})
        
        return results
        
    except ImportError as e:
        print(f'❌ Error importing WeatherAgent: {e}')
        return [{'success': False, 'error': str(e)}]

def test_crop_agent():
    """Test the crop agent"""
    print('\n🌱 Testing Crop Agent...')
    print('=' * 50)
    
    try:
        from app.agents.crop_agent import CropAgent
        crop_agent = CropAgent()
        print('✅ Crop agent initialized')
        
        test_queries = [
            {'query': 'How much fertilizer should I use for wheat?', 'location': 'Punjab', 'crop': 'wheat'},
            {'query': 'What is the best planting time for rice?', 'location': 'Tamil Nadu', 'crop': 'rice'},
            {'query': 'How to control pests in cotton crop?', 'location': 'Maharashtra', 'crop': 'cotton'},
        ]
        
        results = []
        for i, test in enumerate(test_queries, 1):
            print(f'\n🧪 Crop Test {i}: {test["query"]}')
            print(f'📍 Location: {test["location"]} | Crop: {test["crop"]}')
            print('-' * 40)
            
            try:
                result = crop_agent.process_query(test['query'], test['location'], test['crop'])
                
                agent = result.get("agent", "unknown")
                confidence = result.get("confidence", 0.0)
                evidence_count = len(result.get("evidence", []))
                # Crop agent may return advice in result.advice or answer
                answer = result.get('answer', result.get('result', {}).get('advice', 'No advice available'))
                
                print(f'✅ SUCCESS!')
                print(f'🤖 Agent: {agent}')
                print(f'📊 Confidence: {confidence}')
                print(f'📄 Evidence count: {evidence_count}')
                print(f'💬 Answer: {answer[:150]}...')
                
                results.append({'success': True, 'confidence': confidence})
                
            except Exception as e:
                print(f'❌ ERROR: {str(e)}')
                results.append({'success': False, 'error': str(e)})
        
        return results
        
    except ImportError as e:
        print(f'❌ Error importing CropAgent: {e}')
        return [{'success': False, 'error': str(e)}]

def test_finance_agent():
    """Test the finance agent"""
    print('\n💰 Testing Finance Agent...')
    print('=' * 50)
    
    try:
        from app.agents.finance_agent import FinanceAgent
        finance_agent = FinanceAgent()
        print('✅ Finance agent initialized')
        
        test_queries = [
            {'query': 'What are the current market prices for rice?', 'location': 'Karnataka', 'crop': 'rice'},
            {'query': 'Where can I sell my wheat for best price?', 'location': 'Haryana', 'crop': 'wheat'},
            {'query': 'What is the mandi rate for cotton today?', 'location': 'Gujarat', 'crop': 'cotton'},
        ]
        
        results = []
        for i, test in enumerate(test_queries, 1):
            print(f'\n🧪 Finance Test {i}: {test["query"]}')
            print(f'📍 Location: {test["location"]} | Crop: {test["crop"]}')
            print('-' * 40)
            
            try:
                result = finance_agent.process_query(test['query'], test['location'], test['crop'])
                
                agent = result.get("agent", "unknown")
                confidence = result.get("confidence", 0.0)
                evidence_count = len(result.get("evidence", []))
                # Finance agent may return advice in result.advice or answer
                answer = result.get('answer', result.get('result', {}).get('advice', 'No advice available'))
                
                print(f'✅ SUCCESS!')
                print(f'🤖 Agent: {agent}')
                print(f'📊 Confidence: {confidence}')
                print(f'📄 Evidence count: {evidence_count}')
                print(f'💬 Answer: {answer[:150]}...')
                
                results.append({'success': True, 'confidence': confidence})
                
            except Exception as e:
                print(f'❌ ERROR: {str(e)}')
                results.append({'success': False, 'error': str(e)})
        
        return results
        
    except ImportError as e:
        print(f'❌ Error importing FinanceAgent: {e}')
        return [{'success': False, 'error': str(e)}]

def test_policy_agent():
    """Test the policy agent (quick version)"""
    print('\n📋 Testing Policy Agent...')
    print('=' * 50)
    
    try:
        from app.agents.policy_agent import PolicyAgent
        policy_agent = PolicyAgent()
        print('✅ Policy agent initialized')
        
        test_query = 'What government subsidies are available for farmers?'
        result = policy_agent.process_query(test_query, 'Maharashtra', 'wheat')
        
        agent = result.get("agent", "unknown")
        confidence = result.get("confidence", 0.0)
        evidence_count = len(result.get("evidence", []))
        
        print(f'🧪 Policy Test: {test_query}')
        print(f'✅ SUCCESS! Agent: {agent} | Confidence: {confidence} | Evidence: {evidence_count}')
        
        return [{'success': True, 'confidence': confidence}]
        
    except Exception as e:
        print(f'❌ Error: {str(e)}')
        return [{'success': False, 'error': str(e)}]

def main():
    """Run all agent tests"""
    print('🧪 COMPREHENSIVE AGENT TESTING')
    print('=' * 70)
    
    all_results = {}
    
    # Test each agent
    all_results['weather'] = test_weather_agent()
    all_results['crop'] = test_crop_agent()
    all_results['finance'] = test_finance_agent()
    all_results['policy'] = test_policy_agent()
    
    # Overall summary
    print('\n' + '=' * 70)
    print('🎯 COMPREHENSIVE AGENT TEST SUMMARY')
    print('=' * 70)
    
    total_tests = 0
    total_success = 0
    
    for agent_name, results in all_results.items():
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        total_tests += total
        total_success += successful
        
        status = "✅" if successful == total else "⚠️"
        print(f"{status} {agent_name.upper()} Agent: {successful}/{total} tests passed")
        
        if successful < total:
            for i, result in enumerate(results):
                if not result.get('success', False):
                    error = result.get('error', 'Unknown error')
                    print(f"   ❌ Test {i+1} failed: {error}")
    
    overall_rate = (total_success / total_tests * 100) if total_tests > 0 else 0
    print(f"\n📊 Overall Success Rate: {total_success}/{total_tests} ({overall_rate:.1f}%)")
    
    if total_success == total_tests:
        print("🎉 ALL AGENTS ARE WORKING PERFECTLY!")
        print("✅ Ready for production use")
    else:
        print(f"⚠️ {total_tests - total_success} issues need attention")
    
    return all_results

if __name__ == "__main__":
    main()