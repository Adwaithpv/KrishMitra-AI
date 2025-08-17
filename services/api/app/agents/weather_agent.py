"""
Weather Agent for agricultural weather advisories with LLM-powered analysis of real-time weather data
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
import json
import re


class WeatherAgent:
    def __init__(self):
        self.name = "weather_agent"
        self.api_key = "49197751d7fa46cda81192655250908"  # WeatherAPI key
        self.base_url = "https://api.weatherapi.com/v1"
        self.llm_client = None
    
    def _get_llm_client(self):
        """Get LLM client for weather analysis"""
        if self.llm_client is None:
            try:
                # Import here to avoid circular imports
                from ..llm_client import LLMClient
                self.llm_client = LLMClient()
            except ImportError:
                try:
                    import sys
                    import os
                    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    from llm_client import LLMClient
                    self.llm_client = LLMClient()
                except ImportError:
                    print("Warning: LLM client not available, using fallback analysis")
                    self.llm_client = None
        return self.llm_client
    
    def process_query(self, query: str, location: str = None, crop: str = None) -> Dict[str, Any]:
        """Process weather-related queries with LLM-powered analysis of real weather data"""
        
        # Get real weather data
        weather_data = self._get_weather_data(location)
        
        if not weather_data:
            return self._generate_fallback_response(query, location, crop)
        
        # Use LLM to analyze weather data and generate agricultural advice
        return self._analyze_weather_with_llm(query, weather_data, location, crop)
    
    def _extract_coordinates(self, location: str) -> Optional[tuple]:
        """Extract coordinates from location string"""
        if not location:
            return None
            
        # Look for coordinate pattern (lat, lon)
        coord_pattern = r'(-?\d+\.?\d*),\s*(-?\d+\.?\d*)'
        match = re.search(coord_pattern, location)
        if match:
            lat, lon = float(match.group(1)), float(match.group(2))
            return (lat, lon)
        
        return None
    
    def _get_weather_data(self, location: str) -> Optional[Dict]:
        """Fetch real weather data from WeatherAPI"""
        if not location:
            # Use default location for general agricultural advice
            location = "Delhi, India"  # Major agricultural region as default
            print(f"No location provided, using default: {location}")
            
        try:
            # Try to extract coordinates first
            coords = self._extract_coordinates(location)
            if coords:
                lat, lon = coords
                query_location = f"{lat},{lon}"
            else:
                query_location = location
            
            # Fetch current weather and 7-day forecast
            url = f"{self.base_url}/forecast.json"
            params = {
                "key": self.api_key,
                "q": query_location,
                "days": 7,  # Extended forecast for better analysis
                "aqi": "yes",  # Include air quality data
                "alerts": "yes"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Weather API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def _format_weather_data_for_llm(self, weather_data: Dict) -> str:
        """Format weather data into a structured text for LLM analysis"""
        
        location_info = weather_data.get("location", {})
        current = weather_data.get("current", {})
        forecast = weather_data.get("forecast", {}).get("forecastday", [])
        alerts = weather_data.get("alerts", {}).get("alert", [])
        
        # Build comprehensive weather summary
        weather_summary = f"""
LOCATION: {location_info.get('name', 'Unknown')}, {location_info.get('region', '')}, {location_info.get('country', '')}
COORDINATES: {location_info.get('lat', 0)}, {location_info.get('lon', 0)}
TIMEZONE: {location_info.get('tz_id', '')}
LAST UPDATED: {current.get('last_updated', '')}

CURRENT CONDITIONS:
- Temperature: {current.get('temp_c', 0)}°C (feels like {current.get('feelslike_c', 0)}°C)
- Condition: {current.get('condition', {}).get('text', 'Unknown')}
- Humidity: {current.get('humidity', 0)}%
- Precipitation: {current.get('precip_mm', 0)}mm
- Wind: {current.get('wind_kph', 0)} km/h {current.get('wind_dir', '')}
- Pressure: {current.get('pressure_mb', 0)} mb
- UV Index: {current.get('uv', 0)}
- Visibility: {current.get('vis_km', 0)} km
- Cloud Cover: {current.get('cloud', 0)}%
"""

        # Add air quality if available
        if current.get('air_quality'):
            aq = current['air_quality']
            weather_summary += f"""
AIR QUALITY:
- CO: {aq.get('co', 0)} μg/m³
- NO2: {aq.get('no2', 0)} μg/m³
- O3: {aq.get('o3', 0)} μg/m³
- PM2.5: {aq.get('pm2_5', 0)} μg/m³
- PM10: {aq.get('pm10', 0)} μg/m³
"""

        # Add forecast data
        weather_summary += "\n7-DAY FORECAST:\n"
        for i, day in enumerate(forecast[:7]):
            date = day.get('date', '')
            day_data = day.get('day', {})
            astro = day.get('astro', {})
            
            weather_summary += f"""
Day {i+1} ({date}):
- Condition: {day_data.get('condition', {}).get('text', 'Unknown')}
- Temperature: {day_data.get('mintemp_c', 0)}°C to {day_data.get('maxtemp_c', 0)}°C
- Precipitation: {day_data.get('totalprecip_mm', 0)}mm (chance: {day_data.get('daily_chance_of_rain', 0)}%)
- Humidity: {day_data.get('avghumidity', 0)}%
- Wind: {day_data.get('maxwind_kph', 0)} km/h
- UV Index: {day_data.get('uv', 0)}
- Sunrise: {astro.get('sunrise', '')} | Sunset: {astro.get('sunset', '')}
"""

        # Add weather alerts if any
        if alerts:
            weather_summary += "\nWEATHER ALERTS:\n"
            for alert in alerts:
                weather_summary += f"""
- {alert.get('headline', 'Alert')}
- Severity: {alert.get('severity', 'Unknown')}
- Areas: {alert.get('areas', '')}
- Description: {alert.get('desc', '')}
- Effective: {alert.get('effective', '')} to {alert.get('expires', '')}
"""

        return weather_summary.strip()
    
    def _analyze_weather_with_llm(self, query: str, weather_data: Dict, location: str, crop: str) -> Dict[str, Any]:
        """Use LLM to analyze weather data and provide agricultural insights"""
        
        llm_client = self._get_llm_client()
        if not llm_client:
            return self._generate_fallback_response(query, location, crop)
        
        # Format weather data for LLM
        weather_summary = self._format_weather_data_for_llm(weather_data)
        location_name = weather_data.get("location", {}).get("name", location or "your area")
        
        # Create comprehensive prompt for agricultural weather analysis
        analysis_prompt = f"""You are an expert agricultural weather advisor. Analyze the following real-time weather data and provide specific, actionable agricultural advice.

USER QUERY: "{query}"
LOCATION: {location_name}
CROP: {crop or "general farming"}

REAL-TIME WEATHER DATA:
{weather_summary}

Please provide:
1. IMMEDIATE AGRICULTURAL ADVICE: Specific actions farmers should take based on current and forecast conditions
2. CROP-SPECIFIC RECOMMENDATIONS: Tailored advice for {crop or "the specified crop"} if applicable
3. RISK ASSESSMENT: Identify potential weather-related agricultural risks (heat stress, frost, waterlogging, drought, etc.)
4. TIMING RECOMMENDATIONS: Best times for field operations (planting, harvesting, spraying, irrigation)
5. URGENCY LEVEL: Rate as "low", "medium", or "high" based on immediate weather threats

Focus on:
- Irrigation scheduling based on rainfall forecasts
- Crop protection from extreme weather
- Optimal timing for agricultural operations
- Disease and pest risk due to weather conditions
- Soil management recommendations
- Worker safety considerations

Keep advice practical, specific, and immediately actionable. Use the actual weather data provided."""

        try:
            # Generate LLM analysis using custom agricultural analysis method
            llm_analysis = llm_client.generate_agricultural_analysis(analysis_prompt)
            
            # Extract urgency level from analysis
            urgency = "medium"  # default
            if any(word in llm_analysis.lower() for word in ["urgent", "immediate", "critical", "emergency", "severe"]):
                urgency = "high"
            elif any(word in llm_analysis.lower() for word in ["low risk", "normal", "stable", "favorable"]):
                urgency = "low"
            
            # Prepare evidence
            evidence = [
                {
                    "source": "real_time_weather_api",
                    "excerpt": f"Live weather data from {location_name}: {weather_data.get('current', {}).get('condition', {}).get('text', 'Unknown condition')} at {weather_data.get('current', {}).get('temp_c', 0)}°C",
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "geo": location_name,
                    "crop": crop or "all"
                }
            ]
            
            # Add forecast summary to evidence
            if weather_data.get("forecast", {}).get("forecastday"):
                forecast_days = weather_data["forecast"]["forecastday"][:3]
                forecast_summary = ", ".join([
                    f"{day.get('date')}: {day.get('day', {}).get('condition', {}).get('text', 'Unknown')} ({day.get('day', {}).get('mintemp_c', 0)}-{day.get('day', {}).get('maxtemp_c', 0)}°C, {day.get('day', {}).get('totalprecip_mm', 0)}mm rain)"
                    for day in forecast_days
                ])
                
                evidence.append({
                    "source": "weather_forecast_api",
                    "excerpt": f"3-day forecast: {forecast_summary}",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "geo": location_name,
                    "crop": crop or "all"
                })
            
            return {
                "agent": self.name,
                "result": {
                    "advice": llm_analysis,
                    "urgency": urgency,
                    "location": location_name
                },
                "evidence": evidence,
                "confidence": 0.95  # High confidence since using real-time data + LLM analysis
            }
            
        except Exception as e:
            print(f"Error in LLM weather analysis: {e}")
            return self._generate_fallback_response(query, location, crop)
    
    def _generate_fallback_response(self, query: str, location: str, crop: str) -> Dict[str, Any]:
        """Generate fallback response when weather data or LLM is not available"""
        
        query_lower = query.lower()
        
        # Basic pattern matching for fallback advice
        if any(word in query_lower for word in ["rain", "rainfall", "storm"]):
            advice = "Monitor rainfall patterns and ensure proper field drainage. Avoid field operations during heavy rain."
        elif any(word in query_lower for word in ["drought", "dry"]):
            advice = "Implement water conservation measures. Consider drought-resistant varieties and efficient irrigation."
        elif any(word in query_lower for word in ["temperature", "heat", "cold"]):
            advice = "Monitor temperature fluctuations. Protect crops from extreme heat or cold stress."
        elif any(word in query_lower for word in ["irrigation", "water"]):
            advice = "Schedule irrigation based on soil moisture and weather conditions. Avoid overwatering."
        else:
            advice = "Stay updated with local weather forecasts and adjust agricultural practices accordingly."
        
        # Add crop-specific advice if applicable
        if crop:
            if crop.lower() == "rice":
                advice += " For rice: Maintain proper water levels and monitor for disease risks."
            elif crop.lower() == "wheat":
                advice += " For wheat: Ensure adequate moisture during critical growth stages."
            elif crop.lower() == "cotton":
                advice += " For cotton: Monitor for pest and disease risks, especially during humid conditions."
        
        return {
            "agent": self.name,
            "result": {
                "advice": advice,
                "urgency": "medium",
                "location": location or "general area"
            },
            "evidence": [
                {
                    "source": "general_agricultural_guidelines",
                    "excerpt": advice,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "geo": location or "general",
                    "crop": crop or "all"
                }
            ],
            "confidence": 0.6  # Lower confidence for fallback
        }