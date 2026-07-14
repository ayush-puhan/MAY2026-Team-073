"""Authentication module: users and auth sessions."""

from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import AuthProvider, Gender, UserRole
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

    # Google Sign-In / academic / accessibility additions
    google_id = Column(String(255), unique=True, nullable=True)
    dob = Column(Date, nullable=True)
    auth_provider = Column(SAEnum(AuthProvider), default=AuthProvider.LOCAL, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    gender = Column(SAEnum(Gender), nullable=True)
    color_blind_mode = Column(Boolean, default=False, nullable=False)

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
    department = relationship("Department", back_populates="users")
    student_profile = relationship(
        "StudentProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    interest_links = relationship("UserInterest", back_populates="user", cascade="all, delete-orphan")
    club_join_applications = relationship(
        "ClubJoinApplication", back_populates="user", foreign_keys="ClubJoinApplication.user_id"
    )


class AuthSession(Base, TimestampMixin):
    """Tracks the single active JWT issued to a user after login.

    Stores the complete real JWT string (not just an identifier) so it can
    be looked up directly on each authenticated request and removed on
    logout or expiry."""

    __tablename__ = "auth_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(Text, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="auth_sessions")
