import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../models/query_response.dart';

class ResponseCard extends StatelessWidget {
  final QueryResponse response;
  final VoidCallback onSpeak;
  final bool isSpeaking;

  const ResponseCard({
    super.key,
    required this.response,
    required this.onSpeak,
    required this.isSpeaking,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with action buttons
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Agri Advisor Response',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                  ),
                ),
                Row(
                  children: [
                    IconButton(
                      tooltip: 'Copy',
                      icon: const Icon(Icons.copy_all_outlined, size: 20),
                      onPressed: () async {
                        await Clipboard.setData(ClipboardData(text: response.answer));
                        if (context.mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Copied to clipboard')),
                          );
                        }
                      },
                    ),
                    IconButton(
                      tooltip: 'Speak',
                      icon: Icon(
                        isSpeaking ? Icons.volume_up : Icons.volume_up_outlined,
                        color: isSpeaking ? theme.colorScheme.primary : null,
                        size: 20,
                      ),
                      onPressed: onSpeak,
                    ),
                  ],
                )
              ],
            ),

            const SizedBox(height: 16),

            // Enhanced Answer Section
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: theme.colorScheme.surfaceVariant.withOpacity(0.3),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: theme.colorScheme.primary.withOpacity(0.2),
                  width: 1,
                ),
              ),
              child: MarkdownBody(
                data: response.answer,
                styleSheet: MarkdownStyleSheet(
                  p: theme.textTheme.bodyLarge?.copyWith(
                    height: 1.6,
                    fontSize: 16,
                  ),
                  strong: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.primary,
                    fontSize: 17,
                  ),
                  h1: theme.textTheme.headlineSmall?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.bold,
                  ),
                  h2: theme.textTheme.titleLarge?.copyWith(
                    color: theme.colorScheme.primary,
                    fontWeight: FontWeight.w600,
                  ),
                  h3: theme.textTheme.titleMedium?.copyWith(
                    color: theme.colorScheme.onSurface,
                    fontWeight: FontWeight.w600,
                  ),
                  listBullet: theme.textTheme.bodyLarge?.copyWith(
                    color: theme.colorScheme.primary,
                  ),
                  code: theme.textTheme.bodyMedium?.copyWith(
                    backgroundColor: theme.colorScheme.secondaryContainer,
                    fontFamily: 'monospace',
                  ),
                  blockquote: theme.textTheme.bodyLarge?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                    fontStyle: FontStyle.italic,
                  ),
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Enhanced Metadata Section
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: theme.colorScheme.secondary.withOpacity(0.08),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Column(
                children: [
                  // Confidence and Agents Row
                  Row(
                    children: [
                      // Confidence Badge
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                        decoration: BoxDecoration(
                          color: _getConfidenceColor(response.confidence).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: _getConfidenceColor(response.confidence).withOpacity(0.3),
                          ),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(
                              _getConfidenceIcon(response.confidence),
                              size: 16,
                              color: _getConfidenceColor(response.confidence),
                            ),
                            const SizedBox(width: 4),
                            Text(
                              '${(response.confidence * 100).toStringAsFixed(1)}%',
                              style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.bold,
                                color: _getConfidenceColor(response.confidence),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      
                      // Agents Badge
                      if (response.agentsConsulted != null && response.agentsConsulted!.isNotEmpty)
                        Expanded(
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(16),
                              border: Border.all(
                                color: theme.colorScheme.primary.withOpacity(0.2),
                              ),
                            ),
                            child: Row(
                              children: [
                                Icon(
                                  Icons.smart_toy,
                                  size: 16,
                                  color: theme.colorScheme.primary,
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    _formatAgentNames(response.agentsConsulted!),
                                    style: TextStyle(
                                      fontSize: 13,
                                      fontWeight: FontWeight.w500,
                                      color: theme.colorScheme.primary,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
            ),

            // Workflow Information (if available)
            if (response.agentUsed != null || response.workflowTrace != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  if (response.agentUsed != null) ...[
                    Icon(Icons.psychology, size: 16, color: theme.colorScheme.primary),
                    const SizedBox(width: 4),
                    Text(
                      'Agent: ${response.agentUsed}',
                      style: TextStyle(
                        fontSize: 12,
                        color: theme.colorScheme.primary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                  if (response.workflowTrace != null) ...[
                    const SizedBox(width: 16),
                    Icon(Icons.timeline, size: 16, color: theme.colorScheme.secondary),
                    const SizedBox(width: 4),
                    Text(
                      'Trace: ${response.workflowTrace}',
                      style: TextStyle(
                        fontSize: 12,
                        color: theme.colorScheme.secondary,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ],
              ),
            ],

            // Performance Information (if available)
            if (response.responseTime != null || response.cacheHit != null) ...[
              const SizedBox(height: 4),
              Row(
                children: [
                  if (response.responseTime != null) ...[
                    Icon(Icons.speed, size: 16, color: theme.colorScheme.outline),
                    const SizedBox(width: 4),
                    Text(
                      '${response.responseTime!.toStringAsFixed(2)}s',
                      style: TextStyle(
                        fontSize: 12,
                        color: theme.colorScheme.outline,
                      ),
                    ),
                  ],
                  if (response.cacheHit != null) ...[
                    const SizedBox(width: 16),
                    Icon(
                      response.cacheHit! ? Icons.cached : Icons.cloud_download,
                      size: 16,
                      color: response.cacheHit! ? Colors.green : theme.colorScheme.outline,
                    ),
                    const SizedBox(width: 4),
                    Text(
                      response.cacheHit! ? 'Cached' : 'Live',
                      style: TextStyle(
                        fontSize: 12,
                        color: response.cacheHit! ? Colors.green : theme.colorScheme.outline,
                      ),
                    ),
                  ],
                ],
              ),
            ],

            // Enhanced Evidence Section
            if (response.evidence.isNotEmpty) ...[
              const SizedBox(height: 12),
              Container(
                decoration: BoxDecoration(
                  border: Border.all(
                    color: theme.colorScheme.outline.withOpacity(0.2),
                  ),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: ExpansionTile(
                  tilePadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                  childrenPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                  leading: Icon(
                    Icons.library_books,
                    color: theme.colorScheme.primary,
                    size: 24,
                  ),
                  title: Text(
                    'Supporting Evidence (${response.evidence.length})',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: theme.colorScheme.primary,
                    ),
                  ),
                  subtitle: Text(
                    'Tap to view sources and references',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                  children: [
                    ListView.separated(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: response.evidence.length,
                      separatorBuilder: (context, index) => const SizedBox(height: 12),
                      itemBuilder: (context, index) {
                        final evidence = response.evidence[index];
                        return Container(
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: theme.colorScheme.surfaceVariant.withOpacity(0.3),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: theme.colorScheme.primary.withOpacity(0.2),
                            ),
                          ),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // Evidence Header
                              Row(
                                children: [
                                  Container(
                                    padding: const EdgeInsets.all(6),
                                    decoration: BoxDecoration(
                                      color: theme.colorScheme.primary.withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(
                                      '${index + 1}',
                                      style: TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: theme.colorScheme.primary,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      evidence.source ?? 'Agricultural Database',
                                      style: theme.textTheme.titleSmall?.copyWith(
                                        fontWeight: FontWeight.w600,
                                        color: theme.colorScheme.primary,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              
                              if (evidence.excerpt != null) ...[
                                const SizedBox(height: 12),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: theme.colorScheme.surface,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                      color: theme.colorScheme.outline.withOpacity(0.2),
                                    ),
                                  ),
                                  child: Text(
                                    evidence.excerpt!,
                                    style: theme.textTheme.bodyMedium?.copyWith(
                                      height: 1.5,
                                      fontSize: 14,
                                    ),
                                  ),
                                ),
                              ],
                              
                              const SizedBox(height: 12),
                              
                              // Metadata tags
                              Wrap(
                                spacing: 8,
                                runSpacing: 6,
                                children: [
                                  if (evidence.date != null)
                                    _buildEvidenceTag(
                                      Icons.calendar_today,
                                      evidence.date!,
                                      theme.colorScheme.secondary,
                                      theme,
                                    ),
                                  if (evidence.geo != null)
                                    _buildEvidenceTag(
                                      Icons.location_on,
                                      evidence.geo!,
                                      theme.colorScheme.tertiary,
                                      theme,
                                    ),
                                  if (evidence.crop != null)
                                    _buildEvidenceTag(
                                      Icons.agriculture,
                                      evidence.crop!,
                                      Colors.green,
                                      theme,
                                    ),
                                ],
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.7) {
      return Colors.green;
    } else if (confidence >= 0.4) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }

  IconData _getConfidenceIcon(double confidence) {
    if (confidence >= 0.7) {
      return Icons.check_circle;
    } else if (confidence >= 0.4) {
      return Icons.warning;
    } else {
      return Icons.error;
    }
  }

  String _formatAgentNames(List<String> agents) {
    return agents
        .map((agent) => agent.replaceAll('_agent', '').replaceAll('_', ' ').toUpperCase())
        .join(', ');
  }

  Widget _buildEvidenceTag(IconData icon, String text, Color color, ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 14,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            text,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}
