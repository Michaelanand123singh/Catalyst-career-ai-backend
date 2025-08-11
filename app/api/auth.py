from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import jwt
import os
import json
import hashlib

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
TOKEN_EXP_MIN = int(os.getenv("JWT_EXP_MIN", "1440"))  # 24h default
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


def _get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
  data = _decode_token(creds.credentials)
  users = _read_users().get("users", [])
  user = next((u for u in users if u["id"] == data["sub"]), None)
  if not user:
    raise HTTPException(status_code=401, detail="User not found")
  return {"id": user["id"], "email": user["email"], "name": user.get("name")}


@router.post("/auth/signup")
def signup(payload: SignupRequest):
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
def login(payload: LoginRequest):
  users = _read_users().get("users", [])
  user = next((u for u in users if u["email"].lower() == payload.email.lower()), None)
  if not user or user["password"] != _hash_password(payload.password):
    raise HTTPException(status_code=401, detail="Invalid credentials")
  token = _make_token(user)
  return {"token": token, "user": {"id": user["id"], "email": user["email"], "name": user.get("name")}}


@router.get("/auth/me")
def me(current = Depends(_get_current_user)):
  return {"user": current}


