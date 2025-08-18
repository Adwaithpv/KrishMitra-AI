import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import '../models/query_response.dart';
import '../models/chat_message.dart';
import '../models/weather_models.dart';
import '../services/weather_service.dart';

class AgriProvider with ChangeNotifier {
  static const String baseUrl = 'http://127.0.0.1:8000';
  
  bool _isLoading = false;
  String _error = '';
  List<QueryResponse> _history = [];
  List<ChatMessage> _messages = [];
  String? _userLocation; // Will be set from GPS location
  String? _userCrop;
  UserLocation? _detectedLocation; // GPS location data
  final WeatherService _weatherService = WeatherService();
  String? _sessionId;

  bool get isLoading => _isLoading;
  String get error => _error;
  List<QueryResponse> get history => _history;
  List<ChatMessage> get messages => _messages;
  Future<void> _ensureSession() async {
    if (_sessionId != null) return;
    final prefs = await SharedPreferences.getInstance();
    _sessionId = prefs.getString('session_id');
    if (_sessionId == null || _sessionId!.isEmpty) {
      _sessionId = DateTime.now().millisecondsSinceEpoch.toString();
      await prefs.setString('session_id', _sessionId!);
    }
  }

  Map<String, String> _headersWithSession() => {
        'X-Session-ID': _sessionId ?? '',
      };
  String? get userLocation => _userLocation;
  String? get userCrop => _userCrop;

  void setUserLocation(String location) {
    _userLocation = location;
    notifyListeners();
  }

  void setUserCrop(String crop) {
    _userCrop = crop;
    notifyListeners();
  }

  /// Initialize location detection when app starts
  Future<void> initializeLocation() async {
    try {
      print('🌍 AgriProvider: Initializing location detection...');
      final location = await _weatherService.getCurrentLocation();
      
      if (location != null) {
        _detectedLocation = location;
        _userLocation = location.displayName ?? "${location.locality}, ${location.administrativeArea}";
        print('✅ AgriProvider: Location detected: $_userLocation');
        notifyListeners();
      } else {
        // Fallback to default location
        _userLocation = "Delhi, India";
        print('⚠️ AgriProvider: Using default location: $_userLocation');
        notifyListeners();
      }
    } catch (e) {
      print('❌ AgriProvider: Location detection failed: $e');
      _userLocation = "Delhi, India"; // Fallback
      notifyListeners();
    }
  }

  /// Get current location for API queries (prioritizes GPS, falls back to default)
  String get locationForAPI {
    if (_detectedLocation != null) {
      // Use GPS coordinates for better accuracy
      return "${_detectedLocation!.latitude},${_detectedLocation!.longitude}";
    } else if (_userLocation != null) {
      // Use location name
      return _userLocation!;
    } else {
      // Final fallback
      return "Delhi, India";
    }
  }

  Future<QueryResponse?> sendQuery(String query) async {
    // record user message
    _messages.add(ChatMessage(isUser: true, text: query));
    notifyListeners();

    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      await _ensureSession();
      final params = <String, String>{
        'text': query,
      };
      
      // Use GPS-based location for better accuracy
      params['location'] = locationForAPI;
      
      if (_userCrop != null) {
        params['crop'] = _userCrop!;
      }
      
      print('🌍 AgriProvider: Sending query with location: ${params['location']}');

      final uri = Uri.parse('$baseUrl/query').replace(queryParameters: params);
      final response = await http
          .get(uri, headers: _headersWithSession())
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final queryResponse = QueryResponse.fromJson(data);
        
        _history.insert(0, queryResponse);
        _messages.add(ChatMessage(isUser: false, text: queryResponse.answer, response: queryResponse));
        _isLoading = false;
        notifyListeners();
        return queryResponse;
      } else {
        _error = 'Server error: ${response.statusCode}';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Network error: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  Future<QueryResponse?> testAgents(String query) async {
    _messages.add(ChatMessage(isUser: true, text: query));
    notifyListeners();

    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      await _ensureSession();
      final params = <String, String>{
        'text': query,
      };
      
      // Use GPS-based location for better accuracy
      params['location'] = locationForAPI;
      
      if (_userCrop != null) {
        params['crop'] = _userCrop!;
      }
      
      print('🌍 AgriProvider: Sending testAgents with location: ${params['location']}');

      final uri = Uri.parse('$baseUrl/agents').replace(queryParameters: params);
      final response = await http
          .get(uri, headers: _headersWithSession())
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final queryResponse = QueryResponse.fromJson(data);
        
        _history.insert(0, queryResponse);
        _messages.add(ChatMessage(isUser: false, text: queryResponse.answer, response: queryResponse));
        _isLoading = false;
        notifyListeners();
        return queryResponse;
      } else {
        _error = 'Server error: ${response.statusCode}';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Network error: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  /// Test the LangGraph supervisor directly with detailed workflow information
  Future<QueryResponse?> testSupervisor(String query) async {
    _messages.add(ChatMessage(isUser: true, text: query));
    notifyListeners();

    _isLoading = true;
    _error = '';
    notifyListeners();

    try {
      await _ensureSession();
      final params = <String, String>{
        'text': query,
      };
      
      // Use GPS-based location for better accuracy
      params['location'] = locationForAPI;
      
      if (_userCrop != null) {
        params['crop'] = _userCrop!;
      }
      
      print('🔍 AgriProvider: Testing supervisor with location: ${params['location']}');

      final uri = Uri.parse('$baseUrl/supervisor').replace(queryParameters: params);
      final response = await http
          .get(uri, headers: _headersWithSession())
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        
        // The supervisor endpoint returns a nested structure
        final responseData = data['response'] as Map<String, dynamic>;
        final queryResponse = QueryResponse.fromJson(responseData);
        
        // Add workflow trace information
        print('🔍 Supervisor Workflow Trace: ${data['workflow_trace']}');
        print('🔍 Agents Consulted: ${data['agents_consulted']}');
        
        _history.insert(0, queryResponse);
        _messages.add(ChatMessage(isUser: false, text: queryResponse.answer, response: queryResponse));
        _isLoading = false;
        notifyListeners();
        return queryResponse;
      } else {
        _error = 'Server error: ${response.statusCode}';
        _isLoading = false;
        notifyListeners();
        return null;
      }
    } catch (e) {
      _error = 'Network error: $e';
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  void clearHistory() {
    _history.clear();
    _messages.clear();
    notifyListeners();
  }

  void clearError() {
    _error = '';
    notifyListeners();
  }
}
