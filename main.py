from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import os
from jose import jwt, JWTError

from data.storage import USERS, PROFILES, MATCHES, LIKES, MESSAGES
from ai.ai_chat import get_ai_starter

app = FastAPI(title="Dating App API (Improved)")

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

class SignUp(BaseModel):
    phone: str
    password: str
    display_name: str

class SignIn(BaseModel):
    phone: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class Profile(BaseModel):
    user_id: int
    bio: Optional[str] = ""
    interests: List[str] = []
    gender: Optional[str] = None
    looking_for: Optional[str] = None
    city: Optional[str] = None
    birthdate: Optional[str] = None
    verified: bool = False

class CandidateCard(BaseModel):
    user_id: int
    display_name: str
    city: Optional[str] = None
    interests: List[str] = []
    compatibility: float = 0.0

class Swipe(BaseModel):
    target_user_id: int
    action: str = Field(pattern="^(like|pass)$")

class Message(BaseModel):
    from_user_id: int
    to_user_id: int
    text: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=6)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(token: str) -> int:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/auth/signup", response_model=Token)
def signup(body: SignUp):
    if body.phone in USERS:
        raise HTTPException(400, "Phone already registered")
    user_id = len(USERS) + 1
    USERS[body.phone] = {"id": user_id, "password": body.password, "display_name": body.display_name}
    PROFILES[user_id] = Profile(user_id=user_id)
    token = create_access_token({"sub": str(user_id)})
    return Token(access_token=token)

@app.post("/auth/signin", response_model=Token)
def signin(body: SignIn):
    user = USERS.get(body.phone)
    if not user or user["password"] != body.password:
        raise HTTPException(400, "Invalid credentials")
    token = create_access_token({"sub": str(user["id"])})
    return Token(access_token=token)

@app.get("/ai/starter")
def ai_starter():
    """AI-предложение для начала разговора"""
    return {"starter": get_ai_starter()}
