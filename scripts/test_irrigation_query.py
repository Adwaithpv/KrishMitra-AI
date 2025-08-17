#!/usr/bin/env python3
"""
Test script specifically for irrigation queries to verify weather agent integration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

from app.coordinator import Coordinator

def test_irrigation_queries():
    """Test irrigation-related queries"""
    
    coordinator = Coordinator()
    
    test_queries = [
        "Should I irrigate my wheat today?",
        "Do I need to water my crops?", 
        "Irrigation advice for rice",
        "When should I irrigate cotton?",
        "Is it good time for watering sugarcane?"
    ]
    
    print("🌊 Testing Irrigation Queries with Weather Agent Integration")
    print("=" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: '{query}'")
        print("-" * 50)
        
        try:
            result = coordinator.process_query(
                query=query,
                location="Punjab",
                crop="wheat"
            )
            
            print(f"Confidence: {result.get('confidence', 0.0)}")
            print(f"Agents Consulted: {result.get('agents_consulted', [])}")
            print(f"Agent Used: {result.get('agent_used', 'unknown')}")
            print(f"Answer Length: {len(result.get('answer', ''))} characters")
            print(f"Evidence Sources: {len(result.get('evidence', []))} sources")
            
            answer = result.get('answer', '')
            if len(answer) > 200:
                print(f"Answer Preview: {answer[:200]}...")
            else:
                print(f"Full Answer: {answer}")
            
            # Check if real weather data is being used
            evidence = result.get('evidence', [])
            weather_sources = [e for e in evidence if 'weather' in e.get('source', '').lower()]
            if weather_sources:
                print(f"✅ Real weather data found: {len(weather_sources)} weather sources")
                for ws in weather_sources[:1]:  # Show first weather source
                    print(f"   Sample: {ws.get('excerpt', '')[:100]}...")
            else:
                print("❌ No real weather data found in evidence")
                
        except Exception as e:
            print(f"Error: {e}")
        
        print()

if __name__ == "__main__":
    test_irrigation_queries()

