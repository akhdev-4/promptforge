"""Shared domain enums for prompts."""

from __future__ import annotations

import enum


class PromptType(str, enum.Enum):
    UI = "ui"
    BACKEND = "backend"
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
