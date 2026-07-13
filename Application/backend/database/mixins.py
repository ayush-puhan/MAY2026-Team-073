"""Reusable mixins shared across ClubConnect ORM models."""

from datetime import datetime,timezone
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Adds created_at / updated_at columns, maintained by SQLAlchemy and/or DB triggers."""

    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(onupdate=datetime.now(timezone.utc), nullable=True)


class SoftDeleteMixin:
    """Adds deleted_at for soft-delete. Used ONLY by User and Club."""

    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
