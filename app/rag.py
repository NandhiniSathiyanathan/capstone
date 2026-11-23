import requests

from pathlib import Path
import faiss

import numpy as np
from sentence_transformers import SentenceTransformer

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:0.5b"

MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIR = Path(__file__).resolve().parent.parent / "vector_store"
VECTOR_DIR.mkdir(parents=True, exist_ok=True)

_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model

def embed_texts(texts):
    model = get_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings.astype(np.float32)

def save_faiss_index(embeddings, document_id):
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    index_path = VECTOR_DIR / f"{document_id}.index"
    faiss.write_index(index, str(index_path))

    return index_path


def load_faiss_index(document_id):
    index_path = VECTOR_DIR / f"{document_id}.index"
    return faiss.read_index(str(index_path))

def generate_answer(question, context):
    prompt = f"""
You answer questions about a document.
use only the context below to answer.
If the context does not contain the answer, say:
"I could not find that information in the document."

Context:
{context}

Question:
{question}

Answer:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
    except requests.exception.ConnectionError as exc:
        raise RuntimeError(
            "connot connect to Ollama. check that Ollama is running."
        ) from exc
    except requests.exception.Timeout as exc:
        raise RuntimeError("Ollama took too long to answer.") from exc

    return response.json()["response"].strip()