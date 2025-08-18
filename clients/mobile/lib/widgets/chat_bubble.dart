import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/chat_message.dart';
import '../models/query_response.dart';
import 'response_card.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final VoidCallback? onCopy;
  final VoidCallback? onSpeak;
  final bool isSpeaking;

  const ChatBubble({
    super.key,
    required this.message,
    this.onCopy,
    this.onSpeak,
    this.isSpeaking = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isUser = message.isUser;

    final bubbleColor = isUser
        ? LinearGradient(colors: [
            theme.colorScheme.primary,
            theme.colorScheme.primaryContainer,
          ])
        : null;

    final assistantBg = theme.colorScheme.surfaceVariant.withOpacity(0.4);

    final radius = BorderRadius.only(
      topLeft: const Radius.circular(16),
      topRight: const Radius.circular(16),
      bottomLeft: Radius.circular(isUser ? 16 : 4),
      bottomRight: Radius.circular(isUser ? 4 : 16),
    );

    Widget content;
    if (isUser) {
      content = Text(
        message.text,
        style: theme.textTheme.bodyLarge?.copyWith(color: Colors.white, height: 1.5),
      );
    } else {
      content = Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 14,
                backgroundColor: theme.colorScheme.primary.withOpacity(0.15),
                child: Icon(Icons.agriculture, color: theme.colorScheme.primary, size: 18),
              ),
              const SizedBox(width: 8),
              Text('Agri Advisor', style: theme.textTheme.labelLarge?.copyWith(color: theme.colorScheme.primary)),
            ],
          ),
          const SizedBox(height: 8),
          MarkdownBody(
            data: message.text,
            softLineBreak: true,
            styleSheet: MarkdownStyleSheet(
              p: theme.textTheme.bodyLarge?.copyWith(height: 1.55, fontSize: 16),
              strong: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: theme.colorScheme.primary,
              ),
              h2: theme.textTheme.titleLarge?.copyWith(
                color: theme.colorScheme.primary,
                fontWeight: FontWeight.w700,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (onCopy != null)
                IconButton(
                  tooltip: 'Copy',
                  icon: const Icon(Icons.copy_all_outlined, size: 18),
                  onPressed: onCopy,
                  padding: EdgeInsets.zero,
                  constraints: const BoxConstraints(),
                ),
              if (onSpeak != null)
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: IconButton(
                    tooltip: 'Speak',
                    icon: Icon(
                      isSpeaking ? Icons.stop_circle_outlined : Icons.volume_up_outlined,
                      size: 18,
                      color: isSpeaking ? theme.colorScheme.primary : null,
                    ),
                    onPressed: onSpeak,
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
                ),
              if (message.response != null)
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: _DetailsButton(response: message.response!),
                ),
            ],
          ),
        ],
      );
    }

    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final maxBubbleWidth = constraints.maxWidth * 0.88;
          return ConstrainedBox(
            constraints: BoxConstraints(maxWidth: maxBubbleWidth),
            child: Container(
              decoration: BoxDecoration(
                color: isUser ? null : assistantBg,
                gradient: isUser ? bubbleColor as LinearGradient? : null,
                borderRadius: radius,
                border: Border.all(
                  color: isUser
                      ? Colors.transparent
                      : theme.colorScheme.primary.withOpacity(0.15),
                ),
              ),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              child: content,
            ),
          );
        },
      ),
    );
  }
}

class _DetailsButton extends StatelessWidget {
  final QueryResponse response;
  const _DetailsButton({required this.response});

  @override
  Widget build(BuildContext context) {
    return TextButton.icon(
      style: TextButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        visualDensity: VisualDensity.compact,
      ),
      onPressed: () {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Theme.of(context).colorScheme.surface,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
          ),
          builder: (_) => DraggableScrollableSheet(
            expand: false,
            initialChildSize: 0.7,
            minChildSize: 0.4,
            maxChildSize: 0.95,
            builder: (context, controller) {
              return Padding(
                padding: const EdgeInsets.all(16),
                child: SingleChildScrollView(
                  controller: controller,
                  child: ResponseCard(
                    response: response,
                    onSpeak: () {},
                    isSpeaking: false,
                  ),
                ),
              );
            },
          ),
        );
      },
      icon: const Icon(Icons.info_outline, size: 16),
      label: const Text('Details'),
    );
  }
}


