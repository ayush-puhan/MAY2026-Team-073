"""External relations module: sponsors and club-sponsor links."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from ..base import Base


class Sponsor(Base):
    """Kept as a distinct entity (rather than folding into a single per-club
    Sponsorship table) because one sponsor may support multiple clubs (M:N)."""

    __tablename__ = "sponsors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_person = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club_links = relationship("ClubSponsor", back_populates="sponsor", cascade="all, delete-orphan")


class ClubSponsor(Base):
    """M:N association table between clubs and sponsors."""

    __tablename__ = "club_sponsors"
    __table_args__ = (UniqueConstraint("club_id", "sponsor_id", name="uq_club_sponsor"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    sponsor_id = Column(Integer, ForeignKey("sponsors.id", ondelete="CASCADE"), nullable=False)
    sponsorship_details = Column(Text, nullable=True)

    club = relationship("Club", back_populates="sponsor_links")
    sponsor = relationship("Sponsor", back_populates="club_links")
