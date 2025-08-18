from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from typing import Optional, List
from datetime import datetime

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, using system environment variables")

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import (
        Distance,
        VectorParams,
        Filter,
        FieldCondition,
        MatchValue,
    )
except ImportError:
    QdrantClient = None
    Distance = None
    VectorParams = None
    Filter = None
    FieldCondition = None
    MatchValue = None
import numpy as np

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None  # type: ignore
from sklearn.feature_extraction.text import TfidfVectorizer
try:
    from .llm_client import LLMClient
    from .etl_service import ETLService
    from .supervisor import SupervisorAgent
    from .analytics import AnalyticsService
    from .realtime_data import RealTimeDataService
    from .monitoring import metrics_collector, health_checker
    from .cache import get_cache_service, cache_query_result
    from .security import limiter, security_manager, apply_rate_limit, get_client_ip, api_key_header
except ImportError:
    # Handle case when running directly (not as module)
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from llm_client import LLMClient
    from etl_service import ETLService
    from supervisor import SupervisorAgent
    from analytics import AnalyticsService
    from realtime_data import RealTimeDataService
    from monitoring import metrics_collector, health_checker
    from cache import get_cache_service, cache_query_result
    from security import limiter, security_manager, apply_rate_limit, get_client_ip, api_key_header

app = FastAPI(title="Agri Advisor API", version="0.1.0")

# Add rate limiter if available
if limiter:
    app.state.limiter = limiter
    from slowapi.errors import RateLimitExceeded
    from slowapi import _rate_limit_exceeded_handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Query(BaseModel):
    text: str
    location: Optional[str] = None
    crop: Optional[str] = None


def get_qdrant_client():
    if QdrantClient is None:
        raise RuntimeError("qdrant-client not installed")
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(url=url)


COLLECTION_NAME = "agri_docs"


def ensure_collection_exists():
    try:
        if QdrantClient is None:
            return
        client = get_qdrant_client()
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
    except Exception as exc:
        # Likely Qdrant not reachable in dev; continue with local fallback
        print(f"Qdrant not available, will use local fallback. Detail: {exc}")


# Lazy global model to avoid reloading per request
_embedding_model = None
_llm_client = None
_etl_service = None
_coordinator = None
_analytics_service = None
_realtime_data_service = None
_local_docs = []
_local_doc_vectors: np.ndarray | None = None
_tfidf_vectorizer: TfidfVectorizer | None = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None and SentenceTransformer is not None:
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def get_llm_client():
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client


def get_etl_service():
    global _etl_service
    if _etl_service is None:
        _etl_service = ETLService()
    return _etl_service


def get_local_docs():
    global _local_docs
    if not _local_docs:
        etl_service = get_etl_service()
        _local_docs = etl_service.get_all_data()
    return _local_docs


def get_supervisor():
    global _coordinator
    if _coordinator is None:
        _coordinator = SupervisorAgent()
    return _coordinator


def get_analytics_service():
    global _analytics_service
    if _analytics_service is None:
        _analytics_service = AnalyticsService()
    return _analytics_service


def get_realtime_data_service():
    global _realtime_data_service
    if _realtime_data_service is None:
        _realtime_data_service = RealTimeDataService()
    return _realtime_data_service


@app.get("/health")
async def health():
    """Basic health check"""
    return {"status": "ok"}

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check with component status"""
    return await health_checker.check_health()

@app.get("/metrics")
@apply_rate_limit("30/minute")
async def get_metrics(request: Request):
    """Get application metrics"""
    return metrics_collector.get_metrics()

@app.get("/metrics/prometheus")
async def prometheus_metrics():
    """Get metrics in Prometheus format"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(
        content=metrics_collector.export_prometheus_metrics(),
        media_type="text/plain"
    )

@app.get("/cache/info")
async def cache_info():
    """Get cache statistics"""
    cache_service = get_cache_service()
    return cache_service.get_cache_info()

@app.post("/cache/clear")
@apply_rate_limit("10/hour")
async def clear_cache(request: Request, pattern: str = "*", api_key: Optional[str] = Depends(api_key_header)):
    """Clear cache entries matching pattern"""
    # Check API key for admin operations
    user_info = security_manager.authenticate_api_key(api_key) if api_key else None
    if not user_info or not security_manager.check_permissions(user_info, "admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cache_service = get_cache_service()
    cleared = cache_service.clear_pattern(pattern)
    return {"message": f"Cleared {cleared} cache entries", "pattern": pattern}


@app.get("/")
async def root():
    return {"message": "Agri Advisor API is running. Use GET /query?text=... or POST /query."}


@app.on_event("startup")
async def startup_event():
    try:
        ensure_collection_exists()
    except Exception as e:
        # Do not crash API if Qdrant not ready; health endpoint can be used to check
        print(f"Startup warning: {e}")
    # prepare local fallback vectors (either ST or TF-IDF)
    local_docs = get_local_docs()
    texts = [d["text"] for d in local_docs]
    if texts:
        if SentenceTransformer is not None:
            model = get_embedding_model()
            vecs = model.encode(texts)
            norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
            globals()["_local_doc_vectors"] = (vecs / norms).astype(np.float32)
        else:
            # TF-IDF fallback that does not require heavy deps
            vect = TfidfVectorizer(max_features=2048)
            mat = vect.fit_transform(texts)
            # L2 normalize rows
            row_norms = np.sqrt((mat.multiply(mat)).sum(axis=1)) + 1e-12
            mat = mat.multiply(1.0 / row_norms)
            globals()["_tfidf_vectorizer"] = vect
            globals()["_local_doc_vectors"] = mat


def _run_query(q: Query, request=None):
    import time
    start_time = time.time()
    
    # Check cache first
    cache_service = get_cache_service()
    cache_key = cache_service._generate_cache_key(
        "query",
        text=q.text,
        location=q.location or "",
        crop=q.crop or ""
    )
    
    cached_result = cache_service.get(cache_key)
    if cached_result:
        # Add cache hit info and record metrics
        cached_result["cache_hit"] = True
        metrics_collector.record_query(
            query=q.text,
            location=q.location,
            crop=q.crop,
            response_time=0.001,  # Cache hit is very fast
            agent_used=cached_result.get("agent_used"),
            success=True
        )
        return cached_result
    
    # Get services
    analytics_service = get_analytics_service()
    realtime_service = get_realtime_data_service()
    
    client = None
    try:
        client = get_qdrant_client()
    except RuntimeError:
        pass  # Use local fallback
    q_norm = None
    query_vec = None
    if SentenceTransformer is not None:
        model = get_embedding_model()
        q_vec = model.encode(q.text)
        q_norm = q_vec / (np.linalg.norm(q_vec) + 1e-12)
        query_vec = q_vec.tolist()

    must_conditions: List = []
    if q.location and FieldCondition is not None:
        must_conditions.append(FieldCondition(key="geo", match=MatchValue(value=q.location)))
    if q.crop and FieldCondition is not None:
        must_conditions.append(FieldCondition(key="crop", match=MatchValue(value=q.crop)))

    query_filter = None
    if must_conditions and Filter is not None:
        query_filter = Filter(must=must_conditions)

    evidence = []
    scores = []
    try:
        if query_vec is None or client is None:
            raise RuntimeError("No embedding model available for Qdrant query")
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vec,
            limit=5,
            query_filter=query_filter,
            with_payload=True,
            with_vectors=False,
        )
        for r in results:
            payload = r.payload or {}
            evidence.append(
                {
                    "source": payload.get("source"),
                    "excerpt": payload.get("text"),
                    "date": payload.get("date"),
                    "geo": payload.get("geo"),
                    "crop": payload.get("crop"),
                    "score": r.score,
                }
            )
            scores.append(r.score)
    except Exception:
        # Local fallback using in-memory docs
        local_docs = get_local_docs()
        vecs = globals().get("_local_doc_vectors")
        if vecs is not None:
            if SentenceTransformer is not None and q_norm is not None and isinstance(vecs, np.ndarray):
                sims = (vecs @ q_norm.astype(np.float32))
            else:
                # TF-IDF similarity
                vect = globals().get("_tfidf_vectorizer")
                if vect is None:
                    sims = np.array([])
                else:
                    q_vec_tfidf = vect.transform([q.text])
                    # cosine since vectors are normalized
                    sims = (vecs @ q_vec_tfidf.T).toarray().ravel()
            if sims.size > 0:
                topk_idx = np.argsort(-sims)[:5]
                for idx in topk_idx:
                    d = local_docs[int(idx)]
                    sc = float(sims[int(idx)])
                    evidence.append(
                        {
                            "source": d["meta"]["source"],
                            "excerpt": d["text"],
                            "date": d["meta"]["date"],
                            "geo": d["meta"]["geo"],
                            "crop": d["meta"]["crop"],
                            "score": sc,
                        }
                    )
                    scores.append(sc)

    # Simple heuristic confidence: normalized mean score if available
    confidence = float(sum(scores) / len(scores)) if scores else 0.0

    # Try supervisor first (LangGraph-based agent orchestration)
    supervisor = get_supervisor()
    
    # Generate or extract session ID for conversation continuity
    session_id = None
    if request:
        session_id = request.headers.get('X-Session-ID')
    
    if not session_id:
        import uuid
        session_id = str(uuid.uuid4())[:12]
    
    supervisor_response = supervisor.process_query(q.text, q.location, q.crop, session_id)
    
    # Calculate response time
    response_time = time.time() - start_time
    
    # Check if supervisor provided high-quality responses
    supervisor_confidence = supervisor_response.get("confidence", 0.0)
    agents_consulted = supervisor_response.get('agents_consulted', [])
    workflow_trace = supervisor_response.get('workflow_trace', 'unknown')
    
    # Extract session ID from supervisor response (it may have been generated/updated)
    supervisor_session_id = supervisor_response.get('session_id', session_id)
    
    # Use lower threshold for all queries to prioritize supervisor routing
    confidence_threshold = 0.3  # Lower threshold to trust supervisor more
    
    # Always use supervisor response if agents were consulted or we have a session ID
    if supervisor_confidence > confidence_threshold or agents_consulted or supervisor_session_id:
        agent_used = supervisor_response.get("agent_used", "supervisor")
        answer = supervisor_response.get("answer", "")
        confidence = supervisor_response.get("confidence", 0.0)
        # Use evidence from agents, not static RAG data
        evidence = supervisor_response.get("evidence", evidence)
    else:
        # Fall back to LLM generation with static RAG evidence
        llm_client = get_llm_client()
        answer = llm_client.generate_answer(q.text, evidence)
        agent_used = "llm"
        confidence = round(confidence, 3)
    
    # Add real-time data insights if relevant
    realtime_insights = []
    
    # Realtime insight calls can cause event loop conflicts in ASGI if synchronous
    # Disable inline realtime calls to avoid 500s; expose via dedicated endpoints instead
    
    # Combine insights with main answer
    if realtime_insights:
        answer = f"{answer}\n\n📊 Real-time Updates:\n" + "\n".join(f"• {insight}" for insight in realtime_insights)
    
    # Log analytics
    analytics_service.log_query(
        query=q.text,
        location=q.location,
        crop=q.crop,
        response_time=response_time,
        success=True,
        agent_used=agent_used,
        confidence=confidence
    )
    
    # Record metrics
    metrics_collector.record_query(
        query=q.text,
        location=q.location,
        crop=q.crop,
        response_time=response_time,
        agent_used=agent_used,
        success=True
    )
    
    result = {
        "answer": answer, 
        "evidence": evidence, 
        "confidence": confidence,
        "response_time": round(response_time, 3),
        "agent_used": agent_used,
        "agents_consulted": agents_consulted,
        "workflow_trace": workflow_trace,
        "realtime_insights": len(realtime_insights),
        "cache_hit": False,
        "session_id": supervisor_session_id,  # Use session ID from supervisor response
        "conversation_context": supervisor_response.get("conversation_context"),
        "llm_routing": supervisor_response.get("llm_routing")
    }
    
    # Cache the result (TTL: 30 minutes for general queries)
    cache_service.set(cache_key, result, ttl=1800)
    
    return result


@app.post("/query")
@apply_rate_limit("10/minute")
async def handle_query(request: Request, q: Query):
    try:
        # Check for IP blocking
        client_ip = get_client_ip(request)
        if security_manager.is_ip_blocked(client_ip):
            raise HTTPException(status_code=403, detail="IP blocked due to suspicious activity")
        
        return _run_query(q, request)
    except Exception as e:
        metrics_collector.record_query(
            query=q.text,
            location=q.location,
            crop=q.crop,
            success=False
        )
        return {"error": str(e), "status": "failed"}


@app.get("/query")
@apply_rate_limit("10/minute")
async def handle_query_get(request: Request, text: str, location: Optional[str] = None, crop: Optional[str] = None):
    q = Query(text=text, location=location, crop=crop)
    try:
        # Check for IP blocking
        client_ip = get_client_ip(request)
        if security_manager.is_ip_blocked(client_ip):
            raise HTTPException(status_code=403, detail="IP blocked due to suspicious activity")
        
        return _run_query(q, request)
    except Exception as e:
        metrics_collector.record_query(
            query=q.text,
            location=q.location,
            crop=q.crop,
            success=False
        )
        return {"error": str(e), "status": "failed"}


@app.post("/ingest")
@apply_rate_limit("5/hour")
async def ingest_data(request: Request, api_key: Optional[str] = Depends(api_key_header)):
    """Ingest agricultural data"""
    try:
        etl_service = get_etl_service()
        data = etl_service.get_all_data()
        
        # Rebuild vectors with new data
        texts = [d["text"] for d in data]
        if texts:
            if SentenceTransformer is not None:
                model = get_embedding_model()
                vecs = model.encode(texts)
                norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-12
                globals()["_local_doc_vectors"] = (vecs / norms).astype(np.float32)
            else:
                vect = TfidfVectorizer(max_features=2048)
                mat = vect.fit_transform(texts)
                row_norms = np.sqrt((mat.multiply(mat)).sum(axis=1)) + 1e-12
                mat = mat.multiply(1.0 / row_norms)
                globals()["_tfidf_vectorizer"] = vect
                globals()["_local_doc_vectors"] = mat
        
        return {"message": f"Ingested {len(data)} documents", "count": len(data)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/supervisor")
async def test_supervisor(text: str, location: Optional[str] = None, crop: Optional[str] = None):
    """Test supervisor system directly with LangGraph workflow"""
    try:
        supervisor = get_supervisor()
        response = supervisor.process_query(text, location, crop)
        return {
            "query": text,
            "location": location,
            "crop": crop,
            "response": response,
            "workflow_trace": response.get("workflow_trace", "unknown"),
            "agents_consulted": response.get("agents_consulted", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/agents")
async def test_agents(text: str, location: Optional[str] = None, crop: Optional[str] = None):
    """Test agent responses directly (legacy endpoint)"""
    try:
        supervisor = get_supervisor()
        response = supervisor.process_query(text, location, crop)
        return response
    except Exception as e:
        return {"error": str(e)}


@app.get("/analytics/performance")
async def get_performance_stats(hours: int = 24):
    """Get system performance statistics"""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_performance_stats(hours)
    except Exception as e:
        return {"error": str(e)}


@app.get("/analytics/insights")
async def get_user_insights(hours: int = 24):
    """Get user behavior insights"""
    try:
        analytics_service = get_analytics_service()
        return analytics_service.get_user_insights(hours)
    except Exception as e:
        return {"error": str(e)}


@app.get("/analytics/export")
async def export_analytics(format: str = "json"):
    """Export analytics data"""
    try:
        analytics_service = get_analytics_service()
        export_file = analytics_service.export_data(format)
        return {"message": "Analytics exported successfully", "file": export_file}
    except Exception as e:
        return {"error": str(e)}


@app.get("/realtime/weather")
async def get_weather_data(location: str):
    """Get real-time weather data"""
    try:
        realtime_service = get_realtime_data_service()
        weather_data = await realtime_service.get_weather_data(location)
        if weather_data:
            return {
                "location": weather_data.location,
                "temperature": weather_data.temperature,
                "humidity": weather_data.humidity,
                "rainfall": weather_data.rainfall,
                "wind_speed": weather_data.wind_speed,
                "forecast": weather_data.forecast,
                "timestamp": weather_data.timestamp.isoformat()
            }
        else:
            return {"error": f"Weather data not available for {location}"}
    except Exception as e:
        return {"error": str(e)}


@app.get("/realtime/market")
async def get_market_data(crop: str, location: Optional[str] = None):
    """Get real-time market data"""
    try:
        realtime_service = get_realtime_data_service()
        market_data = await realtime_service.get_market_data(crop, location)
        return [
            {
                "crop": data.crop,
                "location": data.location,
                "price": data.price,
                "unit": data.unit,
                "change": data.change,
                "volume": data.volume,
                "timestamp": data.timestamp.isoformat()
            }
            for data in market_data
        ]
    except Exception as e:
        return {"error": str(e)}


@app.post("/realtime/update-cache")
async def update_realtime_cache():
    """Update real-time data cache"""
    try:
        realtime_service = get_realtime_data_service()
        await realtime_service.update_cache()
        return {"message": "Real-time data cache updated successfully"}
    except Exception as e:
        return {"error": str(e)}

