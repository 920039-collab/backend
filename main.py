# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import random

app = FastAPI(title="Dating API (MVP)")

# Разрешаем фронтенду ходить на бэк
ALLOWED_ORIGINS = [
    "https://dating-frontend-bice.vercel.app",  # твой фронт на Vercel
    "http://localhost:5173",                    # локальная разработка (если пригодится)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Health/пинг ---
@app.get("/ping")
def ping():
    return {"ok": True, "message": "pong"}

# --- корень (чтобы не видеть Not Found) ---
@app.get("/")
def root():
    return {"ok": True, "message": "Dating API running. See /docs for swagger."}

# --- AI: старт диалога (болванка без внешних ключей) ---
class IcebreakerReq(BaseModel):
    profile: dict | None = None
    context: list[str] = []

@app.post("/ai/chat")
def ai_chat(req: IcebreakerReq):
    # Простейшие подсказки — чтобы фронт уже показывал варианты
    base = [
        "Привет! Видел(а), что ты любишь путешествия — какое место последнее впечатлило?",
        "Какой у тебя идеальный выходной?",
        "Смотрю, у нас совпадают интересы в музыке. Что сейчас в плейлисте?",
        "Выбираем: кофе с круассаном или вечерний киносеанс?",
        "Если бы завтра можно было улететь куда угодно — куда бы полетел(а)?",
        "Какая книга/фильм недооценены и почему?",
        "Чем занимаешься вне работы, чтобы перезарядиться?",
    ]
    # Чуть рандома + учёт контекста
    rand = random.sample(base, k=min(3, len(base)))
    if req.context:
        rand.insert(0, f"Кстати: «{req.context[-1]}» — звучит интересно! Расскажешь подробнее?")
    return {"suggestions": rand[:3]}
