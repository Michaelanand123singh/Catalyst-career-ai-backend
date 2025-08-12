from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

_client: AsyncIOMotorClient | None = None


def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        if not settings.MONGODB_URI:
            raise RuntimeError("MONGODB_URI is not configured")
        _client = AsyncIOMotorClient(settings.MONGODB_URI)
    return _client


def get_db():
    return get_client()[settings.MONGODB_DB]


def get_users_collection():
    return get_db()[settings.MONGODB_USERS_COLLECTION]


def get_activity_collection():
    return get_db()[settings.MONGODB_ACTIVITY_COLLECTION]


def get_blog_posts_collection():
    return get_db()["blog_posts"]


def get_contact_submissions_collection():
    return get_db()["contact_submissions"]