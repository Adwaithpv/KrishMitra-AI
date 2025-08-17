#!/usr/bin/env python3
"""
Test script to verify improved routing accuracy
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_routing_accuracy():
    """Test routing with various query patterns"""
    print('🧪 Testing Improved Routing Accuracy...')
    print('=' * 60)
    
    try:
        from app.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        
        # Test cases with expected agents
        test_cases = [
            # Policy queries (should route to policy agent)
            ("how to apply for centrail pm kisan?", "policy"),
            ("What subsidies are available?", "policy"),
            ("PM-Kisan application process", "policy"),
            ("pradhan mantri kisan scheme", "policy"),
            ("government benefits for farmers", "policy"),
            ("how to get fasal bima?", "policy"),
            ("crop insurance application", "policy"),
            ("eligibility for farm loans", "policy"),
            
            # Weather queries
            ("What is the weather forecast?", "weather"),
            ("Will it rain tomorrow?", "weather"),
            ("drought alert in Punjab", "weather"),
            
            # Crop queries  
            ("How much fertilizer for wheat?", "crop"),
            ("pest control in cotton", "crop"),
            ("best planting time", "crop"),
            
            # Finance queries
            ("market price of rice", "finance"),
            ("mandi rates today", "finance"),
            ("selling wheat prices", "finance"),
        ]
        
        correct_routes = 0
        total_tests = len(test_cases)
        
        print(f'🔍 Testing {total_tests} routing scenarios...\n')
        
        for i, (query, expected_agent) in enumerate(test_cases, 1):
            print(f'🧪 Test {i}: "{query}"')
            print(f'   Expected: {expected_agent} agent')
            
            # Test both modes if possible
            result = supervisor.process_query(query, 'Maharashtra', 'wheat')
            agents_consulted = result.get("agents_consulted", [])
            
            # Check if the expected agent was consulted
            routed_correctly = any(expected_agent in agent.lower() for agent in agents_consulted)
            
            if routed_correctly:
                print(f'   ✅ CORRECT: Routed to {agents_consulted}')
                correct_routes += 1
            else:
                print(f'   ❌ INCORRECT: Routed to {agents_consulted} (expected {expected_agent})')
            
            print()
        
        # Calculate accuracy
        accuracy = (correct_routes / total_tests) * 100
        print('=' * 60)
        print(f'🎯 ROUTING ACCURACY RESULTS:')
        print(f'✅ Correct: {correct_routes}/{total_tests}')
        print(f'📊 Accuracy: {accuracy:.1f}%')
        
        if accuracy >= 90:
            print('🎉 EXCELLENT ROUTING ACCURACY!')
        elif accuracy >= 75:
            print('✅ Good routing accuracy')
        else:
            print('⚠️ Routing needs improvement')
        
        return accuracy >= 75
        
    except Exception as e:
        print(f'❌ ERROR: {str(e)}')
        import traceback
        traceback.print_exc()
        return False

def test_specific_problematic_query():
    """Test the specific query that was failing"""
    print('\n🔍 Testing Specific Problematic Query...')
    print('=' * 60)
    
    try:
        from app.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        
        query = "how to apply for centrail pm kisan?"
        print(f'Query: "{query}"')
        
        result = supervisor.process_query(query, '12.9647654,80.2356074', None)
        
        agents_consulted = result.get("agents_consulted", [])
        workflow_trace = result.get("workflow_trace", "unknown")
        answer = result.get("answer", "")
        
        print(f'Agents Consulted: {agents_consulted}')
        print(f'Workflow: {workflow_trace}')
        print(f'Answer Preview: {answer[:150]}...')
        
        if any("policy" in agent.lower() for agent in agents_consulted):
            print('✅ SUCCESS: Correctly routed to policy agent!')
            return True
        else:
            print('❌ FAILED: Still not routing to policy agent')
            return False
            
    except Exception as e:
        print(f'❌ ERROR: {str(e)}')
        return False

if __name__ == "__main__":
    print('🚀 Starting routing accuracy tests...\n')
    
    # Test general routing accuracy
    general_success = test_routing_accuracy()
    
    # Test the specific problematic query
    specific_success = test_specific_problematic_query()
    
    print('\n' + '=' * 60)
    if general_success and specific_success:
        print('🎉 ALL ROUTING TESTS PASSED!')
        print('✅ Ready for production with improved accuracy!')
    else:
        print('⚠️ Some routing issues remain - needs further tuning')

