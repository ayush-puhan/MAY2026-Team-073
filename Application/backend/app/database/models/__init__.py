"""Importing this package registers every ORM model with SQLAlchemy metadata.

Always import models via this package (not the individual submodules) before
calling Base.metadata.create_all() or configuring mappers, so all 24 tables
and their cross-file relationships resolve correctly.
"""

from .auth import AuthSession, User
from .clubs import Announcement, Club, ClubCreationRequest, ClubMembership, Committee, CommitteeMembership
from .communication import Document, Notification
from .events import AttendanceRecord, Event, EventRegistration, ExternalParticipant, VolunteerAssignment
from .external_relations import ClubSponsor, Sponsor
from .finance import Budget, Expense
from .rewards import RewardPointsLedger, RewardRedemption
from .support import EmergencyReport, SupportTicket, TicketResponse

__all__ = [
    "User",
    "AuthSession",
    "Club",
    "ClubCreationRequest",
    "ClubMembership",
    "Committee",
    "CommitteeMembership",
    "Announcement",
    "Event",
    "EventRegistration",
    "AttendanceRecord",
    "VolunteerAssignment",
    "ExternalParticipant",
    "Budget",
    "Expense",
    "Notification",
    "Document",
    "SupportTicket",
    "TicketResponse",
    "EmergencyReport",
    "RewardPointsLedger",
    "RewardRedemption",
    "Sponsor",
    "ClubSponsor",
]
