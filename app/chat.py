from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import get_current_user
from app.database import documents_collection
from app.rag import retrieve_chunks, generate_answer

router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    document_id: str
    question: str

@router.post("/chat")
def chat_with_document(
    request: ChatRequest,
    current_user=Depends(get_current_user),
):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail= "Question cannot be empty")

    document = documents_collection.find_one({
        "_id": request.document_id,
        "owner_id": str(current_user["_id"]),
    })

    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    try:
        chunks = retrieve_chunks(question, request.document_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Document chunks were not found",
        )

    if not chunks:
        raise HTTPException(status_code=404, detail="No matching text found")

    context = "\n\n".join(
        f"[page {chunk['page']}]\n{chunk['text']}"
        for chunk in chunks
    )

    try:
        answer = generate_answer(question, context)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    sources = []
    seen_pages = set()

    for chunk in chunks:
        page = chunk["page"]

        if page not in seen_pages:
            sources.append({
                "document": document["filename"],
                "page": page,
            })
            seen_pages.add(page)

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }

    