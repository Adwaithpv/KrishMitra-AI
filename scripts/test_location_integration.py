#!/usr/bin/env python3
"""
Test the complete location integration fix
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'api'))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'services', 'api', '.env'))
    print(f"Loaded .env file. GEMINI_API_KEY exists: {bool(os.getenv('GEMINI_API_KEY'))}")
except ImportError:
    print("Warning: python-dotenv not installed, using system environment variables")

def test_location_scenarios():
    """Test different location scenarios"""
    
    print("🧪 TESTING LOCATION INTEGRATION")
    print("=" * 60)
    
    test_cases = [
        # GPS coordinates (what the new Flutter app will send)
        {"query": "is it a good time to grow wheat now", "location": "28.6139,77.2090", "crop": "wheat", "desc": "GPS Delhi coordinates"},
        # City name (fallback)
        {"query": "is it a good time to grow wheat now", "location": "Mumbai", "crop": "wheat", "desc": "City name"},
        # No location (backend default)
        {"query": "is it a good time to grow wheat now", "location": None, "crop": "wheat", "desc": "No location (backend default)"},
        # Real user query style
        {"query": "Should I water my crops today?", "location": "19.0760,72.8777", "crop": None, "desc": "GPS Mumbai coordinates"},
    ]
    
    from app.main import Query, _run_query
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 TEST CASE {i}: {test_case['desc']}")
        print("-" * 50)
        print(f"Query: {test_case['query']}")
        print(f"Location: {test_case['location']}")
        print(f"Crop: {test_case['crop']}")
        
        try:
            q = Query(
                text=test_case['query'], 
                location=test_case['location'], 
                crop=test_case['crop']
            )
            
            result = _run_query(q)
            
            answer = result.get('answer', '')
            confidence = result.get('confidence', 0.0)
            agent_used = result.get('agent_used', '')
            evidence = result.get('evidence', [])
            
            print(f"✅ Confidence: {confidence}")
            print(f"✅ Agent used: {agent_used}")
            print(f"✅ Evidence count: {len(evidence)}")
            
            # Check for success indicators
            if "provided evidence does not contain" in answer.lower():
                print("❌ FAILED: Still using static fallback")
            elif "monitor temperature fluctuations" in answer.lower():
                print("❌ FAILED: Simple pattern matching")
            elif confidence > 0.8:
                print("✅ SUCCESS: High confidence response")
            else:
                print("⚠️  PARTIAL: Moderate confidence response")
            
            # Check for location-specific weather data
            weather_evidence = [e for e in evidence if 'weather' in str(e.get('source', '')).lower()]
            if weather_evidence:
                print(f"✅ Weather evidence: {len(weather_evidence)} sources")
                # Check if location matches
                for we in weather_evidence[:1]:
                    source_text = str(we.get('excerpt', ''))
                    if test_case['location'] and ('delhi' in source_text.lower() or 'mumbai' in source_text.lower()):
                        print("✅ Location-specific weather data detected")
                    elif test_case['location'] is None and 'delhi' in source_text.lower():
                        print("✅ Default location weather data detected")
            else:
                print("⚠️  No weather evidence found")
            
            print(f"Answer preview: {answer[:150]}...")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

def test_weather_agent_with_coordinates():
    """Test weather agent specifically with GPS coordinates"""
    
    print("\n🌍 TESTING WEATHER AGENT WITH GPS COORDINATES")
    print("=" * 60)
    
    from app.agents.weather_agent import WeatherAgent
    
    weather_agent = WeatherAgent()
    
    gps_coordinates = [
        {"location": "28.6139,77.2090", "name": "Delhi GPS"},
        {"location": "19.0760,72.8777", "name": "Mumbai GPS"},
        {"location": "30.7333,76.7794", "name": "Chandigarh GPS"},
    ]
    
    for i, coord in enumerate(gps_coordinates, 1):
        print(f"\n🧪 Weather Test {i}: {coord['name']}")
        print(f"Coordinates: {coord['location']}")
        
        try:
            response = weather_agent.process_query(
                "What are the weather conditions for farming?",
                coord['location'],
                "wheat"
            )
            
            result = response.get('result', {})
            advice = result.get('advice', '')
            confidence = response.get('confidence', 0.0)
            evidence = response.get('evidence', [])
            
            print(f"Confidence: {confidence}")
            print(f"Evidence count: {len(evidence)}")
            
            if confidence > 0.9:
                print("✅ High confidence weather analysis")
            else:
                print("⚠️  Lower confidence response")
            
            print(f"Advice preview: {advice[:150]}...")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_location_scenarios()
    test_weather_agent_with_coordinates()








