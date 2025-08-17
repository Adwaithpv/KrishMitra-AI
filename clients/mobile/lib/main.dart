import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/home_screen.dart';
import 'screens/history_screen.dart';
import 'screens/settings_screen.dart';
import 'providers/agri_provider.dart';
import 'providers/weather_provider.dart';
import 'package:google_fonts/google_fonts.dart';

void main() {
  runApp(const AgriAdvisorApp());
}

class AgriAdvisorApp extends StatelessWidget {
  const AgriAdvisorApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (context) => AgriProvider()),
        ChangeNotifierProvider(create: (context) => WeatherProvider()),
      ],
      child: MaterialApp(
        title: 'Agri Advisor',
        theme: _buildTheme(),
        home: const _LocationInitializer(child: MainScreen()),
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _LocationInitializer extends StatefulWidget {
  final Widget child;
  
  const _LocationInitializer({required this.child});

  @override
  State<_LocationInitializer> createState() => _LocationInitializerState();
}

class _LocationInitializerState extends State<_LocationInitializer> {
  @override
  void initState() {
    super.initState();
    // Initialize location detection when app starts
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeLocation();
    });
  }

  Future<void> _initializeLocation() async {
    final agriProvider = Provider.of<AgriProvider>(context, listen: false);
    final weatherProvider = Provider.of<WeatherProvider>(context, listen: false);
    
    // Initialize both providers in parallel
    await Future.wait([
      agriProvider.initializeLocation(),
      weatherProvider.initializeWeather(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;
  
  final List<Widget> _screens = [
    const HomeScreen(),
    const HistoryScreen(),
    const SettingsScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: AnimatedSwitcher(
        duration: const Duration(milliseconds: 300),
        child: _screens[_currentIndex],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.history_outlined),
            selectedIcon: Icon(Icons.history),
            label: 'History',
          ),
          NavigationDestination(
            icon: Icon(Icons.settings_outlined),
            selectedIcon: Icon(Icons.settings),
            label: 'Settings',
          ),
        ],
      ),
    );
  }
}

ThemeData _buildTheme() {
  final ColorScheme colorScheme = ColorScheme.fromSeed(
    seedColor: const Color(0xFF2E7D32),
    brightness: Brightness.light,
  );

  return ThemeData(
    useMaterial3: true,
    colorScheme: colorScheme,
    textTheme: GoogleFonts.manropeTextTheme(),
    scaffoldBackgroundColor: colorScheme.surface,
    appBarTheme: AppBarTheme(
      backgroundColor: colorScheme.primary,
      foregroundColor: colorScheme.onPrimary,
      elevation: 0,
      centerTitle: false,
      titleTextStyle: GoogleFonts.manrope(
        fontSize: 20,
        fontWeight: FontWeight.w700,
        color: colorScheme.onPrimary,
      ),
    ),
    cardTheme: CardTheme(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: EdgeInsets.zero,
      clipBehavior: Clip.antiAlias,
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: colorScheme.surfaceVariant.withOpacity(0.35),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.outlineVariant),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.outlineVariant),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(color: colorScheme.primary, width: 1.5),
      ),
      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
    ),
    navigationBarTheme: const NavigationBarThemeData(
      // Keep minimal to avoid SDK-specific state property types
      elevation: 1,
    ),
    snackBarTheme: SnackBarThemeData(
      behavior: SnackBarBehavior.floating,
      backgroundColor: colorScheme.inverseSurface,
      contentTextStyle: TextStyle(color: colorScheme.onInverseSurface),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
  );
}
