import json
from pathlib import Path

from app.rag import embed_texts,load_faiss_index, save_faiss_index


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
document_id = chunks[0]["document_id"]

embeddings = embed_texts(texts)
index_path = save_faiss_index(embeddings,document_id)
loaded_index = load_faiss_index(document_id)

print("chunks:", len(chunks))
print("Embedding shape:", embeddings.shape)
print("Embedding data type:", embeddings.dtype)
print("FAISS vectors saved:", loaded_index.ntotal)
print("FAISS index file:", index_path.name)
