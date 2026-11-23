from app.chat import router as chat_router
from fastapi import FastAPI
from app.auth import router as auth_router
from app.documents import router as documents_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)

@app.get("/health")
def health_check():
    return {"status": "running"}
    