# Agentic Agri Advisor

A comprehensive agricultural advisory system with AI agents, RAG pipeline, and mobile frontend.

## 🚀 Current Status

✅ **Phase 1**: Monorepo scaffolding - COMPLETE  
✅ **Phase 2**: RAG pipeline with vector store - COMPLETE  
✅ **Phase 3**: LLM integration - COMPLETE  
✅ **Phase 4**: Agent system - COMPLETE  
✅ **Phase 5**: Mobile frontend - COMPLETE  
✅ **Phase 6**: Advanced features & production readiness - COMPLETE  

## 🏗️ Architecture

```
agri-advisor/
├── services/
│   └── api/                 # FastAPI backend
│       ├── app/
│       │   ├── agents/      # 4 specialized AI agents
│       │   ├── main.py      # API endpoints
│       │   ├── llm_client.py # OpenAI + local LLM
│       │   ├── etl_service.py # Data ingestion
│       │   └── coordinator.py # Agent orchestration
│       └── requirements.txt
├── clients/
│   └── mobile/              # Flutter app
│       ├── lib/
│       │   ├── screens/     # UI screens
│       │   ├── providers/   # State management
│       │   └── models/      # Data models
│       └── pubspec.yaml
├── infra/
│   └── docker-compose.yml   # Qdrant + Postgres
└── scripts/                 # Setup & testing
```

## 🎯 Features

### 🤖 AI Agents with LangGraph Supervisor
- **Supervisor Agent**: LangGraph-based intelligent orchestration and decision-making
- **Weather Agent**: LLM-powered analysis of real-time weather data (WeatherAPI.com) with intelligent agricultural insights
- **Crop Agent**: Irrigation, fertilizer, pest control, planting advice
- **Finance Agent**: Market prices, subsidies, credit, investment guidance
- **Policy Agent**: Government schemes, eligibility, application help

### 🔍 RAG Pipeline
- Vector search with Qdrant (with local fallback)
- TF-IDF fallback for lightweight deployment
- Semantic document retrieval
- Evidence-based responses

### 📱 Mobile App
- Flutter-based cross-platform app
- Voice input/output capabilities
- Real-time query processing
- Query history and settings

## 🚀 Quick Start

### 1. Backend Setup
```bash
cd agri-advisor/services/api
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Environment Configuration
Create `.env` file in `services/api/`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
LOCAL_MODEL=microsoft/DialoGPT-small
EMBEDDING_MODEL=all-MiniLM-L6-v2
QDRANT_URL=http://localhost:6333
```

### 3. Start Backend
```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Start Mobile App
```bash
cd agri-advisor/clients/mobile
flutter pub get
flutter run -d chrome  # Web
# or flutter run        # Mobile device
```

**Debug Mode**: Tap the bug icon in the app bar to enable debug mode and test the LangGraph supervisor directly.

## 🧪 Testing

### API Testing
```bash
# Test basic functionality
python scripts/test_api.py

# Test LangGraph supervisor
python scripts/test_supervisor.py

# Test agent system
python scripts/test_agents.py

# Test all features
python scripts/test_all_agents.py
```

### Manual Testing
- Backend: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Query test: http://127.0.0.1:8000/query?text=wheat%20prices&location=Punjab

## 📊 API Endpoints

### Core Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check with component status
- `GET /query?text=...&location=...&crop=...` - Ask a question (rate limited: 10/min)
- `POST /query` - Ask a question (JSON body, rate limited: 10/min)
- `GET /supervisor?text=...&location=...&crop=...` - Test LangGraph supervisor directly
- `GET /agents?text=...&location=...&crop=...` - Test agent system (legacy endpoint)
- `POST /ingest` - Ingest new data (rate limited: 5/hour, API key required)

### Monitoring & Analytics
- `GET /metrics` - Application metrics (rate limited: 30/min)
- `GET /metrics/prometheus` - Prometheus-format metrics
- `GET /cache/info` - Cache statistics
- `POST /cache/clear` - Clear cache (admin API key required)
- `GET /analytics/performance` - Performance analytics
- `GET /analytics/insights` - User insights
- `GET /realtime/weather` - Live weather data
- `GET /realtime/market` - Live market data

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key for AI responses
- `LOCAL_MODEL`: Hugging Face model for local inference
- `EMBEDDING_MODEL`: Sentence transformer model
- `QDRANT_URL`: Vector database URL

### Agent Configuration
Each agent can be configured with:
- Confidence thresholds
- Response templates
- Domain-specific knowledge

## ✅ Phase 6: Advanced Features (Complete)

### Production-Ready Enhancements
- ✅ **Monitoring & Observability**
  - Prometheus metrics collection
  - Grafana dashboards
  - Comprehensive health checks
  - Application performance monitoring

- ✅ **Caching & Performance**
  - Redis-based query caching
  - Response time optimization
  - Cache hit/miss analytics
  - Intelligent cache invalidation

- ✅ **Security & Rate Limiting**
  - IP-based rate limiting (10 queries/minute)
  - API key authentication
  - Automatic IP blocking for abuse
  - Security headers and CORS protection

- ✅ **Production Infrastructure**
  - Docker containerization with monitoring stack
  - Health checks for all services
  - Logging with structured output
  - Error handling and recovery

## 🚀 Phase 7: Next Steps

### Future Enhancements
- [ ] **Enhanced Mobile Features**
  - Offline mode with local data sync
  - Push notifications for weather alerts
  - Image recognition for crop diseases

- [ ] **Multi-language Support**
  - Hindi/English support
  - Regional language agents
  - Voice recognition improvements

- [ ] **Advanced Analytics**
  - User behavior insights
  - Predictive analytics
  - Seasonal trend analysis

- [ ] **LangGraph Enhancements**
  - Parallel agent execution
  - Advanced workflow patterns
  - Conversation memory and context
  - Custom workflow templates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review existing issues
3. Create a new issue with detailed information

---

**Status**: Phase 6 in progress - Advanced features and production readiness

