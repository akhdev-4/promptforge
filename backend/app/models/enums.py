"""Shared domain enums for prompts."""

from __future__ import annotations

import enum


class PromptType(str, enum.Enum):
    UI = "ui"
    FRONTEND = "frontend"
    BACKEND = "backend"
    # One prompt that produces an entire application, end to end.
    FULL_STACK = "full_stack"
    DATABASE = "database"
    API = "api"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    BUG_FIX = "bug_fix"
    DEPLOYMENT = "deployment"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    REFACTORING = "refactoring"
    # --- Creative / non-developer work ---
    IMAGE_GENERATION = "image_generation"
    PHOTO_EDITING = "photo_editing"
    VIDEO = "video"
    WRITING = "writing"
    OTHER = "other"


class Complexity(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class PromptStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class KitCategory(str, enum.Enum):
    """Curated starter-kit types for the Starter Kits catalog."""

    ECOMMERCE = "ecommerce"
    DASHBOARD = "dashboard"
    SAAS = "saas"
    LANDING = "landing"
    BLOG = "blog"
    MOBILE = "mobile"
    API_SERVICE = "api_service"
    PORTFOLIO = "portfolio"
    OTHER = "other"
