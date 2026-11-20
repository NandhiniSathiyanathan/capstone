from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.auth import get_current_user
from app.database import documents_collection

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok= True)

MAX_FILE_SIZE = 10 * 1024 * 1024 # 10 MB

@router.post("/upload", status_code=201)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")

    filename = Path(file.filename).name

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    content = await file.read(MAX_FILE_SIZE + 1)

    if not content:
        raise HTTPException(status_code=400, detail="The file is empty")
    
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File must be 10 MB or smaller")
    
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="The file is not a valid PDF")
    
    document_id = str(uuid4())
    stored_path = UPLOAD_DIR / f"{document_id}.pdf"
    stored_path.write_bytes(content)
    
    documents_collection.insert_one({
        "_id": document_id,
        "filename": filename,
        "stored_path": str(stored_path),
        "owner_id": str(current_user["_id"]),
        "total_pages": None,
        "total_chunks": 0,
        "created_at": datetime.now(timezone.utc),
    })

    return {
        "message": "PDF uploaded successfully",
        "document_id": document_id,
        "filename": filename,
    }
    


