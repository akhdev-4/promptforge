"""Metadata aggregation point for Alembic.

Import ``Base`` plus every model module here so that ``Base.metadata`` is fully
populated for autogenerate migrations and ``create_all``. New model modules must
be added to this file as the domain grows.
"""

from __future__ import annotations

from app.db.base_class import Base  # noqa: F401

# Domain models are imported for their side effect of registering with Base's
# metadata. They are added milestone by milestone.
from app.models.asset import PromptAsset  # noqa: F401,E402
from app.models.category import Category  # noqa: F401,E402
from app.models.collection import Collection, CollectionItem  # noqa: F401,E402
from app.models.community import (  # noqa: F401,E402
    Notification,
    PromptComment,
    PromptReport,
)
from app.models.embedding import PromptEmbedding  # noqa: F401,E402
from app.models.interaction import (  # noqa: F401,E402
    PromptBookmark,
    PromptLike,
    PromptRating,
)
from app.models.project import Component, Module, Project  # noqa: F401,E402
from app.models.prompt import Prompt, PromptVersion  # noqa: F401,E402
from app.models.tag import Tag, prompt_tags  # noqa: F401,E402
from app.models.team import PromptTeam, Team, TeamMember  # noqa: F401,E402
from app.models.user import User  # noqa: F401,E402
