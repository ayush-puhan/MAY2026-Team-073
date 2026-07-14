"""Club management module: clubs, creation requests, memberships,
committees, committee memberships, and announcements."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from ..base import Base
from ..enums import (
    AnnouncementAudience,
    ClubMemberRole,
    ClubRequestStatus,
    ClubStatus,
    MembershipStatus,
)
from ..mixins import SoftDeleteMixin, TimestampMixin


class Club(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    objectives = Column(Text, nullable=True)
    logo_url = Column(Text, nullable=True)
    status = Column(SAEnum(ClubStatus), default=ClubStatus.ACTIVE, nullable=False)
    faculty_advisor_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    member_count_cache = Column(Integer, default=0, nullable=False)

    faculty_advisor = relationship("User", back_populates="advised_clubs")
    memberships = relationship("ClubMembership", back_populates="club", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="club", cascade="all, delete-orphan")
    committees = relationship("Committee", back_populates="club", cascade="all, delete-orphan")
    budgets = relationship("Budget", back_populates="club", cascade="all, delete-orphan")
    announcements = relationship("Announcement", back_populates="club", cascade="all, delete-orphan")
    sponsor_links = relationship("ClubSponsor", back_populates="club", cascade="all, delete-orphan")
    interest_links = relationship("ClubInterest", back_populates="club", cascade="all, delete-orphan")
    join_applications = relationship(
        "ClubJoinApplication", back_populates="club", cascade="all, delete-orphan"
    )


class ClubCreationRequest(Base):
    """Student-submitted new-club proposal."""

    __tablename__ = "club_creation_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    proposed_name = Column(String(255), nullable=False)
    proposed_category = Column(String(100), nullable=True)
    proposal_description = Column(Text, nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(SAEnum(ClubRequestStatus), default=ClubRequestStatus.SUBMITTED, nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_comments = Column(Text, nullable=True)
    resulting_club_id = Column(Integer, ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)

    requester = relationship("User", foreign_keys=[requested_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    resulting_club = relationship("Club", foreign_keys=[resulting_club_id])


class ClubMembership(Base):
    """Single source of truth for the membership workflow: Pending -> Approved/Rejected,
    or Withdrawn. Also carries the per-club role (Assumption: club-scoped roles live
    here, not on the global User.role)."""

    __tablename__ = "club_memberships"
    __table_args__ = (UniqueConstraint("user_id", "club_id", name="uq_user_club"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    role_in_club = Column(SAEnum(ClubMemberRole), default=ClubMemberRole.MEMBER, nullable=False)
    status = Column(SAEnum(MembershipStatus), default=MembershipStatus.PENDING, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    decided_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason = Column(Text, nullable=True)

    user = relationship("User", back_populates="club_memberships", foreign_keys=[user_id])
    club = relationship("Club", back_populates="memberships")
    approver = relationship("User", foreign_keys=[approved_by])
    committee_links = relationship(
        "CommitteeMembership", back_populates="membership", cascade="all, delete-orphan"
    )
    volunteer_assignments = relationship(
        "VolunteerAssignment", back_populates="assignee_membership", cascade="all, delete-orphan"
    )


class Committee(Base):
    __tablename__ = "committees"
    __table_args__ = (UniqueConstraint("club_id", "name", name="uq_committee_name_per_club"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("Club", back_populates="committees")
    member_links = relationship(
        "CommitteeMembership", back_populates="committee", cascade="all, delete-orphan"
    )


class CommitteeMembership(Base):
    """M:N bridge Committee<->ClubMembership (association table)."""

    __tablename__ = "committee_memberships"
    __table_args__ = (UniqueConstraint("committee_id", "membership_id", name="uq_committee_membership"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    committee_id = Column(Integer, ForeignKey("committees.id", ondelete="CASCADE"), nullable=False)
    membership_id = Column(Integer, ForeignKey("club_memberships.id", ondelete="CASCADE"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    committee = relationship("Committee", back_populates="member_links")
    membership = relationship("ClubMembership", back_populates="committee_links")


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True)
    posted_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    target_audience = Column(
        SAEnum(AnnouncementAudience), default=AnnouncementAudience.ALL_MEMBERS, nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    club = relationship("Club", back_populates="announcements")
    poster = relationship("User", foreign_keys=[posted_by])
