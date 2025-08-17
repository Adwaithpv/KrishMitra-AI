class QueryResponse {
  final String answer;
  final List<Evidence> evidence;
  final double confidence;
  final List<String>? agentsConsulted;
  final String? agentUsed;
  final String? workflowTrace;
  final double? responseTime;
  final bool? cacheHit;

  QueryResponse({
    required this.answer,
    required this.evidence,
    required this.confidence,
    this.agentsConsulted,
    this.agentUsed,
    this.workflowTrace,
    this.responseTime,
    this.cacheHit,
  });

  factory QueryResponse.fromJson(Map<String, dynamic> json) {
    return QueryResponse(
      answer: json['answer'] ?? '',
      evidence: (json['evidence'] as List<dynamic>?)
          ?.map((e) => Evidence.fromJson(e))
          .toList() ?? [],
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      agentsConsulted: (json['agents_consulted'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList(),
      agentUsed: json['agent_used'],
      workflowTrace: json['workflow_trace'],
      responseTime: (json['response_time'] as num?)?.toDouble(),
      cacheHit: json['cache_hit'] as bool?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'answer': answer,
      'evidence': evidence.map((e) => e.toJson()).toList(),
      'confidence': confidence,
      'agents_consulted': agentsConsulted,
      'agent_used': agentUsed,
      'workflow_trace': workflowTrace,
      'response_time': responseTime,
      'cache_hit': cacheHit,
    };
  }
}

class Evidence {
  final String? source;
  final String? excerpt;
  final String? date;
  final String? geo;
  final String? crop;
  final double? score;

  Evidence({
    this.source,
    this.excerpt,
    this.date,
    this.geo,
    this.crop,
    this.score,
  });

  factory Evidence.fromJson(Map<String, dynamic> json) {
    return Evidence(
      source: json['source'],
      excerpt: json['excerpt'],
      date: json['date'],
      geo: json['geo'],
      crop: json['crop'],
      score: (json['score'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'source': source,
      'excerpt': excerpt,
      'date': date,
      'geo': geo,
      'crop': crop,
      'score': score,
    };
  }
}
