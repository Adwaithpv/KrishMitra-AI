## Agri Advisor (MVP scaffold)

This is a minimal scaffold for the Agentic Agri Advisor.

### What's included
- **FastAPI Backend**: Complete API with RAG pipeline and agent orchestration
- **Agent System**: 4 specialized agents (Weather, Crop, Finance, Policy) with intelligent coordinator
- **Flutter Mobile App**: Voice-enabled mobile interface with offline capabilities
- **Qdrant Vector Database**: For semantic search and retrieval
- **ETL Service**: Data ingestion from agricultural sources
- **LLM Integration**: OpenAI and local model support
- **Docker Setup**: Complete containerized development environment

### Quick start

1. Start services

```bash
cd infra
docker compose up -d --build
```

2. Ingest sample data

```bash
curl -X POST http://localhost:8000/ingest
```

3. Test API

```bash
curl http://localhost:8000/health
curl "http://localhost:8000/query?text=irrigation%20for%20wheat&location=Punjab&crop=wheat"
curl "http://localhost:8000/agents?text=irrigation%20for%20wheat&location=Punjab&crop=wheat"
```

### Features
- **RAG Pipeline**: Retrieval + LLM generation with evidence attribution
- **Agent System**: 4 specialized agents (Weather, Crop, Finance, Policy) with intelligent routing
- **Mobile Interface**: Flutter app with voice input/output and offline support
- **Multiple LLM Options**: OpenAI GPT-3.5, local transformers, fallback
- **Agricultural Knowledge**: 12+ sample documents covering crops, weather, markets, policies
- **Location/Crop Filtering**: Context-aware responses with user preferences
- **Evidence Attribution**: Sources, confidence scores, and agent attribution
- **Coordinator**: Intelligent agent orchestration and response synthesis

### Next steps
- **Phase 6**: Safety, evaluation, MLOps & monitoring
- **Phase 7**: Deployment & CI/CD
- Add image-based pest/disease detection
- Implement SMS/IVR interfaces
- Add real-time data ingestion from public APIs
- Multilingual support (Indian languages)

