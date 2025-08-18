# KrishMitraAI - Agentic Agricultural Advisor

A comprehensive AI-powered agricultural advisory system that combines multiple specialized agents, real-time data integration, and a modern mobile application to provide farmers with intelligent, contextual agricultural guidance.

## 🌾 Solution Overview

KrishMitraAI is an intelligent agricultural advisory platform that leverages advanced AI agents, real-time data sources, and a sophisticated RAG (Retrieval-Augmented Generation) pipeline to provide farmers with personalized, evidence-based agricultural advice. The system addresses the critical need for accessible, reliable agricultural guidance in India and other developing regions.

### 🎯 Key Problems Solved

- **Information Accessibility**: Provides instant access to agricultural knowledge through natural language queries
- **Real-time Decision Support**: Integrates live weather data, market prices, and policy updates
- **Personalized Guidance**: Tailors advice based on location, crop type, and farming context
- **Multi-domain Expertise**: Covers weather, crop management, financial planning, and government policies
- **Language Accessibility**: Supports multiple languages for broader farmer reach

## 🏗️ System Architecture

```
KrishMitraAI/
├── services/
│   └── api/                    # FastAPI Backend Service
│       ├── app/
│       │   ├── agents/         # Specialized AI Agents
│       │   │   ├── weather_agent.py    # Weather analysis & forecasting
│       │   │   ├── crop_agent.py       # Crop management & advice
│       │   │   ├── finance_agent.py    # Market prices & financial guidance
│       │   │   └── policy_agent.py     # Government schemes & policies
│       │   ├── supervisor.py           # LangGraph-based agent orchestration
│       │   ├── llm_client.py           # Multi-model LLM integration
│       │   ├── etl_service.py          # Data ingestion & processing
│       │   ├── realtime_data.py        # Live data integration
│       │   ├── cache.py                # Redis-based caching
│       │   ├── monitoring.py           # Performance monitoring
│       │   └── security.py             # Rate limiting & security
│       └── requirements.txt
├── clients/
│   └── mobile/                 # Flutter Mobile Application
│       ├── lib/
│       │   ├── screens/        # UI Screens
│       │   │   ├── home_screen.dart      # Main chat interface
│       │   │   ├── history_screen.dart   # Query history
│       │   │   └── settings_screen.dart  # App configuration
│       │   ├── providers/      # State Management
│       │   ├── models/         # Data Models
│       │   ├── services/       # API Integration
│       │   └── widgets/        # Reusable UI Components
│       └── pubspec.yaml
├── infra/
│   ├── docker-compose.yml      # Production infrastructure
│   ├── grafana/                # Monitoring dashboards
│   └── prometheus.yml          # Metrics collection
└── scripts/                    # Testing & development tools
```

## 🤖 AI Agent System

### LangGraph Supervisor
The system uses a sophisticated LangGraph-based supervisor that intelligently orchestrates multiple specialized agents:

- **Query Analysis**: Understands user intent and context
- **Agent Routing**: Routes queries to appropriate specialized agents
- **Response Synthesis**: Combines multiple agent responses into coherent answers
- **Quality Validation**: Ensures response accuracy and relevance

### Specialized Agents

#### 🌤️ Weather Agent
- **Real-time Weather Data**: Integrates with WeatherAPI.com for live weather information
- **Agricultural Weather Analysis**: Provides weather-based farming recommendations
- **Forecast Integration**: Uses weather predictions for planning advice
- **Location-specific Insights**: Tailors advice based on local weather patterns

#### 🌱 Crop Agent
- **Irrigation Management**: Optimal watering schedules and techniques
- **Fertilizer Recommendations**: Nutrient management and application timing
- **Pest Control**: Integrated pest management strategies
- **Planting Guidance**: Optimal planting times and techniques
- **Disease Management**: Crop disease identification and treatment

#### 💰 Finance Agent
- **Market Price Analysis**: Real-time crop price tracking and trends
- **Subsidy Information**: Government subsidy eligibility and application guidance
- **Credit Facilities**: Agricultural loan information and requirements
- **Investment Planning**: Cost-benefit analysis for farming decisions
- **Financial Risk Assessment**: Market volatility and risk mitigation

#### 📋 Policy Agent
- **Government Schemes**: Comprehensive information on agricultural policies
- **Eligibility Assessment**: Automatic eligibility checking for various schemes
- **Application Guidance**: Step-by-step application process assistance
- **Documentation Requirements**: Required documents and procedures
- **Timeline Information**: Application deadlines and processing times

## 🔍 RAG Pipeline

### Vector Search with Qdrant
- **Semantic Search**: Advanced vector-based document retrieval
- **Contextual Matching**: Finds relevant agricultural documents and policies
- **Evidence-based Responses**: Provides source citations for all recommendations
- **Multi-language Support**: Handles queries in multiple languages

### Fallback Mechanisms
- **TF-IDF Fallback**: Lightweight text-based search when vector search is unavailable
- **Local Model Support**: Offline-capable responses using local LLMs
- **Graceful Degradation**: Maintains functionality even with partial service outages

## 📱 Mobile Application

### Flutter-based Cross-platform App
- **Native Performance**: Optimized for both Android and iOS
- **Offline Capability**: Basic functionality without internet connection
- **Voice Integration**: Speech-to-text and text-to-speech capabilities
- **Location Services**: Automatic location detection for contextual advice
- **Multi-language UI**: Supports Hindi and English interfaces

### Key Features
- **Chat Interface**: Natural conversation with the AI advisor
- **Query History**: Persistent storage of past interactions
- **Settings Management**: User preferences and configuration
- **Real-time Updates**: Live weather and market data integration
- **Push Notifications**: Weather alerts and important updates

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8+ 
- Flutter SDK 3.0+
- Docker and Docker Compose
- Google Gemini API key (for AI responses)

### 1. Clone and Setup Repository
```bash
git clone <repository-url>
cd agri-advisor
```

### 2. Backend Setup

#### Option A: Local Development
```bash
cd services/api
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

pip install -r requirements.txt
```



### 3. Environment Configuration
Create `.env` file in `services/api/`:
```env
# Required: Google Gemini API for AI responses
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Local model fallback
LOCAL_MODEL=microsoft/DialoGPT-small
EMBEDDING_MODEL=all-MiniLM-L6-v2

```

### 4. Start Backend Services

#### Local Development
```bash
cd services/api
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 5. Mobile App Setup
```bash
cd clients/mobile
flutter pub get

# Run on web (for testing)
flutter run -d chrome

# Run on connected device
flutter run

# Build for production
flutter build apk --release
```

### 6. Verify Installation
- **Backend Health**: http://127.0.0.1:8000/health
- **API Documentation**: http://127.0.0.1:8000/docs
- **Monitoring Dashboard**: http://127.0.0.1:3000 (Grafana)

## 🧪 Testing & Validation

### API Testing
```bash
# Test basic functionality
python scripts/test_api.py

# Test LangGraph supervisor
python scripts/test_supervisor.py

# Test all agents
python scripts/test_all_agents.py

# Test specific features
python scripts/test_weather_query.py
python scripts/test_finance_form.py
```

### Manual Testing
- **Health Check**: `GET /health`
- **Query Test**: `GET /query?text=wheat%20prices&location=Punjab`
- **Supervisor Test**: `GET /supervisor?text=weather%20forecast&location=Mumbai`

### Sample Queries
- "What's the weather forecast for wheat farming in Punjab?"
- "Tell me about government subsidies for organic farming"
- "What are the current market prices for rice?"
- "How to control pests in tomato crops?"

## 📊 API Reference

### Core Endpoints
| Endpoint | Method | Description | Rate Limit |
|----------|--------|-------------|------------|
| `/health` | GET | Basic health check | None |
| `/health/detailed` | GET | Detailed system status | None |
| `/query` | GET/POST | Ask agricultural questions | 10/min |
| `/supervisor` | GET | Test LangGraph supervisor | 10/min |
| `/ingest` | POST | Add new data sources | 5/hour |

### Query Parameters
- `text` (required): The agricultural question
- `location` (optional): Geographic location for context
- `crop` (optional): Specific crop type for targeted advice

### Response Format
```json
{
  "answer": "Comprehensive agricultural advice...",
  "confidence": 0.95,
  "evidence": [
    {
      "source": "Government Policy Document",
      "content": "Relevant policy information..."
    }
  ],
  "agents_used": ["weather", "crop"],
  "response_time": 1.2
}
```

## 🔧 Configuration & Customization

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `LOCAL_MODEL` | Fallback local LLM | `microsoft/DialoGPT-small` |
| `EMBEDDING_MODEL` | Vector embedding model | `all-MiniLM-L6-v2` |
| `QDRANT_URL` | Vector database URL | `http://localhost:6333` |
| `REDIS_URL` | Cache database URL | `redis://localhost:6379` |

### Agent Configuration
Each agent can be customized through configuration files:
- Confidence thresholds for response quality
- Response templates and formatting
- Domain-specific knowledge bases
- API endpoints and data sources

## 📈 Monitoring & Analytics

### Production Monitoring Stack
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Redis**: Query caching and session management
- **Structured Logging**: Comprehensive application logs

### Key Metrics
- Query response times and success rates
- Agent performance and accuracy
- Cache hit/miss ratios
- System resource utilization
- User interaction patterns

### Health Checks
- Database connectivity
- External API availability
- Agent system status
- Cache service health
- Overall system performance

## 🔒 Security & Performance

### Security Features
- **Rate Limiting**: 10 queries per minute per IP
- **API Key Authentication**: For administrative endpoints
- **Input Validation**: Comprehensive query sanitization
- **CORS Protection**: Cross-origin request handling
- **Automatic IP Blocking**: Protection against abuse

### Performance Optimizations
- **Redis Caching**: Intelligent query result caching
- **Response Compression**: Reduced bandwidth usage
- **Async Processing**: Non-blocking agent execution
- **Connection Pooling**: Efficient database connections
- **Load Balancing**: Horizontal scaling support


## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `python scripts/test_all_agents.py`
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use Flutter linting rules for mobile code
- Add comprehensive tests for new features
- Update documentation for API changes


## 🆘 Support & Troubleshooting

### Common Issues
1. **API Key Issues**: Ensure `GEMINI_API_KEY` is set correctly


### Getting Help
1. Check the troubleshooting section in this README
2. Review existing GitHub issues
3. Create a new issue with detailed information including:
   - Error messages and logs
   - Environment details
   - Steps to reproduce
   - Expected vs actual behavior

---


*KrishMitraAI - Empowering farmers with intelligent agricultural guidance*

