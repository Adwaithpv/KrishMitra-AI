#!/usr/bin/env python3
"""
Debug script to simulate the exact Flutter query that's failing
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

def debug_flutter_query():
    """Debug the specific query that Flutter is sending"""
    
    # This is the exact query from user
    query = "is it a good time to grow wheat now"
    location = None  # Flutter might not be sending location
    crop = None      # Flutter might not be sending crop
    
    print("🐛 DEBUGGING FLUTTER QUERY SIMULATION")
    print("=" * 60)
    print(f"Query: '{query}'")
    print(f"Location: {location}")
    print(f"Crop: {crop}")
    print()
    
    # Step 1: Test coordinator agent identification
    print("STEP 1: Agent Identification")
    print("-" * 30)
    
    from app.coordinator import Coordinator
    coordinator = Coordinator()
    
    query_lower = query.lower()
    relevant_agents = coordinator._identify_relevant_agents(query_lower)
    print(f"Query keywords: {query_lower}")
    print(f"Relevant agents: {relevant_agents}")
    
    # Check specific keyword matching
    weather_keywords = ["weather", "rain", "rainfall", "drought", "temperature", "heat", "cold", "storm", "forecast", "alert", "growing", "grow", "suitable", "conditions", "climate", "season"]
    matching_weather = [kw for kw in weather_keywords if kw in query_lower]
    print(f"Matching weather keywords: {matching_weather}")
    
    if "weather" not in relevant_agents:
        print("❌ PROBLEM: Weather agent not identified!")
        print("Query contains 'good time to grow' but weather agent not triggered")
        return
    else:
        print("✅ Weather agent correctly identified")
    
    # Step 2: Test coordinator full processing
    print("\nSTEP 2: Coordinator Processing")
    print("-" * 30)
    
    try:
        coord_response = coordinator.process_query(query, location, crop)
        
        coord_confidence = coord_response.get('confidence', 0.0)
        agents_consulted = coord_response.get('agents_consulted', [])
        answer = coord_response.get('answer', '')
        evidence = coord_response.get('evidence', [])
        
        print(f"Coordinator confidence: {coord_confidence}")
        print(f"Agents consulted: {agents_consulted}")
        print(f"Answer length: {len(answer)} chars")
        print(f"Evidence count: {len(evidence)}")
        
        # Check for the problematic response
        if "provided evidence does not contain" in answer.lower():
            print("❌ PROBLEM FOUND: Static data fallback response!")
            print(f"Answer: {answer[:200]}...")
        else:
            print("✅ Answer doesn't contain static fallback text")
            print(f"Answer preview: {answer[:200]}...")
        
        # Check evidence sources
        weather_evidence = [e for e in evidence if 'weather' in str(e.get('source', '')).lower()]
        if weather_evidence:
            print(f"✅ Weather evidence found: {len(weather_evidence)} items")
        else:
            print("❌ PROBLEM: No weather evidence found!")
        
    except Exception as e:
        print(f"❌ PROBLEM: Coordinator failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 3: Test main pipeline simulation
    print("\nSTEP 3: Main Pipeline Simulation")
    print("-" * 30)
    
    from app.main import Query, _run_query
    
    q = Query(text=query, location=location, crop=crop)
    
    try:
        result = _run_query(q)
        
        final_answer = result.get('answer', '')
        final_confidence = result.get('confidence', 0.0)
        agent_used = result.get('agent_used', '')
        final_evidence = result.get('evidence', [])
        
        print(f"Final confidence: {final_confidence}")
        print(f"Agent used: {agent_used}")
        print(f"Evidence count: {len(final_evidence)}")
        
        if "provided evidence does not contain" in final_answer.lower():
            print("❌ FINAL PROBLEM: Main pipeline returned static fallback!")
            print(f"Final answer: {final_answer[:300]}...")
            
            # Debug the confidence threshold logic
            weather_in_agents = any("weather" in str(agent) for agent in agents_consulted)
            confidence_threshold = 0.4 if weather_in_agents else 0.6
            print(f"Weather in agents: {weather_in_agents}")
            print(f"Confidence threshold: {confidence_threshold}")
            print(f"Coordinator confidence: {coord_confidence}")
            print(f"Threshold check: {coord_confidence} > {confidence_threshold} = {coord_confidence > confidence_threshold}")
            
        else:
            print("✅ Final answer looks good!")
            print(f"Final answer preview: {final_answer[:200]}...")
        
    except Exception as e:
        print(f"❌ PROBLEM: Main pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_flutter_query()

