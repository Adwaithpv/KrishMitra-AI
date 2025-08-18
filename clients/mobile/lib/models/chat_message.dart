import 'query_response.dart';

class ChatMessage {
  final bool isUser;
  final String text;
  final QueryResponse? response;
  final DateTime timestamp;

  ChatMessage({
    required this.isUser,
    required this.text,
    this.response,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();
}


