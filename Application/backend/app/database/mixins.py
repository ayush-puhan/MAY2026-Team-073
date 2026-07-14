"""Reusable mixins shared across ClubConnect ORM models (classic Column style)."""

from datetime import datetime

from sqlalchemy import Column, DateTime


class TimestampMixin:
    """Adds created_at / updated_at columns, maintained by SQLAlchemy."""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, nullable=True)


class SoftDeleteMixin:
    """Adds deleted_at for soft-delete. Used ONLY by User and Club."""

    deleted_at = Column(DateTime, nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
