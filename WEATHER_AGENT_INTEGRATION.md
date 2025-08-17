# Weather Agent Integration with Flutter App

## Overview
The weather agent has been enhanced to use real weather data from user coordinates and provide location-specific agricultural insights.

## Key Enhancements

### 🌍 **Real Weather Data Integration**
- Uses WeatherAPI.com to fetch current weather and 3-day forecasts
- Extracts coordinates from location strings
- Provides fallback advice when weather data is unavailable

### 📍 **Location Coordinate Support**
- Automatically extracts GPS coordinates from location strings
- Format: `"13.0449408,80.2127872"` (latitude,longitude)
- Falls back to location name if coordinates not available

### 🌾 **Crop-Specific Weather Advice**
- Rice: Drainage management, water level maintenance
- Cotton: Rain timing, boll rot prevention  
- Wheat: Temperature sensitivity, irrigation timing
- Sugarcane: Moisture requirements, drip irrigation

### ⚡ **Real-Time Weather Analysis**
- Current precipitation and humidity
- 3-day rainfall forecasts
- Temperature extremes and trends
- Wind speed and UV index
- Irrigation recommendations

## Flutter Integration

### 1. **Sending Location Data**
When the Flutter app queries the weather agent, include the user's coordinates:

```dart
// In Flutter app - agri_provider.dart
Future<void> queryWeatherAgent(String query) async {
  final weatherProvider = Provider.of<WeatherProvider>(context, listen: false);
  
  // Get user location coordinates
  String? locationString;
  if (weatherProvider.currentLocation != null) {
    final lat = weatherProvider.currentLocation!.latitude;
    final lon = weatherProvider.currentLocation!.longitude;
    locationString = "$lat,$lon";
  }
  
  // Send query to API with location
  final response = await http.post(
    Uri.parse('$apiBaseUrl/query'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({
      'text': query,
      'location': locationString,  // GPS coordinates
      'crop': selectedCrop,        // User's crop selection
    }),
  );
}
```

### 2. **Example Location Formats**
The weather agent accepts multiple location formats:

```dart
// GPS coordinates (preferred)
"13.0449408,80.2127872"

// City name
"Chennai, Tamil Nadu, India"

// Region
"Tamil Nadu, India"

// City only
"Chennai"
```

### 3. **API Response Structure**
The enhanced weather agent returns:

```json
{
  "agent": "weather_agent",
  "result": {
    "advice": "Current weather in Chennai: Partly cloudy, 28°C, 65% humidity. For rice: Good rainfall conditions. Maintain optimal water levels.",
    "urgency": "low",
    "location": "Chennai, Tamil Nadu, India"
  },
  "evidence": [{
    "source": "real_time_weather_data",
    "excerpt": "Current: 28°C (feels like 31°C). 3-day range: 24°C to 32°C",
    "date": "2024-12-19",
    "geo": "Chennai, Tamil Nadu, India",
    "crop": "rice"
  }],
  "confidence": 0.9
}
```

## Weather Query Examples

### 🌧️ **Rain Queries**
- "Will it rain tomorrow?"
- "Should I irrigate my rice field?"
- "Heavy rain expected - what should I do?"

### 🌡️ **Temperature Queries**  
- "Is it too hot for my wheat crop?"
- "Temperature forecast for this week"
- "Heat stress prevention advice"

### 💧 **Irrigation Queries**
- "When should I water my cotton field?"
- "Irrigation schedule based on weather"
- "Water conservation tips"

### 🌪️ **General Weather**
- "Weather forecast for farming"
- "Agricultural weather advisory"
- "Farming conditions today"

## Integration Benefits

### 🎯 **Location-Aware Advice**
```
Query: "irrigation advice"
Location: 13.0449408,80.2127872 (Chennai)
Result: "Plan regular irrigation - minimal rainfall (2mm) expected in Chennai over next 3 days. High temperature and low humidity increase water loss. For rice: Maintain 2-3 cm standing water."
```

### 📊 **Real-Time Data**
- Current weather conditions
- 3-day precipitation forecasts
- Temperature ranges and extremes
- Humidity and wind analysis

### 🚨 **Smart Urgency Levels**
- **High**: Extreme weather, frost risk, heavy rain
- **Medium**: Heat stress, strong winds, moderate rain
- **Low**: Normal conditions, general advice

### 🌾 **Crop Optimization**
- Rice: Water level management, drainage advice
- Cotton: Rain timing, disease prevention
- Wheat: Temperature sensitivity, irrigation timing
- Sugarcane: Moisture maintenance, efficiency tips

## Testing

Run the test script to verify integration:

```bash
cd agri-advisor/services/api
python test_weather_agent.py
```

This will test:
- ✅ Real weather data fetching
- ✅ Coordinate extraction
- ✅ Crop-specific advice generation
- ✅ Urgency assessment
- ✅ Fallback handling

## Configuration

Make sure the WeatherAPI key is configured in `weather_agent.py`:

```python
class WeatherAgent:
    def __init__(self):
        self.api_key = "49197751d7fa46cda81192655250908"  # Your API key
        self.base_url = "https://api.weatherapi.com/v1"
```

## Error Handling

The agent includes robust error handling:
- **Network failures**: Falls back to general advice
- **Invalid coordinates**: Uses location name
- **API errors**: Returns confidence-adjusted responses
- **Missing data**: Provides basic recommendations

## Expected Improvements

With location integration, users will get:
1. **Precise local weather** instead of generic advice
2. **Real-time conditions** for immediate decisions  
3. **Crop-specific guidance** based on actual weather
4. **Proactive alerts** for extreme conditions
5. **Irrigation optimization** based on rainfall forecasts

The weather agent now provides farmers with actionable, location-specific agricultural guidance powered by real weather data! 🌾🌤️
