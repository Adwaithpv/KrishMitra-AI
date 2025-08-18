import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:flutter/services.dart';
import 'package:flutter/rendering.dart';
import '../providers/agri_provider.dart';
import '../models/query_response.dart';
import '../widgets/weather_forecast_widget.dart';
import '../widgets/response_card.dart';
import '../models/chat_message.dart';
import '../widgets/chat_bubble.dart';

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
  bool _showSuggestions = true;
  final ScrollController _chatController = ScrollController();
  final GlobalKey _composerKey = GlobalKey();
  double _composerHeight = 0;

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

    // Handlers to keep UI state in sync with TTS engine
    _flutterTts.setStartHandler(() {
      if (mounted) {
        setState(() {
          _isSpeaking = true;
        });
      }
    });
    _flutterTts.setCompletionHandler(() {
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
    });
    _flutterTts.setCancelHandler(() {
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
    });
    _flutterTts.setErrorHandler((message) {
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
    });
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

  Future<void> _toggleSpeak(String text) async {
    if (_isSpeaking) {
      await _flutterTts.stop();
      if (mounted) {
        setState(() {
          _isSpeaking = false;
        });
      }
      return;
    }
    await _flutterTts.speak(text);
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
          // Measure composer, then scroll to bottom with the correct spacer
          WidgetsBinding.instance.addPostFrameCallback((_) {
            _updateComposerHeight();
            _scrollToBottom();
          });
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
                child: provider.messages.isEmpty
                    ? const _EmptyState()
                    : ListView.builder(
                        controller: _chatController,
                        padding: const EdgeInsets.fromLTRB(16, 8, 16, 8),
                        itemCount: provider.messages.length + 1,
                        itemBuilder: (context, index) {
                          if (index == provider.messages.length) {
                            final bottomInset = MediaQuery.of(context).viewInsets.bottom;
                            final spacer = (_composerHeight + bottomInset + 24).clamp(24, 400);
                            return SizedBox(height: spacer.toDouble());
                          }
                          final msg = provider.messages[index];
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 6),
                            child: ChatBubble(
                              message: msg,
                              onCopy: msg.isUser
                                  ? null
                                  : () async {
                                      await Clipboard.setData(ClipboardData(text: msg.text));
                                      if (context.mounted) {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('Copied to clipboard')),
                                        );
                                      }
                                    },
                              onSpeak: msg.isUser ? null : () => _toggleSpeak(msg.text),
                              isSpeaking: _isSpeaking && !msg.isUser,
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
                  key: _composerKey,
                  padding: const EdgeInsets.fromLTRB(12, 8, 12, 12),
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
                      // Accessory row: compact controls
                      Row(
                        children: [
                          TextButton.icon(
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              visualDensity: VisualDensity.compact,
                            ),
                            onPressed: () => _openCropPicker(context),
                            icon: const Icon(Icons.agriculture_outlined, size: 18),
                            label: Text(provider.userCrop != null ? provider.userCrop! : 'Crop'),
                          ),
                          const SizedBox(width: 8),
                          FilterChip(
                            selected: _showSuggestions,
                            onSelected: (v) => setState(() => _showSuggestions = v),
                            label: const Text('Suggestions'),
                            avatar: const Icon(Icons.bolt, size: 16),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      if (_showSuggestions)
                        _SuggestionRow(onPick: (s) {
                          _queryController.text = s;
                          _queryController.selection = TextSelection.fromPosition(
                            TextPosition(offset: _queryController.text.length),
                          );
                        }),
                      const SizedBox(height: 6),
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
                          margin: const EdgeInsets.only(top: 6),
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
    _chatController.dispose();
    super.dispose();
  }

  Future<void> _openCropPicker(BuildContext context) async {
    final provider = Provider.of<AgriProvider>(context, listen: false);
    final crops = <String>['wheat', 'rice', 'cotton', 'maize', 'pulses', 'sugarcane', 'groundnut'];
    final theme = Theme.of(context);

    await showModalBottomSheet(
      context: context,
      backgroundColor: theme.colorScheme.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Select Crop', style: theme.textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w700)),
                const SizedBox(height: 12),
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: crops.map((c) {
                    final selected = provider.userCrop == c;
                    return ChoiceChip(
                      label: Text(c),
                      selected: selected,
                      onSelected: (_) {
                        provider.setUserCrop(c);
                        Navigator.pop(context);
                      },
                      avatar: const Icon(Icons.spa, size: 16),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _scrollToBottom() {
    if (!_chatController.hasClients) return;
    _chatController.animateTo(
      _chatController.position.maxScrollExtent,
      duration: const Duration(milliseconds: 250),
      curve: Curves.easeOut,
    );
  }

  void _updateComposerHeight() {
    final ctx = _composerKey.currentContext;
    if (ctx == null) return;
    final box = ctx.findRenderObject();
    if (box is RenderBox) {
      final newHeight = box.size.height;
      if ((newHeight - _composerHeight).abs() > 1) {
        setState(() {
          _composerHeight = newHeight;
        });
      }
    }
  }
}

class _SuggestionRow extends StatelessWidget {
  final void Function(String) onPick;
  const _SuggestionRow({required this.onPick});

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
    return SizedBox(
      height: 36,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 2),
        itemCount: suggestions.length,
        separatorBuilder: (_, __) => const SizedBox(width: 8),
        itemBuilder: (context, index) {
          final s = suggestions[index];
          return ActionChip(
            label: Text(s, overflow: TextOverflow.ellipsis),
            avatar: const Icon(Icons.bolt, size: 16),
            onPressed: () => onPick(s),
            visualDensity: VisualDensity.compact,
            materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
          );
        },
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
