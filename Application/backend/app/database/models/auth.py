"""Authentication module: users and auth sessions."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import UserRole
from ..mixins import SoftDeleteMixin, TimestampMixin


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    roll_number = Column(String(30), unique=True, nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.STUDENT, nullable=False)
    phone = Column(String(20), nullable=True)
    profile_photo_url = Column(Text, nullable=True)
    accessibility_prefs = Column(Text, nullable=True)  # JSON string
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    auth_sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")
    club_memberships = relationship(
        "ClubMembership", back_populates="user", foreign_keys="ClubMembership.user_id"
    )
    advised_clubs = relationship("Club", back_populates="faculty_advisor")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    tickets_raised = relationship(
        "SupportTicket", back_populates="raised_by_user", foreign_keys="SupportTicket.raised_by"
    )


class AuthSession(Base, TimestampMixin):
    """Tracks issued JWT refresh tokens to support logout/revocation."""

    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    jti = Column(String(64), unique=True, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(64), nullable=True)

    user = relationship("User", back_populates="auth_sessions")
