import json
from pathlib import Path

from app.rag import embed_texts


vector_dir = Path("vector_store")
metadata_files = sorted(
    vector_dir.glob("*.json"),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)


if not metadata_files:
    raise FileNotFoundError("No chunk JSON file found in vector_store")

chunks = json.loads(metadata_files[0].read_text(encoding="utf-8"))
texts = [chunk["text"] for chunk in chunks]

embeddings = embed_texts(texts)

print("chunks:", len(texts))
print("Embedding shape:", embeddings.shape)
print("Embedding data type:", embeddings.dtype)
