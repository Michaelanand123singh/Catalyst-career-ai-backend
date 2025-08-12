# backend/app/api/__init__.py
"""
API endpoints and routing for the Catalyst Career AI application
"""

from .chat import router
from .admin import router as admin_router
from .content import router as content_router

__all__ = ["router", "admin_router", "content_router"]