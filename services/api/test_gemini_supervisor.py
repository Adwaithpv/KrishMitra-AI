#!/usr/bin/env python3
"""
Test supervisor with Gemini LLM intelligence
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

print('🧪 Testing Supervisor with Gemini LLM...')
print('=' * 50)

# Check API key
api_key = os.getenv("GEMINI_API_KEY")
print(f'✅ API Key: {api_key[:8]}...{api_key[-4:]}')

# Test supervisor
from app.supervisor import SupervisorAgent

supervisor = SupervisorAgent()

# Test the problematic query
query = 'how to apply for centrail pm kisan?'
print(f'\n🔍 Query: "{query}"')
print('-' * 30)

result = supervisor.process_query(query, 'Maharashtra', 'wheat')

print(f'🤖 Agents Consulted: {result.get("agents_consulted", [])}')
print(f'📊 Confidence: {result.get("confidence", 0.0)}')
print(f'🔧 Workflow: {result.get("workflow_trace", "unknown")}')
print(f'💬 Answer: {result.get("answer", "")[:200]}...')

# Check if it's using LLM or fallback
if "fallback" in str(result.get("workflow_trace", "")).lower():
    print('\n⚠️ Still using fallback routing')
else:
    print('\n🎉 Using AI-powered routing!')

