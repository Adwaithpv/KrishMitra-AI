import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/agri_provider.dart';
import '../l10n/app_localizations.dart';
import '../widgets/response_card.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final t = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(t.historyTitle),
        backgroundColor: Colors.green,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.clear_all),
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text(t.clearHistory),
                  content: Text(t.areYouSureClearHistory),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: Text(t.cancel),
                    ),
                    TextButton(
                      onPressed: () {
                        Provider.of<AgriProvider>(context, listen: false).clearHistory();
                        Navigator.pop(context);
                      },
                      child: Text(t.clear),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: Consumer<AgriProvider>(
        builder: (context, provider, child) {
          if (provider.history.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.history,
                    size: 64,
                    color: Colors.grey,
                  ),
                  SizedBox(height: 16),
                  Text(
                    'No query history yet',
                    style: TextStyle(
                      fontSize: 18,
                      color: Colors.grey,
                    ),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Your queries and responses will appear here',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.history.length,
            itemBuilder: (context, index) {
              final response = provider.history[index];
              return ResponseCard(
                response: response,
                onSpeak: () {
                  // TODO: Implement text-to-speech
                },
                isSpeaking: false,
              );
            },
          );
        },
      ),
    );
  }
}
