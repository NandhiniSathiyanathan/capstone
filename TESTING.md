# Manual Test Notes

| Check | Result |
|---|---|
| `GET /health` | Passed — returned status `running` |
| Register a new user | Passed — returned `201 Created` |
| Register the same email again | Passed — returned `409 Conflict` |
| Log in and call `GET /me` with the token | Passed — returned `200 OK` |
| Upload a text-based PDF | Passed — returned `201 Created`; extracted 13 pages and created 55 chunks |
| Create embeddings | Passed — 55 embeddings, shape `(55, 384)`, data type `float32` |
| Save and reload the FAISS index | Passed — loaded 55 vectors in a fresh Python process |
| Ask `/chat` an unrelated question | Passed — returned `200 OK` and said the answer was not found in the document |
| Document ownership check | Passed — a second user received `404 Not Found` when trying to chat with another user’s document |

## Not manually checked yet

- Whether one user is blocked from chatting with another user’s document.
- Behavior when MongoDB or Ollama is stopped.