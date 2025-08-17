import 'package:flutter/foundation.dart';
import '../models/weather_models.dart';
import '../services/weather_service.dart';

enum WeatherLoadingState {
  idle,
  loadingLocation,
  loadingWeather,
  loaded,
  error,
}

class WeatherProvider with ChangeNotifier {
  final WeatherService _weatherService = WeatherService();
  
  WeatherLoadingState _loadingState = WeatherLoadingState.idle;
  WeatherForecast? _currentForecast;
  UserLocation? _currentLocation;
  String? _errorMessage;
  DateTime? _lastUpdated;

  // Getters
  WeatherLoadingState get loadingState => _loadingState;
  WeatherForecast? get currentForecast => _currentForecast;
  UserLocation? get currentLocation => _currentLocation;
  String? get errorMessage => _errorMessage;
  DateTime? get lastUpdated => _lastUpdated;
  
  bool get isLoading => _loadingState == WeatherLoadingState.loadingLocation || 
                      _loadingState == WeatherLoadingState.loadingWeather;
  
  bool get hasData => _currentForecast != null && _currentLocation != null;
  
  bool get hasError => _loadingState == WeatherLoadingState.error && _errorMessage != null;

  // Get today's weather if available
  DailyWeather? get todayWeather {
    if (_currentForecast == null || _currentForecast!.dailyForecast.isEmpty) {
      return null;
    }
    return _currentForecast!.dailyForecast.first;
  }

  // Get upcoming days weather (excluding today)
  List<DailyWeather> get upcomingWeather {
    if (_currentForecast == null || _currentForecast!.dailyForecast.length <= 1) {
      return [];
    }
    return _currentForecast!.dailyForecast.skip(1).toList();
  }

  /// Initialize weather data - gets location and fetches weather
  Future<void> initializeWeather() async {
    await fetchWeatherData();
  }

  /// Fetch weather data for current location
  Future<void> fetchWeatherData() async {
    try {
      _setLoadingState(WeatherLoadingState.loadingLocation);
      _clearError();

      // Get current location
      final location = await _weatherService.getCurrentLocation();
      if (location == null) {
        _setError('Unable to get your location. Please check your location settings.');
        return;
      }

      _currentLocation = location;
      _setLoadingState(WeatherLoadingState.loadingWeather);

      // Fetch weather data
      final response = await _weatherService.getWeatherForecast(location);
      
      if (response.success && response.forecast != null) {
        _currentForecast = response.forecast;
        _lastUpdated = DateTime.now();
        _setLoadingState(WeatherLoadingState.loaded);
        
        // Cache the data
        await _weatherService.cacheWeatherData(response.forecast!);
      } else {
        _setError(response.error ?? 'Failed to fetch weather data');
      }
    } catch (e) {
      _setError('An unexpected error occurred: ${e.toString()}');
    }
  }

  /// Refresh weather data
  Future<void> refreshWeatherData() async {
    await fetchWeatherData();
  }

  /// Load cached weather data if available
  Future<void> loadCachedWeatherData() async {
    try {
      final cachedForecast = await _weatherService.getCachedWeatherData();
      if (cachedForecast != null) {
        _currentForecast = cachedForecast;
        _lastUpdated = cachedForecast.lastUpdated;
        _setLoadingState(WeatherLoadingState.loaded);
      }
    } catch (e) {
      print('Error loading cached weather data: $e');
    }
  }

  /// Check if data needs refresh (older than 30 minutes)
  bool get needsRefresh {
    if (_lastUpdated == null) return true;
    final now = DateTime.now();
    final difference = now.difference(_lastUpdated!);
    return difference.inMinutes > 30;
  }

  /// Get weather for specific day index (0 = today, 1 = tomorrow, etc.)
  DailyWeather? getWeatherForDay(int dayIndex) {
    if (_currentForecast == null || 
        dayIndex < 0 || 
        dayIndex >= _currentForecast!.dailyForecast.length) {
      return null;
    }
    return _currentForecast!.dailyForecast[dayIndex];
  }

  /// Check location permission status
  Future<bool> checkLocationPermission() async {
    return await _weatherService.isLocationPermissionGranted();
  }

  /// Open location settings
  Future<void> openLocationSettings() async {
    await _weatherService.openLocationSettings();
  }

  /// Get location permission status message
  Future<String> getLocationPermissionStatusMessage() async {
    return await _weatherService.getLocationPermissionStatus();
  }

  /// Set loading state and notify listeners
  void _setLoadingState(WeatherLoadingState state) {
    _loadingState = state;
    notifyListeners();
  }

  /// Set error message and loading state
  void _setError(String message) {
    _errorMessage = message;
    _loadingState = WeatherLoadingState.error;
    notifyListeners();
  }

  /// Clear error message
  void _clearError() {
    _errorMessage = null;
  }

  /// Clear all data
  void clearData() {
    _currentForecast = null;
    _currentLocation = null;
    _errorMessage = null;
    _lastUpdated = null;
    _loadingState = WeatherLoadingState.idle;
    notifyListeners();
  }

  /// Get human-readable time since last update
  String get timeSinceLastUpdate {
    if (_lastUpdated == null) return 'Never updated';
    
    final now = DateTime.now();
    final difference = now.difference(_lastUpdated!);
    
    if (difference.inMinutes < 1) {
      return 'Just now';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes}m ago';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago';
    } else {
      return '${difference.inDays}d ago';
    }
  }

  /// Get summary of current weather conditions
  String get currentWeatherSummary {
    final today = todayWeather;
    if (today == null) return 'Weather data not available';
    
    return '${today.condition}, ${today.avgTemp.round()}°C';
  }

  /// Check if it's a good day for farming activities
  bool get isGoodFarmingWeather {
    final today = todayWeather;
    if (today == null) return false;
    
    // Consider it good farming weather if:
    // - No heavy rain (chance of rain < 70%)
    // - Not too windy (wind speed < 20 km/h)
    // - Reasonable temperature (between 5°C and 35°C)
    return today.chanceOfRain < 70.0 && 
           today.windSpeed < 20.0 && 
           today.avgTemp >= 5.0 && 
           today.avgTemp <= 35.0;
  }

  /// Get farming advice based on current weather
  String get farmingAdvice {
    final today = todayWeather;
    if (today == null) return 'Check weather conditions before farming activities.';
    
    if (today.chanceOfRain >= 70) {
      return 'High chance of rain. Consider indoor activities or postpone field work.';
    } else if (today.windSpeed >= 20) {
      return 'Windy conditions. Be cautious with spraying and harvesting activities.';
    } else if (today.avgTemp < 5) {
      return 'Cold weather. Protect sensitive crops and limit outdoor activities.';
    } else if (today.avgTemp > 35) {
      return 'Very hot weather. Ensure proper irrigation and worker safety.';
    } else if (isGoodFarmingWeather) {
      return 'Good weather for farming activities. Consider field work and maintenance.';
    } else {
      return 'Monitor weather conditions and plan activities accordingly.';
    }
  }
}
