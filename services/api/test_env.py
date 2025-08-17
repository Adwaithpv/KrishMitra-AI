#!/usr/bin/env python3
"""
Test script to check if .env file is being loaded correctly
"""

import os
from dotenv import load_dotenv

print('🔍 Testing .env file loading...')
print('=' * 40)

# Load .env file
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    print(f'✅ GEMINI_API_KEY found: {api_key[:8]}...{api_key[-4:]}')
    print(f'✅ Key length: {len(api_key)} characters')
    
    # Test the LLM client
    try:
        from app.llm_client import LLMClient
        client = LLMClient()
        
        if client.gemini_model:
            print('✅ Gemini client initialized successfully!')
            
            # Test a simple generation
            response = client.generate_text("What is 2+2?")
            print(f'✅ Gemini test: {response[:100]}...')
            
        else:
            print('❌ Gemini client not initialized')
            
    except Exception as e:
        print(f'❌ Error testing Gemini: {e}')
        
else:
    print('❌ GEMINI_API_KEY not found')
    print('Current working directory:', os.getcwd())
    print('Files in directory:', os.listdir('.'))
    
print('\n🎯 Summary:')
if api_key and os.path.exists('.env'):
    print('✅ .env file exists and API key is loaded')
    print('🚀 Gemini should work when supervisor runs!')
else:
    print('❌ Issue with .env loading or API key')

