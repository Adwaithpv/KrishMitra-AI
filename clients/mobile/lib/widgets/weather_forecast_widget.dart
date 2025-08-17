import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../providers/weather_provider.dart';
import '../models/weather_models.dart';

class WeatherForecastWidget extends StatefulWidget {
  const WeatherForecastWidget({super.key});

  @override
  State<WeatherForecastWidget> createState() => _WeatherForecastWidgetState();
}

class _WeatherForecastWidgetState extends State<WeatherForecastWidget> {
  @override
  void initState() {
    super.initState();
    // Initialize weather data when widget is first created
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<WeatherProvider>().initializeWeather();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<WeatherProvider>(
      builder: (context, weatherProvider, child) {
        return Card(
          margin: const EdgeInsets.all(16),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: _getBackgroundGradient(weatherProvider),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(context, weatherProvider),
                  const SizedBox(height: 16),
                  _buildContent(context, weatherProvider),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildHeader(BuildContext context, WeatherProvider provider) {
    return Row(
      children: [
        const Icon(
          Icons.cloud,
          color: Colors.white,
          size: 24,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Weather Forecast',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
              ),
              if (provider.hasData || provider.currentLocation != null)
                Text(
                  _getLocationDisplayName(provider),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.white.withOpacity(0.9),
                      ),
                ),
            ],
          ),
        ),
        _buildRefreshButton(provider),
      ],
    );
  }

  Widget _buildRefreshButton(WeatherProvider provider) {
    return IconButton(
      onPressed: provider.isLoading
          ? null
          : () => provider.refreshWeatherData(),
      icon: provider.isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
              ),
            )
          : const Icon(
              Icons.refresh,
              color: Colors.white,
            ),
      tooltip: 'Refresh weather data',
    );
  }

  Widget _buildContent(BuildContext context, WeatherProvider provider) {
    if (provider.hasError) {
      return _buildErrorState(context, provider);
    } else if (provider.isLoading && !provider.hasData) {
      return _buildLoadingState();
    } else if (provider.hasData) {
      return _buildWeatherData(context, provider);
    } else {
      return _buildEmptyState(context, provider);
    }
  }

  Widget _buildLoadingState() {
    return const SizedBox(
      height: 200,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
            SizedBox(height: 16),
            Text(
              'Getting weather forecast...',
              style: TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, WeatherProvider provider) {
    return SizedBox(
      height: 200,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              color: Colors.white,
              size: 48,
            ),
            const SizedBox(height: 16),
            Text(
              provider.errorMessage ?? 'An error occurred',
              style: const TextStyle(color: Colors.white),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => provider.fetchWeatherData(),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Theme.of(context).primaryColor,
              ),
              child: const Text('Try Again'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context, WeatherProvider provider) {
    return SizedBox(
      height: 200,
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.location_off,
              color: Colors.white,
              size: 48,
            ),
            const SizedBox(height: 16),
            const Text(
              'Weather data not available',
              style: TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => provider.fetchWeatherData(),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.white,
                foregroundColor: Theme.of(context).primaryColor,
              ),
              child: const Text('Get Weather'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherData(BuildContext context, WeatherProvider provider) {
    final today = provider.todayWeather!;
    final upcoming = provider.upcomingWeather;

    return Column(
      children: [
        _buildTodayWeather(context, today, provider),
        const SizedBox(height: 16),
        _buildWeeklyForecast(context, upcoming),
        const SizedBox(height: 12),
        _buildFarmingAdvice(context, provider),
        const SizedBox(height: 8),
        _buildLastUpdated(context, provider),
      ],
    );
  }

  Widget _buildTodayWeather(BuildContext context, DailyWeather today, WeatherProvider provider) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      today.weatherIcon,
                      style: const TextStyle(fontSize: 32),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Today',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                ),
                          ),
                          Text(
                            today.condition,
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                  color: Colors.white.withOpacity(0.9),
                                ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    _buildWeatherStat(
                      Icons.thermostat,
                      '${today.avgTemp.round()}°C',
                      'Temperature',
                    ),
                    const SizedBox(width: 16),
                    _buildWeatherStat(
                      Icons.water_drop,
                      '${today.chanceOfRain.round()}%',
                      'Rain chance',
                    ),
                    const SizedBox(width: 16),
                    _buildWeatherStat(
                      Icons.air,
                      '${today.windSpeed.round()} km/h',
                      'Wind',
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherStat(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(
          icon,
          color: Colors.white,
          size: 20,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.8),
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  Widget _buildWeeklyForecast(BuildContext context, List<DailyWeather> upcoming) {
    if (upcoming.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '7-Day Forecast',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 110,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: upcoming.length,
            itemBuilder: (context, index) {
              final weather = upcoming[index];
              final dayName = DateFormat('EEE').format(weather.date);
              
              return Container(
                width: 75,
                margin: const EdgeInsets.only(right: 10),
                padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Text(
                      dayName,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                      ),
                    ),
                    Text(
                      weather.weatherIcon,
                      style: const TextStyle(fontSize: 20),
                    ),
                    Column(
                      children: [
                        Text(
                          '${weather.maxTemp.round()}°',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                        Text(
                          '${weather.minTemp.round()}°',
                          style: TextStyle(
                            color: Colors.white.withOpacity(0.7),
                            fontSize: 9,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildFarmingAdvice(BuildContext context, WeatherProvider provider) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.15),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(
            provider.isGoodFarmingWeather ? Icons.agriculture : Icons.warning,
            color: Colors.white,
            size: 20,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              provider.farmingAdvice,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLastUpdated(BuildContext context, WeatherProvider provider) {
    return Text(
      'Updated ${provider.timeSinceLastUpdate}',
      style: TextStyle(
        color: Colors.white.withOpacity(0.7),
        fontSize: 10,
      ),
    );
  }

  LinearGradient _getBackgroundGradient(WeatherProvider provider) {
    if (provider.todayWeather != null) {
      final colors = provider.todayWeather!.backgroundColors;
      return LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: colors,
      );
    }
    
    // Default gradient
    return const LinearGradient(
      begin: Alignment.topLeft,
      end: Alignment.bottomRight,
      colors: [
        Color(0xFF87CEEB),
        Color(0xFF4682B4),
      ],
    );
  }

  String _getLocationDisplayName(WeatherProvider provider) {
    // Prefer the location name from weather API (more accurate)
    if (provider.hasData && provider.currentForecast!.locationName.isNotEmpty) {
      final apiLocation = provider.currentForecast!.locationName;
      if (apiLocation != 'Unknown Location') {
        return apiLocation;
      }
    }
    
    // Fallback to GPS location name
    if (provider.currentLocation != null) {
      return provider.currentLocation!.displayName;
    }
    
    // Final fallback
    return 'Location unavailable';
  }
}
