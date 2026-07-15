"""Insert/select/update/delete across all major ClubConnect workflows."""

from datetime import datetime, timedelta

from database.enums import (
    BudgetStatus,
    ClubMemberRole,
    DocumentType,
    EmergencyCategory,
    EventStatus,
    ExpenseApprovalStatus,
    ExternalParticipantType,
    MembershipStatus,
    NotificationType,
    RedemptionStatus,
    UserRole,
)
from database.models.auth import AuthSession, User
from database.models.clubs import Announcement, Club, ClubMembership, Committee, CommitteeMembership
from database.models.communication import Document, Notification
from database.models.events import (
    AttendanceRecord,
    Event,
    EventRegistration,
    ExternalParticipant,
    VolunteerAssignment,
)
from database.models.external_relations import ClubSponsor, Sponsor
from database.models.finance import Budget, Expense
from database.models.rewards import RewardPointsLedger, RewardRedemption
from database.models.support import EmergencyReport, SupportTicket, TicketResponse


def _make_user(session, email="user@example.com", role=UserRole.STUDENT):
    user = User(email=email, password_hash="hash", full_name="Test User", role=role)
    session.add(user)
    session.commit()
    return user


def _make_club(session, advisor, university):
    club = Club(name="Chess Club", slug="chess-club", faculty_advisor_id=advisor.id,
                university_id=university.id)
    session.add(club)
    session.commit()
    return club


def test_user_crud(session):
    user = _make_user(session)
    assert user.id is not None

    fetched = session.get(User, user.id)
    assert fetched.email == "user@example.com"

    fetched.full_name = "Updated Name"
    session.commit()
    assert session.get(User, user.id).full_name == "Updated Name"

    session.delete(fetched)
    session.commit()
    assert session.get(User, user.id) is None


def test_auth_session_crud(session):
    user = _make_user(session)
    auth = AuthSession(user_id=user.id, token="abc.def.ghi", expires_at=datetime.utcnow() + timedelta(days=1))
    session.add(auth)
    session.commit()
    assert session.get(AuthSession, auth.id).user.email == user.email


def test_club_and_membership_lifecycle(session, sample_university):
    advisor = _make_user(session, email="advisor@example.com", role=UserRole.FACULTY_ADVISOR)
    club = _make_club(session, advisor, sample_university)
    student = _make_user(session, email="student@example.com")

    membership = ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.PENDING)
    session.add(membership)
    session.commit()
    assert membership.status == MembershipStatus.PENDING

    membership.status = MembershipStatus.APPROVED
    membership.role_in_club = ClubMemberRole.MEMBER
    session.commit()
    assert session.get(ClubMembership, membership.id).status == MembershipStatus.APPROVED


def test_committee_and_committee_membership(session, sample_university):
    advisor = _make_user(session, email="advisor2@example.com")
    club = _make_club(session, advisor, sample_university)
    student = _make_user(session, email="student2@example.com")
    membership = ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED)
    session.add(membership)
    session.commit()

    committee = Committee(club_id=club.id, name="Events Committee")
    session.add(committee)
    session.commit()

    link = CommitteeMembership(committee_id=committee.id, membership_id=membership.id)
    session.add(link)
    session.commit()
    assert link.committee.name == "Events Committee"


def test_announcement_crud(session, sample_university):
    advisor = _make_user(session, email="advisor3@example.com")
    club = _make_club(session, advisor, sample_university)
    announcement = Announcement(club_id=club.id, posted_by=advisor.id, title="Welcome", body="Hello all")
    session.add(announcement)
    session.commit()
    assert session.get(Announcement, announcement.id).title == "Welcome"


def test_event_registration_and_attendance(session, sample_university):
    advisor = _make_user(session, email="advisor4@example.com")
    club = _make_club(session, advisor, sample_university)
    student = _make_user(session, email="student4@example.com")

    event = Event(
        club_id=club.id,
        title="Hack Night",
        start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=2),
        created_by=advisor.id,
        status=EventStatus.SCHEDULED,
    )
    session.add(event)
    session.commit()

    registration = EventRegistration(event_id=event.id, user_id=student.id)
    session.add(registration)
    session.commit()

    # Registered but did not attend
    assert session.query(AttendanceRecord).filter_by(event_id=event.id, user_id=student.id).first() is None

    attendance = AttendanceRecord(event_id=event.id, user_id=student.id)
    session.add(attendance)
    session.commit()
    assert session.get(AttendanceRecord, attendance.id).user.email == student.email


def test_volunteer_and_external_participant(session, sample_university):
    advisor = _make_user(session, email="advisor5@example.com")
    club = _make_club(session, advisor, sample_university)
    student = _make_user(session, email="student5@example.com")
    membership = ClubMembership(user_id=student.id, club_id=club.id, status=MembershipStatus.APPROVED)
    session.add(membership)
    session.commit()

    event = Event(
        club_id=club.id,
        title="Guest Talk",
        start_at=datetime.utcnow(),
        end_at=datetime.utcnow() + timedelta(hours=1),
        created_by=advisor.id,
    )
    session.add(event)
    session.commit()

    volunteer = VolunteerAssignment(
        event_id=event.id,
        assignee_membership_id=membership.id,
        assigned_by=advisor.id,
        task_description="Registration desk",
    )
    session.add(volunteer)

    external = ExternalParticipant(
        event_id=event.id,
        full_name="Guest Speaker",
        participant_type=ExternalParticipantType.GUEST_SPEAKER,
    )
    session.add(external)
    session.commit()

    assert volunteer.event.title == "Guest Talk"
    assert external.event.title == "Guest Talk"


def test_budget_and_expense_approval(session, sample_university):
    advisor = _make_user(session, email="advisor6@example.com")
    club = _make_club(session, advisor, sample_university)

    budget = Budget(
        club_id=club.id,
        title="Annual Budget",
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow() + timedelta(days=30),
        allocated_amount=1000,
        status=BudgetStatus.APPROVED,
        created_by=advisor.id,
    )
    session.add(budget)
    session.commit()

    expense = Expense(
        budget_id=budget.id,
        description="Snacks",
        amount=50.25,
        submitted_by=advisor.id,
        approval_status=ExpenseApprovalStatus.PENDING,
    )
    session.add(expense)
    session.commit()

    expense.approval_status = ExpenseApprovalStatus.APPROVED
    expense.approved_by = advisor.id
    expense.approval_date = datetime.utcnow()
    session.commit()
    assert session.get(Expense, expense.id).approval_status == ExpenseApprovalStatus.APPROVED


def test_document_and_notification(session):
    user = _make_user(session, email="docs@example.com")
    document = Document(owner_id=user.id, doc_type=DocumentType.CERTIFICATE, file_url="https://x/y.pdf", title="Cert")
    session.add(document)

    notification = Notification(
        user_id=user.id, type=NotificationType.EVENT_REMINDER, title="Reminder", body="Event tomorrow"
    )
    session.add(notification)
    session.commit()

    assert document.owner.email == user.email
    assert notification.is_read is False
    notification.is_read = True
    session.commit()
    assert session.get(Notification, notification.id).is_read is True


def test_support_ticket_and_response(session):
    student = _make_user(session, email="ticket@example.com")
    agent = _make_user(session, email="agent@example.com", role=UserRole.STUDENT_AFFAIRS_OFFICE)

    ticket = SupportTicket(
        raised_by=student.id, 
        title="Login issue", 
        description="Can't log in",
        status="Open",
        priority="Medium",
        ticket_type="Support"
    )
    session.add(ticket)
    session.commit()

    response = TicketResponse(ticket_id=ticket.id, responder_id=agent.id, body="Please reset password")
    session.add(response)
    session.commit()

    assert ticket.responses[0].body == "Please reset password"


def test_emergency_report(session):
    student = _make_user(session, email="emergency@example.com")
    report = EmergencyReport(
        reported_by=student.id, category=EmergencyCategory.MEDICAL, description="Needs assistance"
    )
    session.add(report)
    session.commit()
    assert session.get(EmergencyReport, report.id).status.value == "reported"


def test_reward_points_and_redemption(session):
    student = _make_user(session, email="rewards@example.com")
    ledger_entry = RewardPointsLedger(user_id=student.id, points=100, reason="Volunteering")
    session.add(ledger_entry)
    session.commit()

    redemption = RewardRedemption(
        user_id=student.id, points_spent=50, reward_description="Cafeteria Voucher",
        status=RedemptionStatus.REQUESTED,
    )
    session.add(redemption)
    session.commit()
    assert session.get(RewardRedemption, redemption.id).points_spent == 50


def test_sponsor_and_club_sponsor(session, sample_university):
    advisor = _make_user(session, email="advisor7@example.com")
    club = _make_club(session, advisor, sample_university)
    sponsor = Sponsor(organization_name="Acme Corp")
    session.add(sponsor)
    session.commit()

    link = ClubSponsor(club_id=club.id, sponsor_id=sponsor.id, sponsorship_details="Cash sponsorship")
    session.add(link)
    session.commit()
    assert sponsor.club_links[0].club.name == "Chess Club"
