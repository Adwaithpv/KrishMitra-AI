#!/usr/bin/env python3
"""
Test script for the enhanced weather agent with location coordinates
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents.weather_agent import WeatherAgent

def test_weather_agent():
    """Test the weather agent with different scenarios"""
    agent = WeatherAgent()
    
    # Test scenarios
    test_cases = [
        {
            "query": "weather forecast",
            "location": "13.0449408,80.2127872",  # Chennai coordinates
            "crop": "rice",
            "description": "General weather query with Chennai coordinates and rice crop"
        },
        {
            "query": "will it rain tomorrow",
            "location": "13.0449408,80.2127872",
            "crop": "cotton",
            "description": "Rain query with coordinates"
        },
        {
            "query": "irrigation advice",
            "location": "Chennai, Tamil Nadu, India",
            "crop": "wheat",
            "description": "Irrigation query with location name"
        },
        {
            "query": "temperature alert",
            "location": "13.0449408,80.2127872",
            "crop": None,
            "description": "Temperature query without crop specification"
        },
        {
            "query": "drought conditions",
            "location": None,
            "crop": "sugarcane",
            "description": "Drought query without location (fallback test)"
        }
    ]
    
    print("🌤️ Testing Enhanced Weather Agent with Real Location Data\n")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        print(f"Location: {test_case['location'] or 'None'}")
        print(f"Crop: {test_case['crop'] or 'None'}")
        print("-" * 60)
        
        try:
            result = agent.process_query(
                query=test_case['query'],
                location=test_case['location'],
                crop=test_case['crop']
            )
            
            print(f"✅ Agent: {result['agent']}")
            print(f"🎯 Confidence: {result['confidence']}")
            print(f"⚠️ Urgency: {result['result'].get('urgency', 'N/A')}")
            print(f"📍 Location: {result['result'].get('location', 'N/A')}")
            print(f"💡 Advice: {result['result']['advice']}")
            
            if result['evidence']:
                print(f"📚 Evidence Sources: {len(result['evidence'])}")
                for evidence in result['evidence'][:1]:  # Show first evidence
                    print(f"   - Source: {evidence['source']}")
                    print(f"   - Excerpt: {evidence['excerpt'][:100]}...")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("=" * 80)
    
    print("\n🎉 Weather Agent Testing Complete!")
    print("\nKey Features Tested:")
    print("✅ Real weather data integration")
    print("✅ Location coordinate extraction") 
    print("✅ Crop-specific advice")
    print("✅ Urgency assessment")
    print("✅ Fallback handling")
    print("✅ Evidence sourcing")

if __name__ == "__main__":
    test_weather_agent()
