from .base import factory, BaseFactory
from factory import fuzzy

import bcrypt
from datetime import datetime, timedelta

from app.database.models import (
    User,Club,University,Event,SupportTicket ,AuditLog,Department,Budget,Expense,ClubMembership,
    Committee, ClubCreationRequest,Announcement,ClubJoinApplication,Document
)

from app.database.enums import (
    UserRole,AuthProvider,ClubStatus,EventStatus,TicketType,
    TicketPriority,ClubMemberRole,ClubRequestStatus,
    TicketStatus, MembershipStatus,AnnouncementAudience,
    BudgetStatus,ExpenseStatus,ExpenseApprovalStatus,DocumentType
)

class UserFactory(BaseFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    full_name = factory.Faker("name")
    password_hash = bcrypt.hashpw(b"Password@123",bcrypt.gensalt()).decode("utf-8")
    role = UserRole.STUDENT
    is_active = True
    email_verified = True
    auth_provider = AuthProvider.LOCAL
    phone = None
    roll_number = factory.Sequence(lambda n: f"2025CS{n:03d}")
    profile_photo_url = None
    accessibility_prefs = None
    google_id = None
    dob = None
    gender = None
    color_blind_mode = False
    department = None
    university = None

class UniversityFactory(BaseFactory):
    class Meta:
        model = University

    name = factory.Sequence(lambda n: f"University {n}")
    short_name = factory.Sequence(lambda n: f"UNI{n}")
    domain = factory.Sequence(lambda n: f"university{n}.edu")
    address = factory.Faker("address")
    website = factory.LazyAttribute(
        lambda obj: f"https://www.{obj.domain}"
    )
    logo_url = None
    banner = None
    is_active = True

class DepartmentFactory(BaseFactory):
    class Meta:
        model = Department
    name = factory.Sequence(lambda n: f"Department {n}")
    code = factory.Sequence(lambda n: f"DEPT{n:03d}")
    university = None

class ClubFactory(BaseFactory):
    class Meta:
        model = Club

    name = factory.Sequence(lambda n: f"Club {n}")
    slug = factory.Sequence(lambda n: f"club-{n}")
    category = "Technical"
    description = factory.Faker("paragraph")
    objectives = factory.Faker("paragraph")
    logo_url = None
    banner = None
    status = ClubStatus.ACTIVE
    member_count_cache = 0
    university = None
    faculty_advisor = None


class EventFactory(BaseFactory):
    class Meta:
        model = Event

    club = None
    creator = None
    title = factory.Sequence(lambda n: f"Event {n}")
    description = factory.Faker("paragraph")
    venue = factory.Faker("city")
    start_at = datetime.utcnow()
    end_at = datetime.utcnow() + timedelta(days=1)
    registration_deadline = datetime.utcnow() - timedelta(days=2)
    capacity = 100
    status = EventStatus.SCHEDULED
    banner = None
    requires_external_participants = False
    is_public = False


class SupportTicketFactory(BaseFactory):
    class Meta:
        model = SupportTicket
    raised_by_user = None
    university = None
    title = factory.Sequence(lambda n: f"Support Ticket {n}")
    description = factory.Faker("paragraph")
    ticket_type = TicketType.SUPPORT
    priority = TicketPriority.MEDIUM
    status = TicketStatus.OPEN
    assigned_agent = None
    is_offensive = False
    resolution_rating = None


class AuditLogFactory(BaseFactory):
    class Meta:
        model = AuditLog
    # Relationships (these automatically populate user_id and university_id)
    user = None
    university_id = None
    # Required field
    action = 'LOGIN'
    # Optional/Nullable fields
    entity_type = None
    entity_id = None
    details = None


class BudgetFactory(BaseFactory):
    class Meta:
        model = Budget
    club = None
    committee = None
    parent_budget = None
    title = factory.Sequence(lambda n: f"Budget {n}")
    period_start = factory.LazyFunction(datetime.utcnow)
    period_end = factory.LazyAttribute(
        lambda obj: obj.period_start + timedelta(days=30)
    )
    allocated_amount = 10000.00
    status = BudgetStatus.DRAFT
    creator = None
    created_at = factory.LazyFunction(datetime.utcnow)


class ExpenseFactory(BaseFactory):
    class Meta:
        model = Expense
    budget = None
    description = factory.Faker("sentence")
    amount = 500.00
    category = "General"
    receipt_document = None
    submitter = None #
    status = ExpenseStatus.PENDING
    approval_status = ExpenseApprovalStatus.PENDING
    approver = None
    approval_date = None
    approval_remarks = None
    created_at = factory.LazyFunction(datetime.utcnow)



class ClubMembershipFactory(BaseFactory):
    class Meta:
        model = ClubMembership
    user = None #factory.SubFactory(UserFactory)
    club = None #factory.SubFactory(ClubFactory)
    role_in_club = ClubMemberRole.MEMBER
    status = MembershipStatus.PENDING
    applied_at = factory.LazyFunction(datetime.utcnow)
    decided_at = None
    approver = None
    rejection_reason = None


class CommitteeFactory(BaseFactory):
    class Meta:
        model = Committee
    club = None#factory.SubFactory(ClubFactory)

    name = factory.Sequence(lambda n: f"Committee {n}")
    description = factory.Faker("sentence")

    created_at = factory.LazyFunction(datetime.utcnow)


class ClubCreationRequestFactory(BaseFactory):
    class Meta:
        model = ClubCreationRequest
    proposed_name = factory.Sequence(lambda n: f"Proposed Club {n}")
    proposed_category = "Technical"
    proposal_description = factory.Faker("paragraph")
    requester = None #factory.SubFactory(UserFactory)

    status = ClubRequestStatus.SUBMITTED

    reviewer = None
    faculty_advisor = None
    review_comments = None
    resulting_club = None

    created_at = factory.LazyFunction(datetime.utcnow)
    decided_at = None


class AnnouncementFactory(BaseFactory):
    class Meta:
        model = Announcement
    club = None #factory.SubFactory(ClubFactory)
    poster = None #factory.SubFactory(UserFactory)
    title = factory.Sequence(lambda n: f"Announcement {n}")
    body = factory.Faker("paragraph")
    target_audience = AnnouncementAudience.ALL_MEMBERS
    created_at = factory.LazyFunction(datetime.utcnow)


class ClubJoinApplicationFactory(BaseFactory):
    class Meta:
        model = ClubJoinApplication

    user = None #factory.SubFactory(UserFactory)
    club = None #factory.SubFactory(ClubFactory)

    motivation = factory.Faker("paragraph")
    contribution = factory.Faker("sentence")
    previous_experience = factory.Faker("paragraph")
    skills = factory.Faker("sentence")
    portfolio_url = factory.Faker("url")
    resume_document = None
    weekly_availability = "10 hours/week"

    status = MembershipStatus.PENDING

    reviewer = None
    review_comments = None

    applied_at = factory.LazyFunction(datetime.utcnow)
    reviewed_at = None


class DocumentFactory(BaseFactory):
    class Meta:
        model = Document

    owner = None #factory.SubFactory(UserFactory)

    club = None
    event = None
    committee = None

    doc_type = DocumentType.GENERAL

    file_url = factory.Faker("url")
    title = factory.Sequence(lambda n: f"Document {n}")

    created_at = factory.LazyFunction(datetime.utcnow)