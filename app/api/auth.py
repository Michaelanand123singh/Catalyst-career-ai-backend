from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import jwt
import os
import json
import hashlib
from typing import Optional
from app.db import get_users_collection
from app.config import settings
from bson import ObjectId

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
TOKEN_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "1440"))  # 24h default
# Optional file store fallback; used only if Mongo is not configured
USERS_FILE = os.getenv("USERS_FILE", "data/users.json")

security = HTTPBearer()


class SignupRequest(BaseModel):
  name: str
  email: EmailStr
  password: str


class LoginRequest(BaseModel):
  email: EmailStr
  password: str


def _ensure_user_store():
  os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
  if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
      json.dump({"users": []}, f)


def _read_users():
  _ensure_user_store()
  with open(USERS_FILE, 'r', encoding='utf-8') as f:
    return json.load(f)


def _write_users(data):
  with open(USERS_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f)


def _hash_password(raw: str) -> str:
  return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _make_token(user):
  now = datetime.now(timezone.utc)
  payload = {
    "sub": user["id"],
    "email": user["email"],
    "name": user.get("name"),
    "iat": int(now.timestamp()),
    "exp": int((now + timedelta(minutes=TOKEN_EXP_MIN)).timestamp()),
  }
  return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def _decode_token(token: str):
  try:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Token expired")
  except jwt.InvalidTokenError:
    raise HTTPException(status_code=401, detail="Invalid token")


async def _get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
  data = _decode_token(creds.credentials)
  col = get_users_collection() if settings.MONGODB_URI else None
  user = None
  if col is not None:
    try:
      user = await col.find_one({"_id": ObjectId(data["sub"])})
      if user:
        return {"id": str(user["_id"]), "email": user["email"], "name": user.get("name")}
    except Exception:
      # Ignore DB errors and fall back to file store
      user = None
  # Fallback to file store
  users = _read_users().get("users", [])
  user = next((u for u in users if u["id"] == data["sub"]), None)
  if not user:
    raise HTTPException(status_code=401, detail="User not found")
  return {"id": user["id"], "email": user["email"], "name": user.get("name")}


@router.post("/auth/signup")
async def signup(payload: SignupRequest):
  col = get_users_collection() if settings.MONGODB_URI else None
  if col is not None:
    try:
      existing = await col.find_one({"email": payload.email.lower()})
      if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
      doc = {
        "name": payload.name.strip(),
        "email": payload.email.lower(),
        "password": _hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
        "last_login_at": datetime.now(timezone.utc),
      }
      result = await col.insert_one(doc)
      user = {"id": str(result.inserted_id), "email": doc["email"], "name": doc.get("name")}
      token = _make_token({"id": user["id"], "email": user["email"], "name": user.get("name")})
      return {"token": token, "user": user}
    except HTTPException:
      raise
    except Exception:
      # Fall through to file store if DB operation fails
      col = None
  # Fallback to file store
  users_blob = _read_users()
  users = users_blob.get("users", [])
  if any(u["email"].lower() == payload.email.lower() for u in users):
    raise HTTPException(status_code=400, detail="Email already registered")
  user = {
    "id": hashlib.md5(payload.email.lower().encode('utf-8')).hexdigest(),
    "name": payload.name.strip(),
    "email": payload.email,
    "password": _hash_password(payload.password),
  }
  users.append(user)
  users_blob["users"] = users
  _write_users(users_blob)
  token = _make_token(user)
  return {"token": token, "user": {"id": user["id"], "email": user["email"], "name": user["name"]}}


@router.post("/auth/login")
async def login(payload: LoginRequest):
  col = get_users_collection() if settings.MONGODB_URI else None
  if col is not None:
    try:
      user = await col.find_one({"email": payload.email.lower()})
      if not user or user.get("password") != _hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
      await col.update_one({"_id": user["_id"]}, {"$set": {"last_login_at": datetime.now(timezone.utc)}})
      public = {"id": str(user["_id"]), "email": user["email"], "name": user.get("name")}
      token = _make_token(public)
      return {"token": token, "user": public}
    except HTTPException:
      raise
    except Exception:
      # Fall through to file store if DB operation fails
      col = None
  # Fallback to file store
  users = _read_users().get("users", [])
  user = next((u for u in users if u["email"].lower() == payload.email.lower()), None)
  if not user or user["password"] != _hash_password(payload.password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
  token = _make_token(user)
  return {"token": token, "user": {"id": user["id"], "email": user["email"], "name": user.get("name")}}


@router.get("/auth/me")
async def me(current = Depends(_get_current_user)):
  return {"user": current}