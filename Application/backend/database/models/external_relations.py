"""External relations module: sponsors and club-sponsor links."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional,TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .__init__ import *

class Sponsor(Base):
    """Kept as a distinct entity (rather than folding into a single per-club
    Sponsorship table) because one sponsor may support multiple clubs (M:N)."""

    __tablename__ = "sponsors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    club_links: Mapped[List["ClubSponsor"]] = relationship(back_populates="sponsor", cascade="all, delete-orphan")


class ClubSponsor(Base):
    """M:N association table between clubs and sponsors."""

    __tablename__ = "club_sponsors"
    __table_args__ = (UniqueConstraint("club_id", "sponsor_id", name="uq_club_sponsor"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    sponsor_id: Mapped[int] = mapped_column(ForeignKey("sponsors.id", ondelete="CASCADE"), nullable=False)
    sponsorship_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    club: Mapped["Club"] = relationship(back_populates="sponsor_links")
    sponsor: Mapped["Sponsor"] = relationship(back_populates="club_links")
