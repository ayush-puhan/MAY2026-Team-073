"""Authentication module: users and auth sessions."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import UserRole
from ..mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    roll_number: Mapped[Optional[str]] = mapped_column(String(30), unique=True, nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    profile_photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    accessibility_prefs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON string
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    auth_sessions: Mapped[List["AuthSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    club_memberships: Mapped[List["ClubMembership"]] = relationship(
        back_populates="user", foreign_keys="ClubMembership.user_id"
    )
    advised_clubs: Mapped[List["Club"]] = relationship(back_populates="faculty_advisor")
    notifications: Mapped[List["Notification"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    documents: Mapped[List["Document"]] = relationship(back_populates="owner", cascade="all, delete-orphan")
    tickets_raised: Mapped[List["SupportTicket"]] = relationship(
        back_populates="raised_by_user", foreign_keys="SupportTicket.raised_by"
    )


class AuthSession(Base, TimestampMixin):
    """Tracks issued JWT refresh tokens to support logout/revocation."""

    __tablename__ = "auth_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    user: Mapped["User"] = relationship(back_populates="auth_sessions")
