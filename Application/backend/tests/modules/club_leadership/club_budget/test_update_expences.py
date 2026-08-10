from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_budget  as club_budget_module

def test_update_expense_approval_success(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    budget = BudgetFactory(
        club=club,creator=treasurer
    )
    expense = ExpenseFactory(
        budget=budget,
        submitter=treasurer,
        status=ExpenseStatus.PENDING,
        approval_status=ExpenseApprovalStatus.PENDING,
        approval_date=None,
    )
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.patch(
        f"/api/expenses/{expense.id}",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
            "status": ExpenseStatus.APPROVED.value,
            "approval_remarks": "Expense approved.",
            "approved_by": treasurer.id,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == expense.id
    assert body["approval_status"] == ExpenseApprovalStatus.APPROVED.value
    assert body["status"] == ExpenseStatus.APPROVED.value
    assert body["approval_remarks"] == "Expense approved."
    assert body["approved_by"] == treasurer.id
    assert body["approval_date"] is not None


def test_update_expense_approval_status_only(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    budget = BudgetFactory(club=club,creator=president)
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    expense = ExpenseFactory(
        budget=budget,
        submitter=treasurer,
        approval_status=ExpenseApprovalStatus.PENDING,
    )
    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.patch(
        f"/api/expenses/{expense.id}",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["approval_status"] == ExpenseApprovalStatus.APPROVED.value
    assert body["approval_date"] is not None


def test_update_expense_rejection(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    budget = BudgetFactory(club=club,creator=treasurer)
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    expense = ExpenseFactory(
        budget=budget,
        submitter=member,
        approval_status=ExpenseApprovalStatus.PENDING,
    )
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.patch(
        f"/api/expenses/{expense.id}",
        json={
            "approval_status": ExpenseApprovalStatus.REJECTED.value,
            "approval_remarks": "Insufficient documentation.",
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["approval_status"] == ExpenseApprovalStatus.REJECTED.value
    assert body["approval_remarks"] == "Insufficient documentation."
    assert body["approval_date"] is not None


def test_update_expense_not_found(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.patch(
        "/api/expenses/999999",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Expense not found"


def test_update_expense_forbidden_for_member(
    client,
    auth_headers,mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    budget = BudgetFactory(club=club,creator=treasurer)
    expense = ExpenseFactory(
        budget=budget,
        submitter=member,
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.patch(
        f"/api/expenses/{expense.id}",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_update_expense_unauthorized(
    client,
):
    response = client.patch(
        "/api/expenses/1",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
        },
    )

    assert response.status_code == 401


"""def test_update_expense_invalid_approval_status(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    budget = BudgetFactory(club=club,creator=treasurer)
    member = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    expense = ExpenseFactory(
        budget=budget,
        submitter=member,
    )

    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.patch(
        f"/api/expenses/{expense.id}",
        json={
            "approval_status": "INVALID_STATUS",
        },
        headers=headers,
    )

    assert response.status_code == 400"""

def test_update_expense_database_error(
    client,
    auth_headers,
    db_error,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    db_error(club_budget_module)
    response = client.patch(
        "/api/expenses/1",
        json={
            "approval_status": ExpenseApprovalStatus.APPROVED.value,
        },
        headers=headers,
    )

    assert response.status_code == 500


