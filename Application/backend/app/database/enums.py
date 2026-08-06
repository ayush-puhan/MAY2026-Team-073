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
    VOLUNTEER_COORDINATOR = "volunteer_coordinator"
    EVENT_COORDINATOR = "event_coordinator"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    VICE_PRESIDENT = "vice_president"
    PRESIDENT = "president"


class CommitteeRole(str, enum.Enum):
    HEAD = "head"
    CO_HEAD = "co_head"
    MEMBER = "member"


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
    FACULTY_RECOMMENDED = "faculty_recommended"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class EventStatus(str, enum.Enum):
    PENDING_APPROVAL = "pending_approval"
    SCHEDULED = "scheduled"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class RegistrationStatus(str, enum.Enum):
    REGISTERED = "registered"
    WAITLISTED = "waitlisted"
    CANCELLED = "cancelled"


class VolunteerTaskStatus(str, enum.Enum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    PENDING_REVIEW = "pending_review"
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
    MEETING_MINUTES = "meeting_minutes"
    PRESENTATION = "presentation"
    RULEBOOK = "rulebook"
    FILE = "file"
    DRIVE_LINK = "drive_link"
    GUIDELINE = "guideline"


class NotificationType(str, enum.Enum):
    MEMBERSHIP_UPDATE = "membership_update"
    EVENT_REMINDER = "event_reminder"
    BUDGET_APPROVAL = "budget_approval"
    TICKET_UPDATE = "ticket_update"
    PASSWORD_RESET = "password_reset"
    CERTIFICATE_READY = "certificate_ready"
    EMERGENCY_ALERT = "emergency_alert"
    ANNOUNCEMENT = "announcement"
    CLUB_UPDATE = "club_update"
    CLUB_PROPOSAL_SUBMITTED = "club_proposal_submitted"
    CLUB_PROPOSAL_RECOMMENDED = "club_proposal_recommended"
    CLUB_PROPOSAL_REJECTED = "club_proposal_rejected"
    CLUB_PROPOSAL_APPROVED = "club_proposal_approved"
    DEADLINE_WARNING = "deadline_warning"
    EVENT_STARTING = "event_starting"


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    BOTH = "both"


class AnnouncementAudience(str, enum.Enum):
    ALL_MEMBERS = "all_members"
    COMMITTEE = "committee"
    LEADERSHIP = "leadership"
    SYSTEM_WIDE = "system_wide"
    UNIVERSITY_WIDE = "university_wide"


class TicketStatus(str, enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"


class TicketPriority(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class TicketType(str, enum.Enum):
    SUPPORT = "Support"
    BUG = "Bug"
    FEATURE_REQUEST = "Feature Request"
    INQUIRY = "Inquiry"


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


class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class TokenType(str, enum.Enum):
    ACCESS = "access"
    REFRESH = "refresh"
