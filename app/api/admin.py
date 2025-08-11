from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional, List, Any, Dict
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
import jwt
from app.config import settings
from app.db import get_users_collection, get_activity_collection
from bson import ObjectId
import os

router = APIRouter()
security = HTTPBearer(auto_error=False)


async def _require_admin(
    x_admin_token: Optional[str] = Header(default=None),
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    # 1) Legacy header token support
    configured_token = os.getenv("ADMIN_API_TOKEN") or settings.ADMIN_API_TOKEN
    if x_admin_token and configured_token and x_admin_token == configured_token:
        return

    # 2) JWT bearer support with allowed admin emails
    admin_emails_env = (os.getenv("ADMIN_EMAILS") or settings.ADMIN_EMAILS or "").strip()
    allowed_emails = [e.strip().lower() for e in admin_emails_env.split(",") if e.strip()]
    if not allowed_emails:
        # If neither ADMIN_API_TOKEN matches nor allowed emails configured, deny
        raise HTTPException(status_code=403, detail="Admin access not configured")
    if not creds:
        raise HTTPException(status_code=401, detail="Missing credentials")

    token = creds.credentials
    jwt_secret = os.getenv("JWT_SECRET", "dev_secret_change_me")
    try:
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])  # same as auth.py
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = (payload or {}).get("email", "").lower()
    if email not in allowed_emails:
        raise HTTPException(status_code=403, detail="Not an admin user")


@router.get("/admin/users")
async def list_users(_: Any = Depends(_require_admin)):
    col = get_users_collection()
    try:
        users_cursor = col.find({}, {"password": 0})
        users: List[Dict[str, Any]] = []
        async for u in users_cursor:
            users.append({
                "id": str(u.get("_id")),
                "email": u.get("email"),
                "name": u.get("name"),
                "created_at": u.get("created_at"),
                "last_login_at": u.get("last_login_at"),
            })
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/users/{user_id}")
async def get_user(user_id: str, _: Any = Depends(_require_admin)):
    col = get_users_collection()
    try:
        u = await col.find_one({"_id": ObjectId(user_id)}, {"password": 0})
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user": {
                "id": str(u.get("_id")),
                "email": u.get("email"),
                "name": u.get("name"),
                "created_at": u.get("created_at"),
                "last_login_at": u.get("last_login_at"),
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/activity")
async def list_activity(limit: int = 100, _: Any = Depends(_require_admin)):
    col = get_activity_collection()
    try:
        cursor = col.find({}).sort("ts", -1).limit(limit)
        items: List[Dict[str, Any]] = []
        async for a in cursor:
            a["id"] = str(a.pop("_id"))
            items.append(a)
        return {"activity": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/users/{user_id}/summary")
async def user_summary(user_id: str, _: Any = Depends(_require_admin)):
    col = get_activity_collection()
    try:
        # Aggregate recent searches/questions and simple counts by topic keywords
        cursor = col.find({"user_id": user_id}).sort("ts", -1).limit(200)
        topics = {
            "resume": 0,
            "interview": 0,
            "salary": 0,
            "skills": 0,
            "network": 0,
            "transition": 0,
        }
        recent_queries: List[str] = []
        count = 0
        async for a in cursor:
            q = a.get("message", "")
            if isinstance(q, str) and q:
                recent_queries.append(q)
                ql = q.lower()
                if "resume" in ql or "cv" in ql:
                    topics["resume"] += 1
                if "interview" in ql:
                    topics["interview"] += 1
                if "salary" in ql or "negoti" in ql:
                    topics["salary"] += 1
                if "skill" in ql or "learn" in ql:
                    topics["skills"] += 1
                if "network" in ql:
                    topics["network"] += 1
                if "transition" in ql or "switch" in ql or "change career" in ql:
                    topics["transition"] += 1
            count += 1

        primary_topic = max(topics, key=topics.get) if count else None
        summary = None
        if count:
            summary = (
                f"Primary interest: {primary_topic}. "
                f"Resume:{topics['resume']} Interview:{topics['interview']} Salary:{topics['salary']} "
                f"Skills:{topics['skills']} Network:{topics['network']} Transition:{topics['transition']}. "
                f"Total queries analyzed: {count}."
            )

        return {
            "user_id": user_id,
            "summary": summary,
            "topics": topics,
            "recent_queries": recent_queries[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


