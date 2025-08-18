import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../providers/agri_provider.dart';
import '../models/query_response.dart';
import '../widgets/weather_forecast_widget.dart';
import '../widgets/response_card.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _queryController = TextEditingController();
  final SpeechToText _speechToText = SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();
  bool _isListening = false;
  bool _isSpeaking = false;
  bool _debugMode = false; // Toggle for supervisor testing

  @override
  void initState() {
    super.initState();
    _initializeSpeech();
    _initializeTts();
  }

  Future<void> _initializeSpeech() async {
    bool available = await _speechToText.initialize();
    if (!available) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Speech recognition not available')),
        );
      }
    }
  }

  Future<void> _initializeTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setSpeechRate(0.5);
    await _flutterTts.setVolume(1.0);
    await _flutterTts.setPitch(1.0);
  }

  Future<void> _startListening() async {
    if (!_isListening) {
      bool available = await _speechToText.initialize();
      if (available) {
        setState(() {
          _isListening = true;
        });
        await _speechToText.listen(
          onResult: (result) {
            setState(() {
              _queryController.text = result.recognizedWords;
            });
          },
        );
      }
    }
  }

  Future<void> _stopListening() async {
    await _speechToText.stop();
    setState(() {
      _isListening = false;
    });
  }

  Future<void> _speakText(String text) async {
    if (!_isSpeaking) {
      setState(() {
        _isSpeaking = true;
      });
      await _flutterTts.speak(text);
      setState(() {
        _isSpeaking = false;
      });
    }
  }

  Future<void> _sendQuery() async {
    if (_queryController.text.trim().isEmpty) return;

    final provider = Provider.of<AgriProvider>(context, listen: false);
    QueryResponse? response;
    
    if (_debugMode) {
      // Use supervisor endpoint for debugging
      response = await provider.testSupervisor(_queryController.text.trim());
    } else {
      // Use regular query endpoint
      response = await provider.sendQuery(_queryController.text.trim());
    }
    
    if (response != null) {
      _queryController.clear();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agri Advisor'),
        actions: [
          // Debug mode toggle
          IconButton(
            tooltip: _debugMode ? 'Disable Debug Mode' : 'Enable Debug Mode',
            icon: Icon(
              _debugMode ? Icons.bug_report : Icons.bug_report_outlined,
              color: _debugMode ? Colors.orange : null,
            ),
            onPressed: () {
              setState(() {
                _debugMode = !_debugMode;
              });
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(_debugMode ? 'Debug Mode Enabled - Testing Supervisor' : 'Debug Mode Disabled'),
                  duration: const Duration(seconds: 2),
                ),
              );
            },
          ),
        ],
      ),
      body: Consumer<AgriProvider>(
        builder: (context, provider, child) {
          return Column(
            children: [
              // Compact weather section (expandable)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                child: ExpansionTile(
                  tilePadding: EdgeInsets.zero,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  leading: Icon(
                    Icons.wb_sunny_outlined,
                    color: Theme.of(context).colorScheme.primary,
                  ),
                  title: const Text(
                    'Weather & forecast',
                    style: TextStyle(fontWeight: FontWeight.w600),
                  ),
                  children: const [
                    WeatherForecastWidget(),
                  ],
                ),
              ),
              // Chat list fills available space
              Expanded(
                child: provider.history.isEmpty
                    ? const _EmptyState()
                    : ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                        reverse: true,
                        itemCount: provider.history.length,
                        itemBuilder: (context, index) {
                          final response = provider.history[provider.history.length - 1 - index];
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 8),
                            child: ResponseCard(
                              response: response,
                              onSpeak: () => _speakText(response.answer),
                              isSpeaking: _isSpeaking,
                            ),
                          );
                        },
                      ),
              ),
              if (provider.isLoading)
                const LinearProgressIndicator(minHeight: 2),
              // Input area pinned to bottom
              SafeArea(
                top: false,
                child: Container(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
                  decoration: BoxDecoration(
                    color: Theme.of(context).scaffoldBackgroundColor,
                    boxShadow: const [
                      BoxShadow(
                        color: Colors.black12,
                        blurRadius: 8,
                        offset: Offset(0, -2),
                      )
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // Crop selection (kept, but compact)
                      DropdownButtonFormField<String>(
                        isDense: true,
                        decoration: const InputDecoration(
                          labelText: 'Crop',
                          prefixIcon: Icon(Icons.agriculture_outlined),
                        ),
                        value: provider.userCrop,
                        items: [
                          'wheat', 'rice', 'cotton', 'maize',
                          'pulses', 'sugarcane', 'groundnut'
                        ].map((String value) {
                          return DropdownMenuItem<String>(
                            value: value,
                            child: Text(value),
                          );
                        }).toList(),
                        onChanged: (value) {
                          if (value != null) provider.setUserCrop(value);
                        },
                      ),
                      const SizedBox(height: 8),
                      const _SuggestionChips(),
                      const SizedBox(height: 8),
                      TextField(
                        controller: _queryController,
                        minLines: 1,
                        maxLines: 5,
                        decoration: InputDecoration(
                          hintText: 'Type your message...',
                          filled: true,
                          prefixIcon: const Icon(Icons.chat_outlined),
                          suffixIcon: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                tooltip: _isListening ? 'Stop voice input' : 'Voice input',
                                icon: Icon(_isListening ? Icons.mic : Icons.mic_none),
                                onPressed: _isListening ? _stopListening : _startListening,
                                color: _isListening ? Colors.red : null,
                              ),
                              IconButton(
                                tooltip: 'Send',
                                icon: const Icon(Icons.send),
                                onPressed: provider.isLoading ? null : _sendQuery,
                              ),
                            ],
                          ),
                        ),
                        enabled: !provider.isLoading,
                        textInputAction: TextInputAction.newline,
                      ),
                      if (provider.error.isNotEmpty)
                        Container(
                          width: double.infinity,
                          margin: const EdgeInsets.only(top: 8),
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.red.shade100,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            provider.error,
                            style: TextStyle(color: Colors.red.shade800),
                          ),
                        ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    _queryController.dispose();
    _speechToText.cancel();
    _flutterTts.stop();
    super.dispose();
  }


}

class _SuggestionChips extends StatelessWidget {
  const _SuggestionChips();

  @override
  Widget build(BuildContext context) {
    final suggestions = <String>[
      'weather alert',
      'irrigation schedule',
      'market price of wheat',
      'pest control for rice',
      'fertilizer recommendation',
      'best sowing time',
    ];

    return Align(
      alignment: Alignment.centerLeft,
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: suggestions
            .map((s) => ActionChip(
                  label: Text(s),
                  avatar: const Icon(Icons.bolt, size: 16),
                  onPressed: () {
                    // Find the _HomeScreenState to access the controller
                    final homeState = context.findAncestorStateOfType<_HomeScreenState>();
                    if (homeState != null) {
                      homeState._queryController.text = s;
                      homeState._queryController.selection = TextSelection.fromPosition(
                        TextPosition(offset: homeState._queryController.text.length),
                      );
                    }
                  },
                ))
            .toList(),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.agriculture, size: 80, color: theme.colorScheme.outline),
            const SizedBox(height: 16),
            Text(
              'Ask a question to get started!',
              style: theme.textTheme.titleMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Try: "irrigation for wheat" or "weather alert"',
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.outline,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}

class _WelcomeCard extends StatelessWidget {
  const _WelcomeCard();

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    return Card(
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              colorScheme.primary,
              colorScheme.primaryContainer,
            ],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.agriculture, size: 32, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Welcome to Agri Advisor',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                        ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Get expert, easy-to-understand advice for your farm. Ask your questions below.',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.white.withOpacity(0.95),
                  ),
            ),
          ],
        ),
      ),
    );
  }
}
