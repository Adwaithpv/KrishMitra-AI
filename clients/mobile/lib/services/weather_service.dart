import 'dart:convert';
import 'package:geolocator/geolocator.dart';
import 'package:geocoding/geocoding.dart';
import 'package:http/http.dart' as http;

import '../models/weather_models.dart';

class WeatherService {
  // Replace 'your_api_key_here' with your actual WeatherAPI.com API key
  static const String _apiKey = '49197751d7fa46cda81192655250908';
  static const String _baseUrl = 'https://api.weatherapi.com/v1';
  
  // Set to false to use real weather data, true for mock data
  static const bool _useMockData = false;

  /// Get user's current location with permission handling
  Future<UserLocation?> getCurrentLocation() async {
    try {
      print('📍 Starting location detection...');
      
      // Check if location services are enabled
      bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
      print('🛰️ Location services enabled: $serviceEnabled');
      if (!serviceEnabled) {
        throw Exception('Location services are disabled. Please enable them in settings.');
      }

      // Request location permission
      LocationPermission permission = await Geolocator.checkPermission();
      print('🔐 Initial permission status: $permission');
      
      if (permission == LocationPermission.denied) {
        print('🔐 Requesting location permission...');
        permission = await Geolocator.requestPermission();
        print('🔐 Permission after request: $permission');
        if (permission == LocationPermission.denied) {
          throw Exception('Location permission denied. Please grant location access to get weather updates.');
        }
      }

      if (permission == LocationPermission.deniedForever) {
        throw Exception('Location permissions are permanently denied. Please enable them in app settings.');
      }

      print('📡 Getting GPS position...');
      // Get current position
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
        timeLimit: const Duration(seconds: 10),
      );
      
      print('✅ Got GPS coordinates: ${position.latitude}, ${position.longitude}');

      // Get location details using reverse geocoding
      try {
        print('🗺️ Getting location name...');
        List<Placemark> placemarks = await placemarkFromCoordinates(
          position.latitude,
          position.longitude,
        );
        
        if (placemarks.isNotEmpty) {
          Placemark place = placemarks.first;
          print('🏠 Location resolved: ${place.locality ?? 'Unknown'}, ${place.administrativeArea ?? 'Unknown'}, ${place.country ?? 'Unknown'}');

          return UserLocation(
            latitude: position.latitude,
            longitude: position.longitude,
            locality: place.locality,
            country: place.country,
            administrativeArea: place.administrativeArea,
          );
        } else {
          print('⚠️ No placemark data returned');
          return UserLocation(
            latitude: position.latitude,
            longitude: position.longitude,
          );
        }
      } catch (e) {
        print('⚠️ Reverse geocoding failed: $e');
        // If reverse geocoding fails, still return location with coordinates
        return UserLocation(
          latitude: position.latitude,
          longitude: position.longitude,
        );
      }
    } catch (e) {
      print('Error getting location: $e');
      return null;
    }
  }

  /// Fetch weather forecast for given location
  Future<WeatherApiResponse> getWeatherForecast(UserLocation location) async {
    try {
      print('🌍 Using location: ${location.latitude}, ${location.longitude} (${location.displayName})');
      
      if (_useMockData) {
        print('📱 Using mock weather data');
        // Return mock data for demo purposes
        return _getMockWeatherData(location);
      }

      print('🌐 Fetching real weather data from API...');
      final url = Uri.parse(
        '$_baseUrl/forecast.json?key=$_apiKey&q=${location.latitude},${location.longitude}&days=7&aqi=no&alerts=no',
      );
      
      print('🔗 API URL: $url');

      final response = await http.get(url).timeout(
        const Duration(seconds: 10),
      );

      print('📡 API Response Status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final locationFromAPI = data['location']?['name'] ?? 'Unknown Location';
        print('✅ Weather data received successfully for: $locationFromAPI');
        final forecast = WeatherForecast.fromJson(data);
        return WeatherApiResponse.success(forecast);
      } else {
        print('❌ API Error: ${response.statusCode} - ${response.body}');
        final errorData = json.decode(response.body);
        return WeatherApiResponse.error(
          errorData['error']['message'] ?? 'Failed to fetch weather data',
        );
      }
    } catch (e) {
      return WeatherApiResponse.error('Network error: ${e.toString()}');
    }
  }

  /// Get cached weather data (for offline usage)
  Future<WeatherForecast?> getCachedWeatherData() async {
    // In a real app, you would implement SharedPreferences caching here
    // For now, return null
    return null;
  }

  /// Cache weather data locally
  Future<void> cacheWeatherData(WeatherForecast forecast) async {
    // In a real app, you would implement SharedPreferences caching here
    // For now, do nothing
  }

  /// Mock weather data for demo purposes
  WeatherApiResponse _getMockWeatherData(UserLocation location) {
    final now = DateTime.now();
    final dailyForecasts = List.generate(7, (index) {
      final date = now.add(Duration(days: index));
      final isToday = index == 0;
      
      // Create varied weather conditions
      final conditions = [
        'Sunny',
        'Partly cloudy',
        'Cloudy',
        'Light rain',
        'Heavy rain',
        'Thunderstorm',
        'Clear',
      ];
      
      final condition = conditions[index % conditions.length];
      final baseTemp = 25.0;
      final tempVariation = (index * 2.0) - 6.0;
      
      return DailyWeather(
        date: date,
        maxTemp: baseTemp + tempVariation + 5,
        minTemp: baseTemp + tempVariation - 3,
        avgTemp: baseTemp + tempVariation,
        condition: condition,
        conditionIcon: '', // Will use emoji from weatherIcon getter
        chanceOfRain: condition.contains('rain') ? 80.0 : condition.contains('cloud') ? 30.0 : 10.0,
        humidity: 60.0 + (index * 5.0),
        windSpeed: 10.0 + (index * 2.0),
        windDirection: ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W'][index],
        uvIndex: isToday ? 6.0 : 5.0 + index.toDouble(),
        visibility: 10.0 - index.toDouble(),
        hourlyForecast: [], // Simplified for demo
      );
    });

    final forecast = WeatherForecast(
      locationName: location.displayName,
      latitude: location.latitude,
      longitude: location.longitude,
      lastUpdated: now,
      dailyForecast: dailyForecasts,
    );

    return WeatherApiResponse.success(forecast);
  }

  /// Check if location permission is granted
  Future<bool> isLocationPermissionGranted() async {
    LocationPermission permission = await Geolocator.checkPermission();
    return permission == LocationPermission.whileInUse || 
           permission == LocationPermission.always;
  }

  /// Open app settings for manual permission grant
  Future<void> openLocationSettings() async {
    await Geolocator.openAppSettings();
  }

  /// Get location permission status as human-readable string
  Future<String> getLocationPermissionStatus() async {
    LocationPermission permission = await Geolocator.checkPermission();
    switch (permission) {
      case LocationPermission.denied:
        return 'Location access denied';
      case LocationPermission.deniedForever:
        return 'Location access permanently denied';
      case LocationPermission.whileInUse:
        return 'Location access granted while using app';
      case LocationPermission.always:
        return 'Location access always granted';
      default:
        return 'Unknown location permission status';
    }
  }
}
