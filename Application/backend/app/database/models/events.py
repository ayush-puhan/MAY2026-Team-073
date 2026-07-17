"""Event management module: events, registrations, attendance,
volunteer assignments, and external participants."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import EventStatus, ExternalParticipantType, RegistrationStatus, VolunteerTaskStatus
from ..mixins import TimestampMixin


class Event(Base, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (CheckConstraint("end_at >= start_at", name="ck_event_dates"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    venue = Column(String(255), nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    registration_deadline = Column(DateTime, nullable=True)
    capacity = Column(Integer, nullable=True)
    status = Column(SAEnum(EventStatus), default=EventStatus.SCHEDULED, nullable=False)
    banner = Column(String(255), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    requires_external_participants = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)

    club = relationship("Club", back_populates="events")
    creator = relationship("User", foreign_keys=[created_by])
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")
    attendance_records = relationship(
        "AttendanceRecord", back_populates="event", cascade="all, delete-orphan"
    )
    volunteer_assignments = relationship(
        "VolunteerAssignment", back_populates="event", cascade="all, delete-orphan"
    )
    external_participants = relationship(
        "ExternalParticipant", back_populates="event", cascade="all, delete-orphan"
    )
    interest_links = relationship("EventInterest", back_populates="event", cascade="all, delete-orphan")
    event_sessions = relationship("EventSession", back_populates="event", cascade="all, delete-orphan")


class EventSession(Base):
    __tablename__ = "event_sessions"
    __table_args__ = (CheckConstraint("end_at >= start_at", name="ck_session_dates"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    venue = Column(String(255), nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    session_order = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="event_sessions")


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user_registration"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(SAEnum(RegistrationStatus), default=RegistrationStatus.REGISTERED, nullable=False)
    qr_code_token = Column(String(128), unique=True, nullable=True)

    event = relationship("Event", back_populates="registrations")
    user = relationship("User", foreign_keys=[user_id])


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user_attendance"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    checked_in_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    recorded_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    event = relationship("Event", back_populates="attendance_records")
    user = relationship("User", foreign_keys=[user_id])


class VolunteerAssignment(Base):
    __tablename__ = "volunteer_assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    assignee_membership_id = Column(
        Integer, ForeignKey("club_memberships.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    task_description = Column(Text, nullable=False)
    status = Column(SAEnum(VolunteerTaskStatus), default=VolunteerTaskStatus.ASSIGNED, nullable=False)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="volunteer_assignments")
    assignee_membership = relationship("ClubMembership", back_populates="volunteer_assignments")
    assigner = relationship("User", foreign_keys=[assigned_by])


class ExternalParticipant(Base):
    __tablename__ = "external_participants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    affiliation = Column(String(255), nullable=True)
    participant_type = Column(SAEnum(ExternalParticipantType), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="external_participants")
    platform_user = relationship("User", foreign_keys=[user_id])
