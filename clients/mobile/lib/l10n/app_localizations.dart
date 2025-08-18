import 'package:flutter/widgets.dart';

class AppLocalizations {
  final Locale locale;

  AppLocalizations(this.locale);

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('hi'),
    Locale('ta'),
    Locale('te'),
    Locale('bn'),
    Locale('mr'),
    Locale('kn'),
    Locale('gu'),
    Locale('pa'),
    Locale('ml'),
  ];

  static AppLocalizations of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations) ?? AppLocalizations(const Locale('en'));
  }

  static final Map<String, Map<String, String>> _localizedValues = {
    'en': {
      'appTitle': 'Agri Advisor',
      'navHome': 'Home',
      'navHistory': 'History',
      'navSettings': 'Settings',
      'settingsTitle': 'Settings',
      'profile': 'Profile',
      'currentLocation': 'Current Location',
      'primaryCrop': 'Primary Crop',
      'appSettings': 'App Settings',
      'voiceInput': 'Voice Input',
      'voiceInputSubtitle': 'Enable speech-to-text',
      'voiceOutput': 'Voice Output',
      'voiceOutputSubtitle': 'Enable text-to-speech',
      'offlineMode': 'Offline Mode',
      'offlineModeSubtitle': 'Use cached responses when offline',
      'dataManagement': 'Data Management',
      'clearQueryHistory': 'Clear Query History',
      'deleteAllStoredQueries': 'Delete all stored queries',
      'clearHistory': 'Clear History',
      'areYouSureClearHistory': 'Are you sure you want to clear all query history?',
      'cancel': 'Cancel',
      'clear': 'Clear',
      'about': 'About',
      'version': 'Version',
      'privacyPolicy': 'Privacy Policy',
      'helpSupport': 'Help & Support',
      'selectPrimaryCrop': 'Select Primary Crop',
      'language': 'Language',
      'selectLanguage': 'Select Language',
      'homeTitle': 'Agri Advisor',
      'weatherAndForecast': 'Weather & forecast',
      'suggestions': 'Suggestions',
      'crop': 'Crop',
      'typeMessage': 'Type your message...',
      'voiceInputTooltip': 'Voice input',
      'stopVoiceInputTooltip': 'Stop voice input',
      'send': 'Send',
      'copiedToClipboard': 'Copied to clipboard',
      'speechRecognitionNotAvailable': 'Speech recognition not available',
      'debugEnabled': 'Debug Mode Enabled - Testing Supervisor',
      'debugDisabled': 'Debug Mode Disabled',
      'emptyStateTitle': 'Ask a question to get started!',
      'emptyStateSubtitle': 'Try: "irrigation for wheat" or "weather alert"',
      'details': 'Details',
      'agriAdvisorResponse': 'Agri Advisor Response',
      'copy': 'Copy',
      'speak': 'Speak',
      'supportingEvidence': 'Supporting Evidence',
      'tapToViewSources': 'Tap to view sources and references',
      'agriDatabase': 'Agricultural Database',
      'weatherForecast': 'Weather Forecast',
      'refreshWeatherData': 'Refresh weather data',
      'gettingWeatherForecast': 'Getting weather forecast...',
      'weatherDataNotAvailable': 'Weather data not available',
      'tryAgain': 'Try Again',
      'getWeather': 'Get Weather',
      'today': 'Today',
      'temperature': 'Temperature',
      'rainChance': 'Rain chance',
      'wind': 'Wind',
      'sevenDayForecast': '7-Day Forecast',
      'historyTitle': 'Query History',
      'historyCleared': 'History cleared',
    },
    'hi': {
      'appTitle': 'कृषि सलाहकार',
      'navHome': 'होम',
      'navHistory': 'इतिहास',
      'navSettings': 'सेटिंग्स',
      'settingsTitle': 'सेटिंग्स',
      'profile': 'प्रोफाइल',
      'currentLocation': 'वर्तमान स्थान',
      'primaryCrop': 'मुख्य फसल',
      'appSettings': 'ऐप सेटिंग्स',
      'voiceInput': 'वॉइस इनपुट',
      'voiceInputSubtitle': 'बोली से लिखें सक्षम करें',
      'voiceOutput': 'वॉइस आउटपुट',
      'voiceOutputSubtitle': 'टेक्स्ट-टू-स्पीच सक्षम करें',
      'offlineMode': 'ऑफलाइन मोड',
      'offlineModeSubtitle': 'ऑफलाइन होने पर कैश किया गया उत्तर उपयोग करें',
      'dataManagement': 'डेटा प्रबंधन',
      'clearQueryHistory': 'क्वेरी इतिहास साफ़ करें',
      'deleteAllStoredQueries': 'सहेजे गए सभी प्रश्न हटाएं',
      'clearHistory': 'इतिहास साफ़ करें',
      'areYouSureClearHistory': 'क्या आप सभी क्वेरी इतिहास साफ़ करना चाहते हैं?',
      'cancel': 'रद्द करें',
      'clear': 'साफ़ करें',
      'about': 'के बारे में',
      'version': 'संस्करण',
      'privacyPolicy': 'गोपनीयता नीति',
      'helpSupport': 'सहायता और समर्थन',
      'selectPrimaryCrop': 'मुख्य फसल चुनें',
      'language': 'भाषा',
      'selectLanguage': 'भाषा चुनें',
      'homeTitle': 'कृषि सलाहकार',
      'weatherAndForecast': 'मौसम और पूर्वानुमान',
      'suggestions': 'सुझाव',
      'crop': 'फसल',
      'typeMessage': 'अपना संदेश लिखें...',
      'voiceInputTooltip': 'वॉइस इनपुट',
      'stopVoiceInputTooltip': 'वॉइस इनपुट रोकें',
      'send': 'भेजें',
      'copiedToClipboard': 'क्लिपबोर्ड पर कॉपी किया गया',
      'speechRecognitionNotAvailable': 'वॉइस पहचान उपलब्ध नहीं है',
      'debugEnabled': 'डीबग मोड सक्षम - सुपरवाइजर टेस्ट',
      'debugDisabled': 'डीबग मोड अक्षम',
      'emptyStateTitle': 'शुरू करने के लिए कोई प्रश्न पूछें!',
      'emptyStateSubtitle': 'आजमाएं: "गेहूं की सिंचाई" या "मौसम चेतावनी"',
      'details': 'विवरण',
      'agriAdvisorResponse': 'कृषि सलाहकार उत्तर',
      'copy': 'कॉपी',
      'speak': 'बोलें',
      'supportingEvidence': 'समर्थन साक्ष्य',
      'tapToViewSources': 'स्रोत और संदर्भ देखने के लिए टैप करें',
      'agriDatabase': 'कृषि डेटाबेस',
      'weatherForecast': 'मौसम पूर्वानुमान',
      'refreshWeatherData': 'मौसम डेटा रीफ्रेश करें',
      'gettingWeatherForecast': 'मौसम पूर्वानुमान प्राप्त किया जा रहा है...',
      'weatherDataNotAvailable': 'मौसम डेटा उपलब्ध नहीं',
      'tryAgain': 'पुनः प्रयास करें',
      'getWeather': 'मौसम प्राप्त करें',
      'today': 'आज',
      'temperature': 'तापमान',
      'rainChance': 'वर्षा की संभावना',
      'wind': 'हवा',
      'sevenDayForecast': '7-दिवसीय पूर्वानुमान',
      'historyTitle': 'प्रश्न इतिहास',
      'historyCleared': 'इतिहास साफ़ किया गया',
    },
  };

  String _lookup(String key) {
    final lang = locale.languageCode;
    final map = _localizedValues[lang] ?? _localizedValues['en']!;
    return map[key] ?? _localizedValues['en']![key] ?? key;
  }

  String get appTitle => _lookup('appTitle');
  String get navHome => _lookup('navHome');
  String get navHistory => _lookup('navHistory');
  String get navSettings => _lookup('navSettings');
  String get settingsTitle => _lookup('settingsTitle');
  String get profile => _lookup('profile');
  String get currentLocation => _lookup('currentLocation');
  String get primaryCrop => _lookup('primaryCrop');
  String get appSettings => _lookup('appSettings');
  String get voiceInput => _lookup('voiceInput');
  String get voiceInputSubtitle => _lookup('voiceInputSubtitle');
  String get voiceOutput => _lookup('voiceOutput');
  String get voiceOutputSubtitle => _lookup('voiceOutputSubtitle');
  String get offlineMode => _lookup('offlineMode');
  String get offlineModeSubtitle => _lookup('offlineModeSubtitle');
  String get dataManagement => _lookup('dataManagement');
  String get clearQueryHistory => _lookup('clearQueryHistory');
  String get deleteAllStoredQueries => _lookup('deleteAllStoredQueries');
  String get clearHistory => _lookup('clearHistory');
  String get areYouSureClearHistory => _lookup('areYouSureClearHistory');
  String get cancel => _lookup('cancel');
  String get clear => _lookup('clear');
  String get about => _lookup('about');
  String get version => _lookup('version');
  String get privacyPolicy => _lookup('privacyPolicy');
  String get helpSupport => _lookup('helpSupport');
  String get selectPrimaryCrop => _lookup('selectPrimaryCrop');
  String get language => _lookup('language');
  String get selectLanguage => _lookup('selectLanguage');
  String get homeTitle => _lookup('homeTitle');
  String get weatherAndForecast => _lookup('weatherAndForecast');
  String get suggestions => _lookup('suggestions');
  String get crop => _lookup('crop');
  String get typeMessage => _lookup('typeMessage');
  String get voiceInputTooltip => _lookup('voiceInputTooltip');
  String get stopVoiceInputTooltip => _lookup('stopVoiceInputTooltip');
  String get send => _lookup('send');
  String get copiedToClipboard => _lookup('copiedToClipboard');
  String get speechRecognitionNotAvailable => _lookup('speechRecognitionNotAvailable');
  String get debugEnabled => _lookup('debugEnabled');
  String get debugDisabled => _lookup('debugDisabled');
  String get emptyStateTitle => _lookup('emptyStateTitle');
  String get emptyStateSubtitle => _lookup('emptyStateSubtitle');
  String get details => _lookup('details');
  String get agriAdvisorResponse => _lookup('agriAdvisorResponse');
  String get copy => _lookup('copy');
  String get speak => _lookup('speak');
  String get supportingEvidence => _lookup('supportingEvidence');
  String get tapToViewSources => _lookup('tapToViewSources');
  String get agriDatabase => _lookup('agriDatabase');
  String get weatherForecast => _lookup('weatherForecast');
  String get refreshWeatherData => _lookup('refreshWeatherData');
  String get gettingWeatherForecast => _lookup('gettingWeatherForecast');
  String get weatherDataNotAvailable => _lookup('weatherDataNotAvailable');
  String get tryAgain => _lookup('tryAgain');
  String get getWeather => _lookup('getWeather');
  String get today => _lookup('today');
  String get temperature => _lookup('temperature');
  String get rainChance => _lookup('rainChance');
  String get wind => _lookup('wind');
  String get sevenDayForecast => _lookup('sevenDayForecast');
  String get historyTitle => _lookup('historyTitle');
  String get historyCleared => _lookup('historyCleared');
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  bool isSupported(Locale locale) {
    return AppLocalizations.supportedLocales.any((l) => l.languageCode == locale.languageCode);
  }

  @override
  Future<AppLocalizations> load(Locale locale) async {
    return AppLocalizations(locale);
  }

  @override
  bool shouldReload(covariant LocalizationsDelegate<AppLocalizations> old) => false;
}


