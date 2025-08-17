# Weather Forecast Feature Setup

## Overview
The weather forecast feature provides a beautiful, interactive weather widget on the main page of the Agri Advisor app. It shows current weather conditions, 7-day forecast, and farming-specific advice based on weather conditions.

## Features
- **Current Location Detection**: Automatically gets user's location using GPS
- **7-Day Weather Forecast**: Shows daily weather predictions including temperature, precipitation, wind, and conditions
- **Beautiful UI**: Dynamic background colors that change based on weather conditions
- **Farming Advice**: Intelligent recommendations for farming activities based on weather
- **Real-time Updates**: Refresh weather data with pull-to-refresh
- **Offline Support**: Caches weather data for offline viewing

## Setup Instructions

### 1. Get Weather API Key
The app is currently configured to use mock data for demonstration. To use real weather data:

1. Sign up at [WeatherAPI.com](https://www.weatherapi.com/)
2. Get your free API key (10,000 calls/month free tier)
3. Open `lib/services/weather_service.dart`
4. Replace `YOUR_WEATHERAPI_KEY_HERE` with your actual API key
5. Set `_useMockData = false` to use real data

```dart
// In weather_service.dart
static const String _apiKey = 'your_actual_api_key_here';
static const bool _useMockData = false; // Change to false for real data
```

### 2. Platform Permissions
The necessary permissions are already configured:

**Android** (`android/app/src/main/AndroidManifest.xml`):
- `ACCESS_FINE_LOCATION` - for precise location
- `ACCESS_COARSE_LOCATION` - for approximate location
- `INTERNET` - for API calls

**iOS** (`ios/Runner/Info.plist`):
- `NSLocationWhenInUseUsageDescription` - location permission description

### 3. Dependencies
All required dependencies are already added to `pubspec.yaml`:
- `geolocator` - location services
- `geocoding` - reverse geocoding for location names
- `permission_handler` - permission management
- `intl` - date formatting
- `http` - API calls

## Usage

### First Time Setup
1. When the app first launches, it will request location permission
2. Users need to grant location access for weather features to work
3. The app will automatically fetch weather data for their location

### User Experience
- **Loading State**: Shows spinner while fetching location and weather data
- **Error Handling**: Clear error messages with retry options
- **Permission Denied**: Guides users to enable location in settings
- **Offline Mode**: Shows cached data when network is unavailable

### Weather Widget Components
1. **Today's Weather**: Large card showing current conditions, temperature, rain chance, and wind
2. **7-Day Forecast**: Horizontal scrollable list of upcoming days
3. **Farming Advice**: Context-aware recommendations based on weather conditions
4. **Last Updated**: Shows when data was last refreshed

## Customization

### Weather Conditions
Weather conditions are mapped to emoji icons and background gradients in `weather_models.dart`:
- ☀️ Sunny/Clear
- ⛅ Partly Cloudy
- ☁️ Cloudy/Overcast
- 🌧️ Rain/Drizzle
- ⛈️ Thunderstorms
- ❄️ Snow
- 🌫️ Fog/Mist
- 💨 Windy

### Background Colors
Dynamic gradients change based on weather:
- Sunny: Sky blue to gold
- Cloudy: Gray tones
- Rainy: Steel blue to midnight blue
- Stormy: Dark gray to black

### Farming Advice Logic
The app provides intelligent farming advice based on:
- Rain probability (>70% suggests indoor activities)
- Wind speed (>20 km/h warns about spraying/harvesting)
- Temperature extremes (<5°C or >35°C)
- Combined conditions for optimal farming weather

## Troubleshooting

### Location Issues
- **Permission Denied**: Guide users to app settings
- **Location Services Disabled**: Prompt to enable in device settings
- **Poor GPS Signal**: Falls back to network location

### API Issues
- **Rate Limiting**: WeatherAPI.com has 10,000 calls/month limit
- **Network Errors**: App shows cached data and retry options
- **Invalid API Key**: Clear error message to check configuration

### Performance
- Weather data is cached for 30 minutes to reduce API calls
- Location is cached to avoid repeated GPS requests
- Images and icons are optimized for performance

## Development Notes

### Mock Data
The app includes comprehensive mock weather data for testing:
- Varied weather conditions across 7 days
- Realistic temperature ranges
- Different precipitation and wind patterns

### Testing
Test different scenarios:
1. First app launch (permission flow)
2. Permission denied scenarios
3. Network connectivity issues
4. Location services disabled
5. API errors and rate limiting

### Future Enhancements
- Weather alerts and notifications
- Hourly forecasts
- Agricultural weather indices (UV index, soil moisture prediction)
- Integration with farming calendar
- Weather-based crop recommendations

## API Reference

### WeatherAPI.com Endpoints
- **Current + Forecast**: `/v1/forecast.json`
- **Parameters**: 
  - `key`: API key
  - `q`: lat,lon coordinates
  - `days`: Number of forecast days (1-7)
  - `aqi`: Air quality data (no)
  - `alerts`: Weather alerts (no)

### Response Format
```json
{
  "location": {
    "name": "Location Name",
    "lat": 12.34,
    "lon": 56.78
  },
  "current": {
    "last_updated": "2024-01-01 12:00",
    "temp_c": 25.0,
    "condition": {
      "text": "Sunny",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/116.png"
    }
  },
  "forecast": {
    "forecastday": [...]
  }
}
```
