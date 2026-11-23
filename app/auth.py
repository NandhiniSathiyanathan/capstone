import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.database import users_collection

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TOKEN_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not JWT_SECRET:
    raise RuntimeError ("JWT_SECRET is missing from the .env file")

router = APIRouter()
password_hasher = CryptContext(schemes=["argon2"],deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
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

@router.post("/login")
def login_user(user: LoginRequest):
    email = user.email.strip().lower()
    saved_user = users_collection.find_one({"email": email})

    if not saved_user or not password_hasher.verify(
        user.password, saved_user["password_hash"]
    ):
        raise HTTPException(status_code=401, detail="Incorrect email or possword")

    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    token = jwt.encode(
        {"sub": email, "exp": expires},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    return {"access_token": token, "token_type": "bearer"}

def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
        )
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    current_user = users_collection.find_one({"email": email})
    if current_user is None:
        raise HTTPException(status_code=401,detail="user not found")

    return current_user


@router.get("/me")
def read_me(current_user=Depends(get_current_user)):
    return {
        "name": current_user["name"],
        "email": current_user["email"],
    } 