"""
Real-time data integration service for weather and market data.
"""
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class WeatherData:
    location: str
    temperature: float
    humidity: float
    rainfall: float
    wind_speed: float
    forecast: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class MarketData:
    crop: str
    location: str
    price: float
    unit: str
    change: float
    volume: Optional[float]
    timestamp: datetime

class RealTimeDataService:
    def __init__(self):
        self.weather_cache = {}
        self.market_cache = {}
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
        
        # API keys (should be in environment variables)
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "")
        self.market_api_key = os.getenv("MARKET_API_KEY", "")
        
        # Mock data for development
        self.mock_weather_data = {
            "Punjab": {
                "temperature": 28.5,
                "humidity": 65,
                "rainfall": 0.0,
                "wind_speed": 12.0,
                "forecast": [
                    {"date": "2024-01-15", "temp": 29, "rain": 0},
                    {"date": "2024-01-16", "temp": 27, "rain": 5},
                    {"date": "2024-01-17", "temp": 26, "rain": 15}
                ]
            },
            "Maharashtra": {
                "temperature": 32.0,
                "humidity": 55,
                "rainfall": 0.0,
                "wind_speed": 8.0,
                "forecast": [
                    {"date": "2024-01-15", "temp": 33, "rain": 0},
                    {"date": "2024-01-16", "temp": 31, "rain": 0},
                    {"date": "2024-01-17", "temp": 30, "rain": 2}
                ]
            }
        }
        
        self.mock_market_data = {
            "wheat": {
                "Punjab": {"price": 2100, "change": 50, "volume": 1000},
                "Maharashtra": {"price": 2200, "change": -30, "volume": 800}
            },
            "rice": {
                "Punjab": {"price": 1800, "change": 20, "volume": 1200},
                "Maharashtra": {"price": 1900, "change": 40, "volume": 900}
            },
            "cotton": {
                "Punjab": {"price": 6500, "change": -100, "volume": 500},
                "Maharashtra": {"price": 6800, "change": 150, "volume": 600}
            }
        }
    
    async def get_weather_data(self, location: str) -> Optional[WeatherData]:
        """Get weather data for a location"""
        # Check cache first
        cache_key = f"weather_{location}"
        if cache_key in self.weather_cache:
            cached_data, timestamp = self.weather_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # Try real API first
            if self.weather_api_key:
                weather_data = await self._fetch_weather_api(location)
            else:
                # Use mock data
                weather_data = await self._get_mock_weather(location)
            
            if weather_data:
                self.weather_cache[cache_key] = (weather_data, datetime.now())
                return weather_data
                
        except Exception as e:
            logger.error(f"Error fetching weather data for {location}: {e}")
        
        return None
    
    async def get_market_data(self, crop: str, location: str = None) -> List[MarketData]:
        """Get market data for a crop"""
        cache_key = f"market_{crop}_{location or 'all'}"
        if cache_key in self.market_cache:
            cached_data, timestamp = self.market_cache[cache_key]
            if datetime.now() - timestamp < self.cache_duration:
                return cached_data
        
        try:
            # Try real API first
            if self.market_api_key:
                market_data = await self._fetch_market_api(crop, location)
            else:
                # Use mock data
                market_data = await self._get_mock_market(crop, location)
            
            if market_data:
                self.market_cache[cache_key] = (market_data, datetime.now())
                return market_data
                
        except Exception as e:
            logger.error(f"Error fetching market data for {crop}: {e}")
        
        return []
    
    async def _fetch_weather_api(self, location: str) -> Optional[WeatherData]:
        """Fetch weather data from external API"""
        # This is a placeholder for real weather API integration
        # You would integrate with OpenWeatherMap, WeatherAPI, etc.
        async with aiohttp.ClientSession() as session:
            # Example API call (replace with actual weather API)
            url = f"https://api.weatherapi.com/v1/current.json"
            params = {
                "key": self.weather_api_key,
                "q": location,
                "aqi": "no"
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return WeatherData(
                            location=location,
                            temperature=data["current"]["temp_c"],
                            humidity=data["current"]["humidity"],
                            rainfall=data["current"].get("precip_mm", 0),
                            wind_speed=data["current"]["wind_kph"],
                            forecast=[],  # Would need separate forecast API call
                            timestamp=datetime.now()
                        )
            except Exception as e:
                logger.error(f"Weather API error: {e}")
        
        return None
    
    async def _fetch_market_api(self, crop: str, location: str = None) -> List[MarketData]:
        """Fetch market data from external API"""
        # This is a placeholder for real market API integration
        # You would integrate with NCDEX, MCX, or government price APIs
        async with aiohttp.ClientSession() as session:
            # Example API call (replace with actual market API)
            url = "https://api.agmarknet.gov.in/api/v1/prices"
            params = {
                "api_key": self.market_api_key,
                "commodity": crop,
                "state": location or "all"
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = []
                        for item in data.get("prices", []):
                            market_data.append(MarketData(
                                crop=crop,
                                location=item["state"],
                                price=float(item["price"]),
                                unit=item["unit"],
                                change=float(item.get("change", 0)),
                                volume=float(item.get("volume", 0)),
                                timestamp=datetime.now()
                            ))
                        return market_data
            except Exception as e:
                logger.error(f"Market API error: {e}")
        
        return []
    
    async def _get_mock_weather(self, location: str) -> Optional[WeatherData]:
        """Get mock weather data for development"""
        if location in self.mock_weather_data:
            data = self.mock_weather_data[location]
            return WeatherData(
                location=location,
                temperature=data["temperature"],
                humidity=data["humidity"],
                rainfall=data["rainfall"],
                wind_speed=data["wind_speed"],
                forecast=data["forecast"],
                timestamp=datetime.now()
            )
        return None
    
    async def _get_mock_market(self, crop: str, location: str = None) -> List[MarketData]:
        """Get mock market data for development"""
        market_data = []
        
        if crop in self.mock_market_data:
            locations = [location] if location else self.mock_market_data[crop].keys()
            
            for loc in locations:
                if loc in self.mock_market_data[crop]:
                    data = self.mock_market_data[crop][loc]
                    market_data.append(MarketData(
                        crop=crop,
                        location=loc,
                        price=data["price"],
                        unit="quintal",
                        change=data["change"],
                        volume=data["volume"],
                        timestamp=datetime.now()
                    ))
        
        return market_data
    
    def get_weather_advice(self, location: str, crop: str = None) -> str:
        """Generate weather-based agricultural advice"""
        weather_data = asyncio.run(self.get_weather_data(location))
        
        if not weather_data:
            return f"Weather data not available for {location}"
        
        advice_parts = []
        
        # Temperature advice
        if weather_data.temperature > 35:
            advice_parts.append("High temperature alert: Consider shade nets and frequent irrigation.")
        elif weather_data.temperature < 15:
            advice_parts.append("Low temperature: Protect crops with mulching and row covers.")
        
        # Rainfall advice
        if weather_data.rainfall > 10:
            advice_parts.append("Heavy rainfall expected: Ensure proper drainage and avoid spraying.")
        elif weather_data.rainfall < 1 and weather_data.humidity < 50:
            advice_parts.append("Dry conditions: Increase irrigation frequency.")
        
        # Wind advice
        if weather_data.wind_speed > 20:
            advice_parts.append("High winds: Secure structures and avoid aerial spraying.")
        
        # Crop-specific advice
        if crop:
            if crop.lower() == "wheat" and weather_data.temperature > 30:
                advice_parts.append("Wheat: High temperature may affect grain filling. Monitor closely.")
            elif crop.lower() == "rice" and weather_data.rainfall < 5:
                advice_parts.append("Rice: Low rainfall may require additional irrigation.")
        
        if not advice_parts:
            advice_parts.append("Weather conditions are favorable for agricultural activities.")
        
        return " ".join(advice_parts)
    
    def get_market_advice(self, crop: str, location: str = None) -> str:
        """Generate market-based agricultural advice"""
        market_data = asyncio.run(self.get_market_data(crop, location))
        
        if not market_data:
            return f"Market data not available for {crop}"
        
        # Analyze price trends
        avg_price = sum(d.price for d in market_data) / len(market_data)
        avg_change = sum(d.change for d in market_data) / len(market_data)
        
        advice_parts = []
        
        if avg_change > 50:
            advice_parts.append(f"Strong upward trend: {crop} prices increased by ₹{avg_change:.0f}/quintal.")
        elif avg_change < -50:
            advice_parts.append(f"Declining trend: {crop} prices decreased by ₹{abs(avg_change):.0f}/quintal.")
        else:
            advice_parts.append(f"Stable prices: {crop} prices are relatively stable.")
        
        # Price level advice
        if avg_price > 2500:
            advice_parts.append("Current prices are above average - good time for selling.")
        elif avg_price < 1500:
            advice_parts.append("Prices are below average - consider holding if storage is available.")
        
        # Location-specific advice
        if location and any(d.location == location for d in market_data):
            loc_data = next(d for d in market_data if d.location == location)
            advice_parts.append(f"In {location}: ₹{loc_data.price}/quintal (change: ₹{loc_data.change})")
        
        return " ".join(advice_parts)
    
    async def update_cache(self):
        """Update all cached data"""
        logger.info("Updating real-time data cache...")
        
        # Update weather cache for common locations
        common_locations = ["Punjab", "Maharashtra", "Karnataka", "Tamil Nadu"]
        for location in common_locations:
            await self.get_weather_data(location)
        
        # Update market cache for common crops
        common_crops = ["wheat", "rice", "cotton", "sugarcane"]
        for crop in common_crops:
            await self.get_market_data(crop)
        
        logger.info("Cache update completed")

