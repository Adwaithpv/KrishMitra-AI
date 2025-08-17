import 'package:flutter/material.dart';

class WeatherForecast {
  final String locationName;
  final double latitude;
  final double longitude;
  final DateTime lastUpdated;
  final List<DailyWeather> dailyForecast;

  WeatherForecast({
    required this.locationName,
    required this.latitude,
    required this.longitude,
    required this.lastUpdated,
    required this.dailyForecast,
  });

  factory WeatherForecast.fromJson(Map<String, dynamic> json) {
    try {
      // Build location name from API response
      String locationName = 'Unknown Location';
      if (json['location'] != null) {
        final location = json['location'];
        final name = location['name']?.toString() ?? '';
        final region = location['region']?.toString() ?? '';
        final country = location['country']?.toString() ?? '';
        
        List<String> locationParts = [];
        if (name.isNotEmpty) locationParts.add(name);
        if (region.isNotEmpty && region != name) locationParts.add(region);
        if (country.isNotEmpty && country != region) locationParts.add(country);
        
        if (locationParts.isNotEmpty) {
          locationName = locationParts.join(', ');
        }
      }
      
      return WeatherForecast(
        locationName: locationName,
        latitude: json['location']?['lat']?.toDouble() ?? 0.0,
        longitude: json['location']?['lon']?.toDouble() ?? 0.0,
        lastUpdated: DateTime.tryParse(json['current']?['last_updated'] ?? '') ?? DateTime.now(),
        dailyForecast: (json['forecast']?['forecastday'] as List? ?? [])
            .map((day) => DailyWeather.fromJson(day))
            .toList(),
      );
    } catch (e) {
      throw FormatException('Error parsing weather data: $e');
    }
  }
}

class DailyWeather {
  final DateTime date;
  final double maxTemp;
  final double minTemp;
  final double avgTemp;
  final String condition;
  final String conditionIcon;
  final double chanceOfRain;
  final double humidity;
  final double windSpeed;
  final String windDirection;
  final double uvIndex;
  final double visibility;
  final HourlyWeather? currentHour;
  final List<HourlyWeather> hourlyForecast;

  DailyWeather({
    required this.date,
    required this.maxTemp,
    required this.minTemp,
    required this.avgTemp,
    required this.condition,
    required this.conditionIcon,
    required this.chanceOfRain,
    required this.humidity,
    required this.windSpeed,
    required this.windDirection,
    required this.uvIndex,
    required this.visibility,
    this.currentHour,
    this.hourlyForecast = const [],
  });

  factory DailyWeather.fromJson(Map<String, dynamic> json) {
    try {
      final day = json['day'] ?? {};
      
      return DailyWeather(
        date: DateTime.tryParse(json['date'] ?? '') ?? DateTime.now(),
        maxTemp: day['maxtemp_c']?.toDouble() ?? 25.0,
        minTemp: day['mintemp_c']?.toDouble() ?? 15.0,
        avgTemp: day['avgtemp_c']?.toDouble() ?? 20.0,
        condition: day['condition']?['text'] ?? 'Unknown',
        conditionIcon: day['condition']?['icon'] ?? '',
        chanceOfRain: day['daily_chance_of_rain']?.toDouble() ?? 0.0,
        humidity: day['avghumidity']?.toDouble() ?? 60.0,
        windSpeed: day['maxwind_kph']?.toDouble() ?? 10.0,
        windDirection: '', // Not available in daily summary
        uvIndex: day['uv']?.toDouble() ?? 5.0,
        visibility: day['avgvis_km']?.toDouble() ?? 10.0,
        hourlyForecast: (json['hour'] as List<dynamic>?)
            ?.map((hour) => HourlyWeather.fromJson(hour))
            .toList() ?? [],
      );
    } catch (e) {
      // Return a default weather object if parsing fails
      return DailyWeather(
        date: DateTime.now(),
        maxTemp: 25.0,
        minTemp: 15.0,
        avgTemp: 20.0,
        condition: 'Unknown',
        conditionIcon: '',
        chanceOfRain: 0.0,
        humidity: 60.0,
        windSpeed: 10.0,
        windDirection: '',
        uvIndex: 5.0,
        visibility: 10.0,
      );
    }
  }

  // Helper method to get weather icon based on condition
  String get weatherIcon {
    final condition = this.condition.toLowerCase();
    if (condition.contains('sunny') || condition.contains('clear')) {
      return '☀️';
    } else if (condition.contains('partly cloudy')) {
      return '⛅';
    } else if (condition.contains('cloudy') || condition.contains('overcast')) {
      return '☁️';
    } else if (condition.contains('rain') || condition.contains('drizzle')) {
      return '🌧️';
    } else if (condition.contains('storm') || condition.contains('thunder')) {
      return '⛈️';
    } else if (condition.contains('snow')) {
      return '❄️';
    } else if (condition.contains('fog') || condition.contains('mist')) {
      return '🌫️';
    } else if (condition.contains('wind')) {
      return '💨';
    }
    return '🌤️'; // Default
  }

  // Get background gradient colors based on weather condition
  List<Color> get backgroundColors {
    final condition = this.condition.toLowerCase();
    if (condition.contains('sunny') || condition.contains('clear')) {
      return [const Color(0xFF87CEEB), const Color(0xFFFFD700)]; // Sky blue to gold
    } else if (condition.contains('partly cloudy')) {
      return [const Color(0xFF87CEEB), const Color(0xFFB0C4DE)]; // Sky blue to light steel blue
    } else if (condition.contains('cloudy') || condition.contains('overcast')) {
      return [const Color(0xFF708090), const Color(0xFF2F4F4F)]; // Slate gray to dark slate gray
    } else if (condition.contains('rain') || condition.contains('drizzle')) {
      return [const Color(0xFF4682B4), const Color(0xFF191970)]; // Steel blue to midnight blue
    } else if (condition.contains('storm') || condition.contains('thunder')) {
      return [const Color(0xFF2F4F4F), const Color(0xFF000000)]; // Dark slate gray to black
    } else if (condition.contains('snow')) {
      return [const Color(0xFFF0F8FF), const Color(0xFFB0C4DE)]; // Alice blue to light steel blue
    } else if (condition.contains('fog') || condition.contains('mist')) {
      return [const Color(0xFFD3D3D3), const Color(0xFFA9A9A9)]; // Light gray to dark gray
    }
    return [const Color(0xFF87CEEB), const Color(0xFF4682B4)]; // Default: sky blue to steel blue
  }
}

class HourlyWeather {
  final DateTime time;
  final double temperature;
  final String condition;
  final String conditionIcon;
  final double chanceOfRain;
  final double humidity;
  final double windSpeed;
  final String windDirection;

  HourlyWeather({
    required this.time,
    required this.temperature,
    required this.condition,
    required this.conditionIcon,
    required this.chanceOfRain,
    required this.humidity,
    required this.windSpeed,
    required this.windDirection,
  });

  factory HourlyWeather.fromJson(Map<String, dynamic> json) {
    return HourlyWeather(
      time: DateTime.parse(json['time']),
      temperature: json['temp_c']?.toDouble() ?? 0.0,
      condition: json['condition']['text'] ?? '',
      conditionIcon: json['condition']['icon'] ?? '',
      chanceOfRain: json['chance_of_rain']?.toDouble() ?? 0.0,
      humidity: json['humidity']?.toDouble() ?? 0.0,
      windSpeed: json['wind_kph']?.toDouble() ?? 0.0,
      windDirection: json['wind_dir'] ?? '',
    );
  }
}

// Location model for user's current location
class UserLocation {
  final double latitude;
  final double longitude;
  final String? locality;
  final String? country;
  final String? administrativeArea;

  UserLocation({
    required this.latitude,
    required this.longitude,
    this.locality,
    this.country,
    this.administrativeArea,
  });

  String get displayName {
    List<String> parts = [];
    if (locality != null && locality!.isNotEmpty) parts.add(locality!);
    if (administrativeArea != null && administrativeArea!.isNotEmpty) parts.add(administrativeArea!);
    if (country != null && country!.isNotEmpty) parts.add(country!);
    
    if (parts.isNotEmpty) {
      return parts.join(', ');
    } else {
      // Fallback to coordinates if no location name is available
      return '${latitude.toStringAsFixed(2)}, ${longitude.toStringAsFixed(2)}';
    }
  }
}

// Weather API response wrapper
class WeatherApiResponse {
  final bool success;
  final String? error;
  final WeatherForecast? forecast;

  WeatherApiResponse({
    required this.success,
    this.error,
    this.forecast,
  });

  factory WeatherApiResponse.success(WeatherForecast forecast) {
    return WeatherApiResponse(
      success: true,
      forecast: forecast,
    );
  }

  factory WeatherApiResponse.error(String error) {
    return WeatherApiResponse(
      success: false,
      error: error,
    );
  }
}
