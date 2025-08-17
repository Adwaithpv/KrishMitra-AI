#!/usr/bin/env python3
"""
Debug script to investigate subsidy query issues
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_subsidy_query():
    """Test subsidy query through different approaches"""
    
    print('🔍 Debugging Subsidy Query Issue...')
    print('=' * 60)
    
    # Test 1: Direct Policy Agent
    print('\n1️⃣ Testing Policy Agent Directly:')
    print('-' * 40)
    
    try:
        from app.agents.policy_agent import PolicyAgent
        policy_agent = PolicyAgent()
        
        query = 'What subsidies are available for farmers?'
        result = policy_agent.process_query(query, 'Maharashtra', 'wheat')
        
        print(f'✅ Policy Agent Response:')
        print(f'Agent: {result.get("agent", "unknown")}')
        print(f'Confidence: {result.get("confidence", 0.0)}')
        print(f'Evidence count: {len(result.get("evidence", []))}')
        
        advice = result.get('result', {}).get('advice', 'No advice')
        print(f'Advice: {advice[:200]}...')
        
        print(f'\n📄 Full Evidence:')
        for i, evidence in enumerate(result.get("evidence", []), 1):
            print(f'  {i}. {evidence.get("excerpt", "No excerpt")[:100]}...')
        
    except Exception as e:
        print(f'❌ Policy Agent Error: {e}')
    
    # Test 2: Supervisor Agent
    print('\n2️⃣ Testing Supervisor Agent:')
    print('-' * 40)
    
    try:
        from app.supervisor import SupervisorAgent
        supervisor = SupervisorAgent()
        
        query = 'What subsidies are available for farmers?'
        result = supervisor.process_query(query, 'Maharashtra', 'wheat')
        
        print(f'✅ Supervisor Response:')
        print(f'Answer: {result.get("answer", "No answer")[:200]}...')
        print(f'Agents Consulted: {result.get("agents_consulted", [])}')
        print(f'Confidence: {result.get("confidence", 0.0)}')
        print(f'Evidence count: {len(result.get("evidence", []))}')
        print(f'Workflow trace: {result.get("workflow_trace", "unknown")}')
        
        print(f'\n📄 Supervisor Evidence:')
        for i, evidence in enumerate(result.get("evidence", []), 1):
            excerpt = evidence.get("excerpt", "No excerpt") if isinstance(evidence, dict) else str(evidence)
            print(f'  {i}. {excerpt[:100]}...')
        
    except Exception as e:
        print(f'❌ Supervisor Error: {e}')
    
    # Test 3: Check if routing is working
    print('\n3️⃣ Testing Query Analysis:')
    print('-' * 40)
    
    try:
        supervisor = SupervisorAgent()
        # Try to access the query analysis method directly
        query = 'What subsidies are available for farmers?'
        
        # Create a test state to see how the analysis works
        test_state = {
            "query": query,
            "location": "Maharashtra",
            "crop": "wheat",
            "user_context": {},
            "agent_decisions": [],
            "agent_responses": [],
            "final_answer": "",
            "evidence": [],
            "confidence": 0.0,
            "workflow_step": "started",
            "error": ""
        }
        
        analyzed_state = supervisor._analyze_query(test_state)
        
        print(f'✅ Query Analysis:')
        print(f'User Context: {analyzed_state.get("user_context", {})}')
        print(f'Workflow Step: {analyzed_state.get("workflow_step", "unknown")}')
        print(f'Error: {analyzed_state.get("error", "None")}')
        
    except Exception as e:
        print(f'❌ Query Analysis Error: {e}')

if __name__ == "__main__":
    test_subsidy_query()
