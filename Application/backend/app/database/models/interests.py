"""Normalized interest system: a shared master list of interests, mapped
to users, clubs, and events via dedicated many-to-many tables."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Interest(Base):
    """Centralized master table of interest tags (e.g. Robotics, Photography)."""

    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user_links = relationship("UserInterest", back_populates="interest", cascade="all, delete-orphan")
    club_links = relationship("ClubInterest", back_populates="interest", cascade="all, delete-orphan")
    event_links = relationship("EventInterest", back_populates="interest", cascade="all, delete-orphan")
    application_links = relationship(
        "ApplicationInterest", back_populates="interest", cascade="all, delete-orphan"
    )


class UserInterest(Base):
    """M:N bridge User<->Interest."""

    __tablename__ = "user_interests"
    __table_args__ = (UniqueConstraint("user_id", "interest_id", name="uq_user_interest"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="interest_links")
    interest = relationship("Interest", back_populates="user_links")


class ClubInterest(Base):
    """M:N bridge Club<->Interest."""

    __tablename__ = "club_interests"
    __table_args__ = (UniqueConstraint("club_id", "interest_id", name="uq_club_interest"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("Club", back_populates="interest_links")
    interest = relationship("Interest", back_populates="club_links")


class EventInterest(Base):
    """M:N bridge Event<->Interest (event-specific topics, distinct from the
    parent club's category)."""

    __tablename__ = "event_interests"
    __table_args__ = (UniqueConstraint("event_id", "interest_id", name="uq_event_interest"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False)
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("Event", back_populates="interest_links")
    interest = relationship("Interest", back_populates="event_links")
