# Agentic Agri Advisor — Step-by-step Implementation Guide

**One-line:** Build an agentic, multimodal, multilingual agricultural advisor (MVP → production) that integrates weather, soil, crop, market, and policy data to provide grounded, explainable advice for Indian agricultural stakeholders.

---

## Table of contents

1. [Overview & goals](#overview--goals)
2. [Tech stack (recommended)](#tech-stack-recommended)
3. [Project structure](#project-structure)
4. [Phase 0 — Project setup & infra](#phase-0---project-setup--infra)
5. [Phase 1 — Data collection & ingestion (ETL)](#phase-1---data-collection--ingestion-etl)
6. [Phase 2 — Vector store, embeddings & RAG backbone](#phase-2---vector-store-embeddings--rag-backbone)
7. [Phase 3 — Models: LLM, ASR, Image models](#phase-3---models-llm-asr-image-models)
8. [Phase 4 — Agent design & orchestration](#phase-4---agent-design--orchestration)
9. [Phase 5 — Frontend & accessibility (mobile, IVR/SMS, offline)](#phase-5---frontend--accessibility-mobile-ivrsms-offline)
10. [Phase 6 — Safety, evaluation, MLOps & monitoring](#phase-6---safety-evaluation-mlops--monitoring)
11. [Phase 7 — Deployment & CI/CD](#phase-7---deployment--cicd)
12. [MVP checklist & 60-day roadmap](#mvp-checklist--60-day-roadmap)
13. [Appendix — useful commands & code snippets](#appendix--useful-commands--code-snippets)

---

## Overview & goals

**Goal:** Deliver a practical MVP that answers agronomy, irrigation, pest, market and policy questions in a grounded, explainable way for low-connectivity Indian contexts.

**Key product constraints:**
- Multilingual (Indian languages + code-switched queries)
- Offline / low-connectivity operation (caching & kiosk sync)
- Evidence-backed answers (RAG) with provenance + confidence
- Voice-first UX (ASR & TTS), SMS/IVR for feature phones
- Use only publicly available datasets

---

## Tech stack (recommended)

- **Backend / Orchestration:** Python, FastAPI, Uvicorn
- **RAG / LLM orchestration:** LlamaIndex or LangChain as scaffolding (custom safety wrapper)
- **Vector DB:** Qdrant (self-host) or Pinecone (managed). Milvus/Weaviate are alternatives.
- **Embeddings:** sentence-transformers (open models) or hosted embeddings
- **LLM models:** hosted stronger model for heavy reasoning + quantized open models for local/offline inference (`llama.cpp`/ggml)
- **ASR:** Whisper / XLS-R family (fine-tune for local dialects if possible)
- **TTS:** Local TTS or cloud TTS for production
- **Image models:** PyTorch (EfficientNet / MobileNet) for pest/disease classification
- **ETL:** Prefect / Airflow, Apache Tika + Tesseract for PDFs/scans
- **Databases:** PostgreSQL (structured), S3 (raw files), Redis (cache)
- **Client:** Flutter (mobile), React (dashboard)
- **Offline sync:** PouchDB + CouchDB OR SQLite with periodic sync endpoints
- **IVR/SMS:** Exotel / Twilio / Asterisk
- **MLOps:** MLflow / W&B; BentoML for model serving
- **Deployment:** Docker + Kubernetes (Helm) or managed services

---

## Project structure (monorepo suggestion)

```
agri-advisor/
├─ infra/                 # k8s manifests, terraform, helmcharts
├─ services/
│  ├─ api/                 # FastAPI app (orchestrator + coordinator)
│  ├─ agents/
│  │  ├─ weather_agent/
│  │  ├─ crop_agent/
│  │  ├─ finance_agent/
│  │  └─ policy_agent/
│  ├─ rag_worker/          # retrieval + generation service
│  └─ embeddings_service/  # local embedding endpoints
├─ data/                   # raw downloads, ingestion notebooks
├─ ml/                     # training code for image models, NLU, ASR finetune
├─ clients/
│  ├─ mobile/              # Flutter app
│  └─ dashboard/           # React admin dashboard
├─ docs/
└─ infra/
```

---

## Phase 0 - Project setup & infra

**Goal:** Create repository, basic infra, CI, dev workflow.

**Steps:**
1. Create a GitHub repository (or GitLab). Use branch protections and PR templates.
2. Choose where you'll host: GCP / AWS / Azure or self-host (bare-metal/VPS). For MVP, managed services speed you up.
3. Create basic Dockerfiles and a `docker-compose.yml` for local dev (Postgres, Redis, Qdrant).

**Quick start — local Qdrant (dev):**

```bash
# run qdrant locally
docker run -p 6333:6333 qdrant/qdrant

# run postgres locally
docker run -p 5432:5432 -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=agri postgres:15
```

4. Create initial CI with GitHub Actions: run linters, run unit tests, build Docker images.
5. Set up logging & basic monitoring (Prometheus + Grafana or cloud provider native)

---

## Phase 1 — Data collection & ingestion (ETL)

**Goal:** Build a normalized knowledge repository from public datasets: weather, mandi prices, soil maps, crop advisories, policy PDFs.

### 1. Identify public datasets (examples to fetch manually)
- IMD / GFS / ECMWF (weather grids)
- SoilGrids / national soil portals
- Agmarknet / state mandi price feeds
- ICAR & state agri advisories (PDFs)
- NABARD / PM-Kisan / state subsidy PDFs

> **Important:** Be sure you check each dataset's terms of use and cite them in your project.

### 2. ETL Pipeline (recommended tools)
- Use **Prefect** or **Airflow** for scheduled jobs.
- For HTML scraping: `requests` + `BeautifulSoup` + custom parsers.
- For PDFs: try `pdfminer.six` or `Apache Tika`. For scanned PDFs, run OCR with `pytesseract`.

### 3. Document processing & chunking
- Extract clean text, normalize encoding, detect language.
- Split long documents into chunks of 400–1000 tokens with overlap, attach metadata: `source_url`, `date`, `geo` (if any), `crop_tags`, `confidence`.

### 4. Embedding & vectorization
- Choose an embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) and embed each chunk.
- Upsert into vector DB with metadata payload.

**Example: chunking + embedding + upsert (Python skeleton)**

```python
# requirements: sentence-transformers, qdrant-client
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from uuid import uuid4

model = SentenceTransformer('all-MiniLM-L6-v2')
q = QdrantClient(url='http://localhost:6333')

# preprocessed passages
passages = [
    {"text": "...", "meta": {"source": "icardoc.pdf", "date": "2024-09-01", "geo": "Mandya"}},
    # ...
]

vectors = model.encode([p['text'] for p in passages])

points = []
for p, vec in zip(passages, vectors):
    points.append({
        "id": str(uuid4()),
        "vector": vec.tolist(),
        "payload": p['meta'] | {"text": p['text']}
    })

q.upsert(collection_name='agri_docs', points=points)
```

---

## Phase 2 — Vector store, retrieval & RAG backbone

**Goal:** Build a retrieval pipeline that returns grounded passages and their provenance; wire it into a RAG generation flow.

### Retrieval pipeline principles
- **Hybrid retrieval:** vector similarity + metadata filters (geo / date / crop type).
- **Reranking:** optionally use BM25 or a lightweight cross-encoder to rerank top-k.
- **Provenance:** each retrieved chunk must carry `source_url` & `timestamp` & `confidence`.

### RAG orchestrator (high level)
1. Receive user query + context (location, crop, date).
2. Perform intent classification and entity extraction (NLU).
3. Build a retrieval query (embedding + filters) → fetch top-k chunks.
4. Rerank / filter based on freshness/geo.
5. Prepare a prompt template that includes retrieved chunks as evidence and ask the LLM to answer, **explicitly** instructing it to quote sources and mark speculation.
6. Post-process LLM output to attach evidence bullets and a confidence score.

### Minimal FastAPI RAG endpoint (skeleton)

```python
# app/main.py (skeleton)
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str
    location: str | None = None
    crop: str | None = None

@app.post('/query')
async def handle_query(q: Query):
    # 1) NLU: extract intent/entities
    # 2) call retrieval service -> top_k passages
    # 3) call LLM generation service with prompt and passages
    # 4) return structured response: answer, evidence[], confidence
    return {"answer": "...", "evidence": [{"source":"...","excerpt":"..."}], "confidence":0.7}
```

**Prompt design tip:** Always include: prompt header explaining grounding requirement, followed by `[EVIDENCE START]` with numbered retrieved chunks, then user question, final instruction: "Use only the evidence to state facts. If unsure, say 'I don't know' or provide safe next steps. Cite the evidence with numbers."

---

## Phase 3 — Models: LLM, ASR, Image models

### LLM strategy
- **Two-tier approach**:
  - *Edge / on-device:* small quantized models (via `llama.cpp`) for offline quick replies and intent extraction.
  - *Cloud / server:* larger hosted LLM for complex reasoning, economic forecasting, or long-context RAG generation.
- **Quantize** models to 4-bit / 2-bit for mobile/edge where needed; keep a server fallback.

### ASR & TTS
- **ASR:** Whisper for baseline; XLS-R or fine-tuned models for better Indic dialect support.
- **TTS:** Use lightweight local TTS for offline replies or higher-quality cloud TTS for connected mode.

**ASR quick example using Whisper (server-side):**

```python
# pip install openai-whisper
import whisper
model = whisper.load_model('small')
result = model.transcribe('audio.wav', language='hi')
print(result['text'])
```

### Image models (pest/disease detection)
1. Gather labeled images (public datasets + field-collected photos).
2. Fine-tune a mobile-friendly architecture (MobileNetV3 / EfficientNet-lite) with transfer learning.
3. The model should return: `label`, `confidence`, `severity_estimate`, and `recommended_next_steps`.

**Quick inference skeleton (PyTorch):**

```python
import torch
from torchvision import transforms
from PIL import Image

model = torch.load('pest_model.pt', map_location='cpu')
model.eval()

transform = transforms.Compose([transforms.Resize(256), transforms.CenterCrop(224), transforms.ToTensor()])
img = Image.open('leaf.jpg')
input_tensor = transform(img).unsqueeze(0)
with torch.no_grad():
    logits = model(input_tensor)
    probs = torch.softmax(logits, dim=-1)
    pred = probs.argmax(dim=-1).item()
```

**Important:** Create a feedback loop to collect photos & label corrections from extension officers to retrain models.

---

## Phase 4 — Agent design & orchestration

**Principle:** Build specialized agents as microservices and a lightweight coordinator that merges their outputs.

### Agents (recommended list)
- **Weather Agent:** forecast ingestion, irrigation schedules, extreme event alerts.
- **Crop Agent:** crop calendar, fertilizer/pesticide recs, growth-stage based actions.
- **Soil Agent:** water-holding capacity lookup, salinity / pH advisories.
- **Pest Agent:** image diagnosis, recommended treatments, safety warnings.
- **Finance Agent:** mandi price trend analysis, credit & subsidy matching.
- **Policy Agent:** match eligibility & forms for schemes.

### Coordinator flow
1. Receive user query & context.
2. Run NLU to detect which agents to call.
3. Call agents in parallel; each returns structured outputs + evidence (if available).
4. Coordinator consolidates agent outputs and calls RAG/LLM synthesizer to produce a single human-readable answer with citations and action steps.

**Example agent response schema:**

```json
{
  "agent": "crop_agent",
  "result": {"advice": "Irrigate tonight with 20mm", "urgency": "high"},
  "evidence": [{"source":"icardoc.pdf","date":"2024-09-01","excerpt":"..."}],
  "confidence": 0.78
}
```

---

## Phase 5 — Frontend & accessibility (mobile, IVR/SMS, offline)

### Mobile (smartphone)
- **Framework:** Flutter (recommended) for small binary sizes and strong platform parity.
- **Features:** voice input / playback, short answer + "explain" button, evidence list, save/mark for offline view.
- **Local cache:** store recent answers and retrieved evidence in local DB (SQLite or PouchDB) for offline access.

### Feature-phone / low-connectivity
- **SMS flow:** accept short keywords and return templated answers; provide link to detailed report when online.
- **IVR:** voice menu for key queries; map to intents and use pre-rendered script templates.

### Offline sync strategy
- **Option A:** PouchDB (client) + CouchDB (server) for automatic sync and conflict resolution.
- **Option B:** Local SQLite + background sync endpoint that accepts deltas; sync when user is in connectivity.

**Kiosk sync:** Deploy a small Raspberry Pi or cheap server at village kiosk that syncs the latest vectors & model patches daily.

---

## Phase 6 — Safety, evaluation, MLOps & monitoring

### Grounding & anti-hallucination rules
1. Always attach at least one piece of retrieved evidence for every factual claim.
2. If evidence absent/conflicting, the agent must reply with "I don't know; here are safe next steps".
3. For high-risk recommendations (pesticide use, taking large loans), require human verification step.

### Logging & monitoring
- Log queries, evidence returned, final answers, and user feedback. Track hallucination incidents.
- Monitor model latency, error rates, and agent-specific metrics (e.g., pest classification accuracy).

### Evaluation
- Retrieval quality: top-k accuracy, relevance@k.
- Answer quality: human evaluation rubric (correctness, relevance, clarity).
- Real-world impact: pilot farmer surveys (utility, actions taken, ROI estimates).

### MLOps
- Version datasets & models (MLflow).
- Retrain image & NLU models with new labeled data.
- Automate deploys using CI/CD; stage models in canary before full rollout.

---

## Phase 7 — Deployment & CI/CD

**Suggested deployment flow**
1. Containerize services (FastAPI, agents) with Docker.
2. Create Helm charts for k8s or use managed containers for MVP.
3. Use GitHub Actions: on push to main -> run tests -> build images -> push to registry -> deploy to staging.

**Example Dockerfile (FastAPI)**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY . /app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**GitHub Actions skeleton:**
- `ci.yml`: run tests, lint, build image
- `deploy.yml`: push image to registry, apply helm charts

---

## MVP checklist & 60-day roadmap

**Week 0 (setup)**
- Repo, docker-compose (Postgres, Redis, Qdrant), basic FastAPI skeleton

**Week 1–2 (data & retrieval)**
- Ingest mandi prices, weather snapshots, select soil tiles
- Implement ETL notebook + chunking + embeddings
- Stand up Qdrant and upsert a first dataset

**Week 3–4 (RAG & LLM)**
- Implement retrieval endpoint + LLM prompt template
- Integrate small hosted LLM or local quantized model for generation
- Simple FastAPI `/query` endpoint returning answer + evidence

**Week 5–6 (agents & frontend)**
- Build weather & crop agents; coordinator to merge results
- Flutter prototype: voice input, show answer, save offline
- SMS/IVR stub integration

**Week 7+ (pilot & iterate)**
- Pilot in 1–2 regions, gather feedback, retrain models, harden safety flows

---

## Appendix — useful commands & code snippets

**Run Qdrant locally (docker)**

```bash
docker run -p 6333:6333 qdrant/qdrant
```

**Embedding + upsert (example repeated for convenience)**

```python
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from uuid import uuid4

model = SentenceTransformer('all-MiniLM-L6-v2')
q = QdrantClient(url='http://localhost:6333')

passages = [{"text":"Sample passage about irrigation","meta":{"source":"icardoc.pdf","date":"2024-09-01","geo":"Mandya"}}]
vectors = model.encode([p['text'] for p in passages])

points = []
for p, vec in zip(passages, vectors):
    points.append({
        "id": str(uuid4()),
        "vector": vec.tolist(),
        "payload": p['meta'] | {"text": p['text']}
    })

q.upsert(collection_name='agri_docs', points=points)
```

**FastAPI endpoint skeleton**

```python
# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Query(BaseModel):
    text: str
    location: str | None = None
    crop: str | None = None

@app.post('/query')
async def handle_query(q: Query):
    # TODO: NLU -> retrieval -> generate -> return structured response
    return {"answer":"This feature is not implemented yet"}
```

**Whisper ASR quick (server-side)**

```python
import whisper
model = whisper.load_model('small')
result = model.transcribe('audio.wav', language='hi')
print(result['text'])
```

---

## Next steps I can do for you (pick any):
- Scaffold the starter repo (FastAPI + RAG + embeddings) with working Dockerfiles.
- Create the Flutter app stub with voice input and query demo.
- Build an ETL notebook that ingests Agmarknet + SoilGrids and pushes embeddings to Qdrant.


---

*End of guide.*

