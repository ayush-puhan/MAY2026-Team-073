"""Club join application workflow: the review process leading up to (and
separate from) actual club_memberships rows."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import MembershipStatus


class ClubJoinApplication(Base):
    """A student's application to join a club. club_memberships remains the
    source of truth for actual membership; this table preserves the
    application history that led to it (or didn't)."""

    __tablename__ = "club_join_applications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    motivation = Column(Text, nullable=True)
    contribution = Column(Text, nullable=True)
    previous_experience = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)
    portfolio_url = Column(Text, nullable=True)
    resume_document_id = Column(Integer, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    weekly_availability = Column(String(100), nullable=True)
    status = Column(SAEnum(MembershipStatus), default=MembershipStatus.PENDING, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_comments = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    reviewed_at = Column(DateTime, nullable=True)

    user = relationship("User", foreign_keys=[user_id], back_populates="club_join_applications")
    club = relationship("Club", back_populates="join_applications")
    resume_document = relationship("Document", foreign_keys=[resume_document_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    interest_links = relationship(
        "ApplicationInterest", back_populates="application", cascade="all, delete-orphan"
    )


class ApplicationInterest(Base):
    """M:N bridge ClubJoinApplication<->Interest."""

    __tablename__ = "application_interests"
    __table_args__ = (
        UniqueConstraint("application_id", "interest_id", name="uq_application_interest"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(
        Integer, ForeignKey("club_join_applications.id", ondelete="CASCADE"), nullable=False
    )
    interest_id = Column(Integer, ForeignKey("interests.id", ondelete="CASCADE"), nullable=False)

    application = relationship("ClubJoinApplication", back_populates="interest_links")
    interest = relationship("Interest", back_populates="application_links")
