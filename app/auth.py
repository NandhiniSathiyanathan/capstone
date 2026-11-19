from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database import users_collection

router = APIRouter()
password_hasher = CryptContext(schemes=["argon2"],deprecated="auto")

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

@router.post("/register", status_code=201)
def register_user(user: RegisterRequest):
    email = user.email.strip().lower()

    if users_collection.find_one({"email":email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    result = users_collection.insert_one({
        "name": user.name.strip(),
        "email": email,
        "password_hash": password_hasher.hash(user.password),
    })

    return {
        "message": "User registered successfullly",
        "user_id": str(result.inserted_id),
        "name": user.name.strip(),
        "email": email,
    }
