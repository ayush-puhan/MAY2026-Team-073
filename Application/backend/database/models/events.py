"""Event management module: events, registrations, attendance,
volunteer assignments, and external participants."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional,TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import EventStatus, ExternalParticipantType, RegistrationStatus, VolunteerTaskStatus
from ..mixins import TimestampMixin

if TYPE_CHECKING:
    from .__init__ import *

class Event(Base, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (CheckConstraint("end_at >= start_at", name="ck_event_dates"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    start_at: Mapped[datetime] = mapped_column(nullable=False)
    end_at: Mapped[datetime] = mapped_column(nullable=False)
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    capacity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[EventStatus] = mapped_column(SAEnum(EventStatus), default=EventStatus.SCHEDULED, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    requires_external_participants: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    club: Mapped["Club"] = relationship(back_populates="events")
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    registrations: Mapped[List["EventRegistration"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    attendance_records: Mapped[List["AttendanceRecord"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    volunteer_assignments: Mapped[List["VolunteerAssignment"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    external_participants: Mapped[List["ExternalParticipant"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class EventRegistration(Base):
    __tablename__ = "event_registrations"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user_registration"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    status: Mapped[RegistrationStatus] = mapped_column(
        SAEnum(RegistrationStatus), default=RegistrationStatus.REGISTERED, nullable=False
    )
    qr_code_token: Mapped[Optional[str]] = mapped_column(String(128), unique=True, nullable=True)

    event: Mapped["Event"] = relationship(back_populates="registrations")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (UniqueConstraint("event_id", "user_id", name="uq_event_user_attendance"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    checked_in_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    recorded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    event: Mapped["Event"] = relationship(back_populates="attendance_records")
    user: Mapped["User"] = relationship(foreign_keys=[user_id])


class VolunteerAssignment(Base):
    __tablename__ = "volunteer_assignments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    assignee_membership_id: Mapped[int] = mapped_column(
        ForeignKey("club_memberships.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    task_description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[VolunteerTaskStatus] = mapped_column(
        SAEnum(VolunteerTaskStatus), default=VolunteerTaskStatus.ASSIGNED, nullable=False
    )
    due_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    event: Mapped["Event"] = relationship(back_populates="volunteer_assignments")
    assignee_membership: Mapped["ClubMembership"] = relationship(back_populates="volunteer_assignments")
    assigner: Mapped["User"] = relationship(foreign_keys=[assigned_by])


class ExternalParticipant(Base):
    __tablename__ = "external_participants"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    affiliation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    participant_type: Mapped[ExternalParticipantType] = mapped_column(
        SAEnum(ExternalParticipantType), nullable=False
    )
    registered_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    event: Mapped["Event"] = relationship(back_populates="external_participants")
