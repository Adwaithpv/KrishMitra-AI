#!/usr/bin/env python3
"""
Final test for weather agent LLM integration fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_weather_growing_conditions():
    """Test the specific query that was failing"""
    
    from app.coordinator import Coordinator
    
    coordinator = Coordinator()
    
    test_queries = [
        "whether the weather is good for growing wheat",
        "Should I irrigate my wheat today?",
        "Is the weather suitable for planting rice?",
        "Are conditions good for cotton farming?"
    ]
    
    print("🌾 Testing Weather + Growing Condition Queries")
    print("=" * 60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: '{query}'")
        print("-" * 50)
        
        # Test agent identification
        relevant_agents = coordinator._identify_relevant_agents(query.lower())
        print(f"Agents identified: {relevant_agents}")
        
        if "weather" not in relevant_agents:
            print("❌ Weather agent not identified!")
            continue
        
        # Test full processing
        try:
            result = coordinator.process_query(query, "Punjab", "wheat")
            
            confidence = result.get('confidence', 0.0)
            answer = result.get('answer', '')
            evidence = result.get('evidence', [])
            
            print(f"Confidence: {confidence}")
            print(f"Answer length: {len(answer)} chars")
            print(f"Evidence sources: {len(evidence)}")
            
            # Check for weather data usage
            weather_sources = [e for e in evidence if 'weather' in e.get('source', '').lower()]
            if weather_sources:
                print(f"✅ Using real weather data: {len(weather_sources)} sources")
            else:
                print("❌ No real weather data found")
            
            # Check if answer mentions weather conditions
            if any(word in answer.lower() for word in ['temperature', 'rain', 'weather', 'conditions']):
                print("✅ Answer includes weather analysis")
            else:
                print("❌ Answer doesn't mention weather")
            
            # Check for generic fallback responses
            if "provided evidence does not contain" in answer:
                print("❌ STILL USING STATIC DATA FALLBACK!")
            else:
                print("✅ Not using static data fallback")
            
            print(f"Answer preview: {answer[:150]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    test_weather_growing_conditions()

