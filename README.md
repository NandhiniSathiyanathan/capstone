# Mini RAG Document Assistant

A beginner-friendly backend API that lets a logged-in user upload a PDF and ask questions about its content. Answers include page sources.

## Project flow

1. A user registers and logs in.
2. The user uploads a PDF.
3. The app extracts text and splits it into chunks with page numbers.
4. Sentence Transformers creates embeddings for the chunks.
5. FAISS saves the embeddings in a searchable index.
6. Ollama answers questions using the matching document chunks.

## Tools used

- FastAPI and Uvicorn — API and local server
- MongoDB — users and document records
- JWT and Argon2 — authentication and password hashing
- PyMuPDF — PDF text extraction
- Sentence Transformers — text embeddings
- FAISS — vector search
- Ollama with `qwen2.5:0.5b` — local answer generation

## Requirements

- Python
- MongoDB running locally
- Ollama with the `qwen2.5:0.5b` model

## Run locally

## Run locally

1. Install Python, MongoDB, and Ollama.
2. Open PowerShell in the project folder and create a virtual environment:

   ```powershell
   py -3.14 -m venv .venv
   ```

3. Install the Python packages:

   ```powershell
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. For a fresh setup, copy `.env.example` to `.env`, then replace the placeholder `JWT_SECRET` with a private random secret. Never upload `.env` to GitHub.
5. Make sure MongoDB and Ollama are running. Download the Ollama model if needed:

   ```powershell
   ollama pull qwen2.5:0.5b
   ```

6. Start the API:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

7. Open <http://127.0.0.1:8000/docs> to view the API.

## API endpoints

| Method | Route | Purpose |
|---|---|---|
| GET | `/health` | Check that the API is running |
| POST | `/register` | Create an account |
| POST | `/login` | Log in and receive a token |
| GET | `/me` | Get the logged-in user |
| POST | `/documents/upload` | Upload and process a PDF |
| POST | `/chat` | Ask a question about an owned PDF |

## Chat request

Send a document ID from the upload response and a question:

```json
{
  "document_id": "YOUR_DOCUMENT_ID",
  "question": "What is the project goal?"
}
```

The response contains an answer and source page numbers. If the document does not contain the answer, the app should say so.

## Project notes

- PDF uploads are limited to 10 MB.
- The PDF must contain selectable text; scanned PDFs need OCR, which this project does not include.
- Uploaded PDFs, chunk metadata, and FAISS index files are stored locally and ignored by Git.
- MongoDB stores user and document records. FAISS stores searchable vectors.

## Tested manually

- Health check returned a running status.
- Registration and login worked.
- PDF upload extracted text and created 55 chunks.
- FAISS saved and reloaded 55 vectors.
- Chat returned an answer with source pages.
- An unrelated question received the “not found in the document” response.