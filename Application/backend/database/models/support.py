"""Helpdesk module: support tickets, ticket responses, and emergency reports."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import EmergencyCategory, EmergencyStatus
from ..mixins import TimestampMixin


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    raised_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_offensive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resolution_rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    raised_by_user: Mapped["User"] = relationship(back_populates="tickets_raised", foreign_keys=[raised_by])
    assigned_agent: Mapped[Optional["User"]] = relationship(foreign_keys=[assigned_agent_id])
    responses: Mapped[List["TicketResponse"]] = relationship(back_populates="ticket", cascade="all, delete-orphan")


class TicketResponse(Base):
    __tablename__ = "ticket_responses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    responder_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_resolution: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    ticket: Mapped["SupportTicket"] = relationship(back_populates="responses")
    responder: Mapped["User"] = relationship(foreign_keys=[responder_id])


class EmergencyReport(Base):
    """Harassment/medical/emergency report."""

    __tablename__ = "emergency_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reported_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id: Mapped[Optional[int]] = mapped_column(ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    category: Mapped[EmergencyCategory] = mapped_column(SAEnum(EmergencyCategory), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[EmergencyStatus] = mapped_column(
        SAEnum(EmergencyStatus), default=EmergencyStatus.REPORTED, nullable=False
    )
    handled_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    reporter: Mapped[Optional["User"]] = relationship(foreign_keys=[reported_by])
    event: Mapped[Optional["Event"]] = relationship(foreign_keys=[event_id])
    handler: Mapped[Optional["User"]] = relationship(foreign_keys=[handled_by])
