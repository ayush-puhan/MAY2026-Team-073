"""Club management module: clubs, creation requests, memberships,
committees, committee memberships, and announcements."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from ..enums import (
    AnnouncementAudience,
    ClubMemberRole,
    ClubRequestStatus,
    ClubStatus,
    MembershipStatus,
)
from ..mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    from .__init__ import *


class Club(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    objectives: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ClubStatus] = mapped_column(SAEnum(ClubStatus), default=ClubStatus.ACTIVE, nullable=False)
    faculty_advisor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    member_count_cache: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    faculty_advisor: Mapped[Optional[User]] = relationship(back_populates="advised_clubs")
    memberships: Mapped[List[ClubMembership]] = relationship(back_populates="club", cascade="all, delete-orphan")
    events: Mapped[List[Event]] = relationship(back_populates="club", cascade="all, delete-orphan")
    committees: Mapped[List[Committee]] = relationship(back_populates="club", cascade="all, delete-orphan")
    budgets: Mapped[List[Budget]] = relationship(back_populates="club", cascade="all, delete-orphan")
    announcements: Mapped[List[Announcement]] = relationship(back_populates="club", cascade="all, delete-orphan")
    sponsor_links: Mapped[List[ClubSponsor]] = relationship(back_populates="club", cascade="all, delete-orphan")


class ClubCreationRequest(Base):
    """Student-submitted new-club proposal."""

    __tablename__ = "club_creation_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proposed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    proposed_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    proposal_description: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[ClubRequestStatus] = mapped_column(
        SAEnum(ClubRequestStatus), default=ClubRequestStatus.SUBMITTED, nullable=False
    )
    reviewed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    review_comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    resulting_club_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clubs.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    decided_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    requester: Mapped["User"] = relationship(foreign_keys=[requested_by])
    reviewer: Mapped[Optional["User"]] = relationship(foreign_keys=[reviewed_by])
    resulting_club: Mapped[Optional["Club"]] = relationship(foreign_keys=[resulting_club_id])


class ClubMembership(Base):
    """Single source of truth for the membership workflow: Pending -> Approved/Rejected,
    or Withdrawn. Also carries the per-club role (Assumption: club-scoped roles live
    here, not on the global User.role)."""

    __tablename__ = "club_memberships"
    __table_args__ = (UniqueConstraint("user_id", "club_id", name="uq_user_club"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    role_in_club: Mapped[ClubMemberRole] = mapped_column(
        SAEnum(ClubMemberRole), default=ClubMemberRole.MEMBER, nullable=False
    )
    status: Mapped[MembershipStatus] = mapped_column(
        SAEnum(MembershipStatus), default=MembershipStatus.PENDING, nullable=False
    )
    applied_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    decided_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    approved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="club_memberships", foreign_keys=[user_id])
    club: Mapped["Club"] = relationship(back_populates="memberships")
    approver: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by])
    committee_links: Mapped[List["CommitteeMembership"]] = relationship(
        back_populates="membership", cascade="all, delete-orphan"
    )
    volunteer_assignments: Mapped[List["VolunteerAssignment"]] = relationship(
        back_populates="assignee_membership", cascade="all, delete-orphan"
    )


class Committee(Base):
    __tablename__ = "committees"
    __table_args__ = (UniqueConstraint("club_id", "name", name="uq_committee_name_per_club"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    club: Mapped["Club"] = relationship(back_populates="committees")
    member_links: Mapped[List["CommitteeMembership"]] = relationship(
        back_populates="committee", cascade="all, delete-orphan"
    )


class CommitteeMembership(Base):
    """M:N bridge Committee<->ClubMembership (association table)."""

    __tablename__ = "committee_memberships"
    __table_args__ = (UniqueConstraint("committee_id", "membership_id", name="uq_committee_membership"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    committee_id: Mapped[int] = mapped_column(ForeignKey("committees.id", ondelete="CASCADE"), nullable=False)
    membership_id: Mapped[int] = mapped_column(ForeignKey("club_memberships.id", ondelete="CASCADE"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    committee: Mapped["Committee"] = relationship(back_populates="member_links")
    membership: Mapped["ClubMembership"] = relationship(back_populates="committee_links")


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    club_id: Mapped[Optional[int]] = mapped_column(ForeignKey("clubs.id", ondelete="CASCADE"), nullable=True)
    posted_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[AnnouncementAudience] = mapped_column(
        SAEnum(AnnouncementAudience), default=AnnouncementAudience.ALL_MEMBERS, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    club: Mapped[Optional["Club"]] = relationship(back_populates="announcements")
    poster: Mapped["User"] = relationship(foreign_keys=[posted_by])
