#!/usr/bin/env python3
"""
Setup script to configure Gemini API for enhanced LLM intelligence
"""

import os
import sys

def check_gemini_setup():
    """Check current Gemini configuration"""
    print('🔍 Checking Gemini LLM Setup...')
    print('=' * 50)
    
    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f'✅ GEMINI_API_KEY found: {api_key[:8]}...{api_key[-4:]}')
        
        # Test Gemini client
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))
            from app.llm_client import LLMClient
            
            client = LLMClient()
            if client.gemini_model:
                print('✅ Gemini client initialized successfully')
                
                # Test a simple query
                test_response = client.generate_text("What is agriculture?")
                print(f'✅ Gemini test successful: {test_response[:100]}...')
                
                print('\n🎉 GEMINI IS FULLY CONFIGURED!')
                print('🚀 Your supervisor will now use AI-powered routing')
                return True
            else:
                print('❌ Gemini client failed to initialize')
                return False
                
        except Exception as e:
            print(f'❌ Error testing Gemini: {e}')
            return False
    else:
        print('❌ GEMINI_API_KEY not found')
        print('\n📋 TO ENABLE GEMINI LLM INTELLIGENCE:')
        print('1. Get API key from: https://aistudio.google.com/')
        print('2. Set environment variable:')
        print('   export GEMINI_API_KEY="your_api_key_here"')
        print('   # OR on Windows:')
        print('   set GEMINI_API_KEY=your_api_key_here')
        print('3. Restart your API server')
        print('\n⚡ BENEFITS OF ENABLING GEMINI:')
        print('• Intelligent query understanding')
        print('• Context-aware agent routing') 
        print('• Better handling of complex queries')
        print('• Semantic analysis instead of keyword matching')
        print('• Improved response synthesis')
        return False

def compare_routing_modes():
    """Compare current vs potential LLM routing"""
    print('\n📊 ROUTING COMPARISON:')
    print('=' * 50)
    
    print('🔴 CURRENT (Keyword Matching):')
    print('• "how to apply for centrail pm kisan" → Simple pattern match')
    print('• Limited to predefined keywords')
    print('• No contextual understanding')
    print('• Confidence: 0.6 (fallback)')
    
    print('\n🟢 WITH GEMINI LLM:')
    print('• "how to apply for centrail pm kisan" → AI understands intent')
    print('• Handles typos and variations naturally')
    print('• Contextual analysis of user needs')
    print('• Confidence: 0.8-0.95 (AI-powered)')
    print('• Can handle complex multi-intent queries')

if __name__ == "__main__":
    print('🚀 Gemini LLM Setup Check\n')
    
    is_configured = check_gemini_setup()
    compare_routing_modes()
    
    print('\n' + '=' * 50)
    if is_configured:
        print('✅ READY: Your supervisor uses full AI intelligence!')
    else:
        print('⚠️ LIMITED: Currently using keyword-based routing only')
        print('💡 Enable Gemini for 10x better query understanding')

