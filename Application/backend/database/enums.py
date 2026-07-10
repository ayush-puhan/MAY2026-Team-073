"""All ClubConnect enum classes, mapped via SQLAlchemy Enum (TEXT + CHECK in SQLite)."""

import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    FACULTY_ADVISOR = "faculty_advisor"
    STUDENT_AFFAIRS_OFFICE = "student_affairs_office"
    DEAN_STUDENT_WELFARE = "dean_student_welfare"
    SYSTEM_ADMIN = "system_admin"


class ClubMemberRole(str, enum.Enum):
    APPLICANT = "applicant"
    MEMBER = "member"
    COMMITTEE_MEMBER = "committee_member"
    VOLUNTEER_COORDINATOR = "volunteer_coordinator"
    EVENT_COORDINATOR = "event_coordinator"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    VICE_PRESIDENT = "vice_president"
    PRESIDENT = "president"


class MembershipStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class ClubStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class ClubRequestStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class EventStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RegistrationStatus(str, enum.Enum):
    REGISTERED = "registered"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class VolunteerTaskStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


class ExternalParticipantType(str, enum.Enum):
    OTHER_UNIVERSITY_STUDENT = "other_university_student"
    GUEST_SPEAKER = "guest_speaker"
    COMPETITION_PARTICIPANT = "competition_participant"


class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"


class ExpenseStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REIMBURSED = "reimbursed"


class ExpenseApprovalStatus(str, enum.Enum):
    """Single, non-polymorphic approval lifecycle embedded directly on Expense."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DocumentType(str, enum.Enum):
    CERTIFICATE = "certificate"
    RECEIPT = "receipt"
    REPORT = "report"
    GENERAL = "general"


class NotificationType(str, enum.Enum):
    MEMBERSHIP_UPDATE = "membership_update"
    EVENT_REMINDER = "event_reminder"
    BUDGET_APPROVAL = "budget_approval"
    TICKET_UPDATE = "ticket_update"
    PASSWORD_RESET = "password_reset"
    CERTIFICATE_READY = "certificate_ready"
    EMERGENCY_ALERT = "emergency_alert"
    ANNOUNCEMENT = "announcement"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    BOTH = "both"


class AnnouncementAudience(str, enum.Enum):
    ALL_MEMBERS = "all_members"
    COMMITTEE = "committee"
    LEADERSHIP = "leadership"
    ALL_STUDENTS = "all_students"


class EmergencyCategory(str, enum.Enum):
    HARASSMENT = "harassment"
    MEDICAL = "medical"
    WHEELCHAIR_ASSISTANCE = "wheelchair_assistance"
    OTHER_EMERGENCY = "other_emergency"


class EmergencyStatus(str, enum.Enum):
    REPORTED = "reported"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class RedemptionStatus(str, enum.Enum):
    REQUESTED = "requested"
    APPROVED = "approved"
    FULFILLED = "fulfilled"
    REJECTED = "rejected"
