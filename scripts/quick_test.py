#!/usr/bin/env python3
"""
Quick test to verify routing fix
"""

import sys
import os

# Add the API directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.supervisor import SupervisorAgent

print('🧪 Testing Single Query Routing...')
print('🔧 Initializing supervisor...')
supervisor = SupervisorAgent()

print('🔄 Testing policy query...')
result = supervisor.process_query('What government subsidies are available for farmers?', 'Maharashtra', 'wheat')

print(f'✅ Results:')
print(f'Agents Consulted: {result.get("agents_consulted", [])}')
print(f'Agent Used: {result.get("agent_used", "unknown")}')
print(f'Workflow Trace: {result.get("workflow_trace", "unknown")}')
print(f'Answer: {result.get("answer", "No answer")[:100]}...')
print(f'Confidence: {result.get("confidence", 0.0)}')
