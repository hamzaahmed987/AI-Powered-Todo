"""Base model class with common fields and utilities.

Provides timestamp mixins, UUID primary keys, and utility methods
for all SQLAlchemy ORM models.
"""

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4
from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class TimestampMixin:
    """Mixin providing created_at and updated_at timestamp columns.

    All models should inherit from this mixin to automatically track
    creation and modification times.
    """

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UUIDMixin:
    """Mixin providing UUID primary key column.

    Use this mixin on all models to get automatic UUID generation.
    """

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        unique=True,
        nullable=False,
    )


class IDMixin:
    """Mixin providing standard ID column with UUID."""

    def __init__(self, **kwargs):
        self.id = uuid4()
        super().__init__(**kwargs)


def as_dict(obj) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary.

    Args:
        obj: SQLAlchemy model instance

    Returns:
        dict: Model data without relationships
    """
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


def to_dict(obj, include_relationships: bool = False) -> Dict[str, Any]:
    """Convert SQLAlchemy model to dictionary with optional relationships.

    Args:
        obj: SQLAlchemy model instance
        include_relationships: Whether to include relationship data

    Returns:
        dict: Model data with optional relationship data
    """
    result = as_dict(obj)

    if include_relationships:
        for rel_name in obj.__mapper__.relationships.keys():
            rel = getattr(obj, rel_name, None)
            if rel is None:
                result[rel_name] = None
            elif isinstance(rel, list):
                result[rel_name] = [to_dict(item, include_relationships=False) for item in rel]
            else:
                result[rel_name] = to_dict(rel, include_relationships=False)

    return result