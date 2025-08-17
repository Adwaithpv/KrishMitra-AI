"""
Seed Qdrant with a tiny sample so local queries have something to return.

Run:
    python -m app.seed_qdrant
"""

from __future__ import annotations

import os
from uuid import uuid4

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

try:
    from sentence_transformers import SentenceTransformer
except Exception as exc:  # pragma: no cover - optional import fallback
    raise RuntimeError(
        "sentence-transformers is required to run the seed script"
    ) from exc


COLLECTION_NAME = "agri_docs"


def get_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(url=url)


def ensure_collection(client: QdrantClient, vector_size: int) -> None:
    collections = client.get_collections().collections
    if not any(c.name == COLLECTION_NAME for c in collections):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def main() -> None:
    model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    model = SentenceTransformer(model_name)
    client = get_client()

    examples = [
        {
            "text": "For paddy at tillering stage, irrigate lightly every 3-4 days depending on soil moisture.",
            "meta": {
                "source": "icar_advice_2024.pdf",
                "date": "2024-09-01",
                "geo": "Mandya",
                "crop": "paddy",
            },
        },
        {
            "text": "Apply balanced NPK for cotton; avoid over-irrigation to reduce boll rot risk.",
            "meta": {
                "source": "state_agri_note.pdf",
                "date": "2024-08-15",
                "geo": "Surat",
                "crop": "cotton",
            },
        },
    ]

    texts = [e["text"] for e in examples]
    vectors = model.encode(texts)

    ensure_collection(client, vector_size=int(vectors.shape[1]))

    points = []
    for e, vec in zip(examples, vectors):
        points.append(
            {
                "id": str(uuid4()),
                "vector": np.asarray(vec, dtype=np.float32).tolist(),
                "payload": {"text": e["text"], **e["meta"]},
            }
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Seeded {len(points)} points into '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()

