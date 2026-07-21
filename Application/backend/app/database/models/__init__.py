"""Importing this package registers every ORM model with SQLAlchemy metadata.

Always import models via this package (not the individual submodules) before
calling Base.metadata.create_all() or configuring mappers, so all tables
and their cross-file relationships resolve correctly.
"""

from .academics import Department, Program, StudentProfile
from .applications import ApplicationInterest, ClubJoinApplication
from .audit import AuditLog
from .auth import AuthSession, User
from .clubs import Announcement, Club, ClubCreationRequest, ClubMembership, Committee, CommitteeMembership
from .communication import Document, Notification
from .events import AttendanceRecord, Event, EventRegistration, ExternalParticipant, VolunteerAssignment
from .external_relations import ClubSponsor, Sponsor
from .finance import Budget, Expense
from .interests import ClubInterest, EventInterest, Interest, UserInterest
from .rewards import (
    RewardPointsLedger, 
    RewardRedemption,
    RewardTask,
    RewardTaskCompletion,
    RewardStoreItem
)
from .support import EmergencyReport, SupportTicket, TicketResponse
from .university import University, UniversityDomain

__all__ = [
    "User",
    "AuthSession",
    "AuditLog",
    "Department",
    "Program",
    "StudentProfile",
    "Interest",
    "UserInterest",
    "ClubInterest",
    "EventInterest",
    "ClubJoinApplication",
    "ApplicationInterest",
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
    "RewardTask",
    "RewardTaskCompletion",
    "RewardStoreItem",
    "Sponsor",
    "ClubSponsor",
    "University",
    "UniversityDomain",
]
