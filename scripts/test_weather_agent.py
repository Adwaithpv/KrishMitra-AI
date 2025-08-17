#!/usr/bin/env python3
"""
Test script for the new LLM-powered Weather Agent
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.agents.weather_agent import WeatherAgent

def test_weather_agent():
    """Test the weather agent with various queries"""
    
    agent = WeatherAgent()
    
    # Test cases
    test_cases = [
        {
            "query": "Will it rain today?",
            "location": "Punjab",
            "crop": "wheat"
        },
        {
            "query": "Is it too hot for crops?",
            "location": "Karnataka",
            "crop": "cotton"
        },
        {
            "query": "Drought conditions",
            "location": "Maharashtra",
            "crop": "sugarcane"
        },
        {
            "query": "Irrigation advice for today",
            "location": "Haryana",
            "crop": "rice"
        },
        {
            "query": "Weather forecast",
            "location": "Gujarat",
            "crop": "groundnut"
        }
    ]
    
    print("🌤️  Testing Weather Agent with LLM Analysis")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['query']}")
        print(f"Location: {test['location']}, Crop: {test['crop']}")
        print("-" * 40)
        
        try:
            result = agent.process_query(
                query=test['query'],
                location=test['location'],
                crop=test['crop']
            )
            
            print(f"Agent: {result['agent']}")
            print(f"Confidence: {result['confidence']}")
            print(f"Advice: {result['result']['advice'][:200]}...")
            print(f"Urgency: {result['result']['urgency']}")
            print(f"Evidence Sources: {len(result['evidence'])} sources")
            
            for evidence in result['evidence']:
                print(f"  - {evidence['source']}: {evidence['excerpt'][:100]}...")
            
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_weather_agent()

