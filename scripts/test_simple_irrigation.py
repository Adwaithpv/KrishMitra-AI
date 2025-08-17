#!/usr/bin/env python3
"""
Simple test to verify irrigation query flow
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def test_agent_selection():
    """Test that irrigation queries select the right agents"""
    
    from app.coordinator import Coordinator
    
    coordinator = Coordinator()
    
    # Test agent identification
    query = "Should I irrigate my wheat today?"
    relevant_agents = coordinator._identify_relevant_agents(query.lower())
    
    print(f"Query: '{query}'")
    print(f"Relevant agents identified: {relevant_agents}")
    
    if "weather" in relevant_agents:
        print("✅ Weather agent correctly identified for irrigation query")
    else:
        print("❌ Weather agent NOT identified for irrigation query")
    
    # Test weather agent response
    if "weather" in relevant_agents:
        weather_agent = coordinator.agents["weather"]
        response = weather_agent.process_query(query, "Punjab", "wheat")
        
        print(f"\nWeather Agent Response:")
        print(f"Confidence: {response.get('confidence', 0.0)}")
        print(f"Has advice: {'Yes' if response.get('result', {}).get('advice') else 'No'}")
        print(f"Evidence sources: {len(response.get('evidence', []))}")
        
        if response.get('confidence', 0.0) > 0.8:
            print("✅ Weather agent has high confidence response")
        else:
            print("⚠️ Weather agent has low confidence - might be using fallback")

if __name__ == "__main__":
    test_agent_selection()

