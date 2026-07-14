"""Helpdesk module: support tickets, ticket responses, and emergency reports."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import EmergencyCategory, EmergencyStatus
from ..mixins import TimestampMixin


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    raised_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    assigned_agent_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_open = Column(Boolean, default=True, nullable=False)
    is_offensive = Column(Boolean, default=False, nullable=False)
    resolution_rating = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    raised_by_user = relationship("User", back_populates="tickets_raised", foreign_keys=[raised_by])
    assigned_agent = relationship("User", foreign_keys=[assigned_agent_id])
    responses = relationship("TicketResponse", back_populates="ticket", cascade="all, delete-orphan")


class TicketResponse(Base):
    __tablename__ = "ticket_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    responder_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    body = Column(Text, nullable=False)
    is_resolution = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    ticket = relationship("SupportTicket", back_populates="responses")
    responder = relationship("User", foreign_keys=[responder_id])


class EmergencyReport(Base):
    """Harassment/medical/emergency report."""

    __tablename__ = "emergency_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reported_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="SET NULL"), nullable=True)
    category = Column(SAEnum(EmergencyCategory), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(EmergencyStatus), default=EmergencyStatus.REPORTED, nullable=False)
    handled_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    reporter = relationship("User", foreign_keys=[reported_by])
    event = relationship("Event", foreign_keys=[event_id])
    handler = relationship("User", foreign_keys=[handled_by])
