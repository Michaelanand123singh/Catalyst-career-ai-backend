from fastapi import APIRouter, Depends, HTTPException, Header, Query
from typing import Optional, List, Any, Dict
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone
import jwt
from app.config import settings
from app.db import get_blog_posts_collection, get_contact_submissions_collection
from app.models.schemas import BlogPost, BlogPostResponse, ContactSubmission, ContactSubmissionResponse
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
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    email = (payload or {}).get("email", "").lower()
    if email not in allowed_emails:
        raise HTTPException(status_code=403, detail="Not an admin user")


# Blog Post Endpoints
@router.post("/admin/blog-posts", response_model=BlogPostResponse)
async def create_blog_post(blog_post: BlogPost, _: Any = Depends(_require_admin)):
    col = get_blog_posts_collection()
    try:
        now = datetime.now(timezone.utc)
        blog_data = blog_post.model_dump()
        blog_data["created_at"] = now
        blog_data["updated_at"] = now
        
        if blog_post.status == "published" and not blog_post.published_at:
            blog_data["published_at"] = now
        
        result = await col.insert_one(blog_data)
        
        # Fetch the created document
        created_post = await col.find_one({"_id": result.inserted_id})
        created_post["id"] = str(created_post.pop("_id"))
        
        return BlogPostResponse(**created_post)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/blog-posts", response_model=List[BlogPostResponse])
async def list_blog_posts(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of posts to return"),
    skip: int = Query(0, description="Number of posts to skip"),
    _: Any = Depends(_require_admin)
):
    col = get_blog_posts_collection()
    try:
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        cursor = col.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        posts = []
        async for post in cursor:
            post["id"] = str(post.pop("_id"))
            posts.append(BlogPostResponse(**post))
        
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/blog-posts/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(post_id: str, _: Any = Depends(_require_admin)):
    col = get_blog_posts_collection()
    try:
        post = await col.find_one({"_id": ObjectId(post_id)})
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        post["id"] = str(post.pop("_id"))
        return BlogPostResponse(**post)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/blog-posts/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: str, 
    blog_post: BlogPost, 
    _: Any = Depends(_require_admin)
):
    col = get_blog_posts_collection()
    try:
        now = datetime.now(timezone.utc)
        update_data = blog_post.model_dump()
        update_data["updated_at"] = now
        
        # Handle published_at field
        if blog_post.status == "published":
            existing_post = await col.find_one({"_id": ObjectId(post_id)})
            if existing_post and not existing_post.get("published_at"):
                update_data["published_at"] = now
        
        result = await col.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        # Fetch the updated document
        updated_post = await col.find_one({"_id": ObjectId(post_id)})
        updated_post["id"] = str(updated_post.pop("_id"))
        
        return BlogPostResponse(**updated_post)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/blog-posts/{post_id}")
async def delete_blog_post(post_id: str, _: Any = Depends(_require_admin)):
    col = get_blog_posts_collection()
    try:
        result = await col.delete_one({"_id": ObjectId(post_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        return {"message": "Blog post deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Public Blog Endpoints (for frontend)
@router.get("/blog-posts", response_model=List[BlogPostResponse])
async def get_public_blog_posts(
    limit: int = Query(10, description="Number of posts to return"),
    skip: int = Query(0, description="Number of posts to skip")
):
    col = get_blog_posts_collection()
    try:
        cursor = col.find({"status": "published"}).sort("published_at", -1).skip(skip).limit(limit)
        posts = []
        async for post in cursor:
            post["id"] = str(post.pop("_id"))
            posts.append(BlogPostResponse(**post))
        
        return posts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blog-posts/{post_id}", response_model=BlogPostResponse)
async def get_public_blog_post(post_id: str):
    col = get_blog_posts_collection()
    try:
        post = await col.find_one({"_id": ObjectId(post_id), "status": "published"})
        if not post:
            raise HTTPException(status_code=404, detail="Blog post not found")
        
        post["id"] = str(post.pop("_id"))
        return BlogPostResponse(**post)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Contact Submission Endpoints
@router.post("/contact", response_model=ContactSubmissionResponse)
async def submit_contact(contact: ContactSubmission):
    col = get_contact_submissions_collection()
    try:
        now = datetime.now(timezone.utc)
        contact_data = contact.model_dump()
        contact_data["created_at"] = now
        contact_data["status"] = "new"
        
        result = await col.insert_one(contact_data)
        
        # Fetch the created document
        created_contact = await col.find_one({"_id": result.inserted_id})
        created_contact["id"] = str(created_contact.pop("_id"))
        
        return ContactSubmissionResponse(**created_contact)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/contact-submissions", response_model=List[ContactSubmissionResponse])
async def list_contact_submissions(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Number of submissions to return"),
    skip: int = Query(0, description="Number of submissions to skip"),
    _: Any = Depends(_require_admin)
):
    col = get_contact_submissions_collection()
    try:
        filter_query = {}
        if status:
            filter_query["status"] = status
        
        cursor = col.find(filter_query).sort("created_at", -1).skip(skip).limit(limit)
        submissions = []
        async for submission in cursor:
            submission["id"] = str(submission.pop("_id"))
            submissions.append(ContactSubmissionResponse(**submission))
        
        return submissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/admin/contact-submissions/{submission_id}", response_model=ContactSubmissionResponse)
async def get_contact_submission(submission_id: str, _: Any = Depends(_require_admin)):
    col = get_contact_submissions_collection()
    try:
        submission = await col.find_one({"_id": ObjectId(submission_id)})
        if not submission:
            raise HTTPException(status_code=404, detail="Contact submission not found")
        
        submission["id"] = str(submission.pop("_id"))
        return ContactSubmissionResponse(**submission)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/admin/contact-submissions/{submission_id}/status")
async def update_contact_status(
    submission_id: str,
    status: str,
    _: Any = Depends(_require_admin)
):
    col = get_contact_submissions_collection()
    try:
        now = datetime.now(timezone.utc)
        update_data = {"status": status}
        
        if status == "read":
            update_data["read_at"] = now
        elif status == "replied":
            update_data["replied_at"] = now
        
        result = await col.update_one(
            {"_id": ObjectId(submission_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Contact submission not found")
        
        return {"message": f"Contact submission status updated to {status}"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/admin/contact-submissions/{submission_id}")
async def delete_contact_submission(submission_id: str, _: Any = Depends(_require_admin)):
    col = get_contact_submissions_collection()
    try:
        result = await col.delete_one({"_id": ObjectId(submission_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Contact submission not found")
        
        return {"message": "Contact submission deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
