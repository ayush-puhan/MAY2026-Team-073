# tests/modules/faculty_advisor/test_get_stats.py

from app.database.models import (
    Club,
    Event,
    Budget,
    Expense,
)
from app.database.enums import (
    UserRole,
    EventStatus,
    ExpenseStatus,
    BudgetStatus,
    ExpenseApprovalStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory,
    BudgetFactory,ExpenseFactory
)

# -------------------------------------------------------------------
# Test: Successfully retrieve advisor statistics of only 
# his/her advised clubs
# -------------------------------------------------------------------
def test_get_faculty_stats_success(
    client,
    auth_headers,
    faculty_advisor_user
):
    university = UniversityFactory()
    other_faculty = UserFactory(role=UserRole.FACULTY_ADVISOR)
    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
        member_count_cache=50,
    )
    club2 = ClubFactory(
        university=university,
        faculty_advisor=other_faculty,
        member_count_cache=50,
    )

    budget = BudgetFactory(
        club=club,
        creator=faculty_advisor_user
    )
    budget2 = BudgetFactory(
        club=club2,
        creator=other_faculty
    )

    EventFactory(
        club=club,
        creator=faculty_advisor_user,
        status=EventStatus.PENDING_APPROVAL,
    )
    EventFactory(
        club=club2,
        creator=other_faculty,
        status=EventStatus.PENDING_APPROVAL,
    )

    ExpenseFactory(
        budget=budget,
        status=ExpenseStatus.PENDING,
        submitter=UserFactory()
    )
    ExpenseFactory(
        budget=budget2,
        status=ExpenseStatus.PENDING,
        submitter=UserFactory()
    )

    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/stats",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()

    assert body["advisedClubs"] == 1
    assert body["pendingEvents"] == 1
    assert body["totalMembers"] == 50
    assert body["pendingExpenses"] == 1


# -------------------------------------------------------------------
# Test: Advisor has no clubs
# -------------------------------------------------------------------
def test_get_faculty_stats_empty(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)
    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/stats",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["advisedClubs"] == 0
    assert body["pendingEvents"] == 0
    assert body["pendingExpenses"] == 0


# -------------------------------------------------------------------
# Test: Advisor requests another advisor's statistics
# -------------------------------------------------------------------
def test_get_faculty_stats_forbidden(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)
    another_advisor = UserFactory(role=faculty_advisor_user.role)
    response = client.get(
        f"/api/faculty/{another_advisor.id}/stats",
        headers=headers,
    )
    assert response.status_code == 404
    assert "Forbidden" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_faculty_stats_unauthorized(client):

    response = client.get(
        "/api/faculty/1/stats",
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Forbidden (student token)
# -------------------------------------------------------------------
def test_get_faculty_stats_wrong_role(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)
    response = client.get(
        f"/api/faculty/{student_user.id}/stats",
        headers=headers,
    )
    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_faculty_stats_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    monkeypatch,
):
    headers = auth_headers(faculty_advisor_user.email)
    def broken_session():
        raise Exception("Database Error")
        

    monkeypatch.setattr(
        "app.modules.faculty.routes.get_session",
        broken_session,
    )

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/stats",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]