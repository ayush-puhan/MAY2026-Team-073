from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_budget  as club_budget_module


def test_create_expense_success(
    client,
    auth_headers,
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
        club=club,
        creator=treasurer
    )

    headers = auth_headers(treasurer.email)
    payload = {
        "budget_id": budget.id,
        "description": "Purchase of sports equipment",
        "amount": 5000,
        "category": "Equipment",
    }
    response = client.post(
        "/api/expenses",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["budget_id"] == budget.id
    assert body["description"] == "Purchase of sports equipment"
    assert body["amount"] == 5000.0
    assert body["category"] == "Equipment"
    assert body["submitted_by"] == treasurer.id
    assert body["status"] == ExpenseStatus.PENDING.value
    assert body["approval_status"] == ExpenseApprovalStatus.PENDING.value


def test_create_expense_success_as_president(
    client,
    auth_headers,
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
    budget = BudgetFactory(
        club=club,
        creator=president
    )
    headers = auth_headers(president.email)
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": budget.id,
            "description": "Event decorations",
            "amount": 2500,
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["budget_id"] == budget.id
    assert body["description"] == "Event decorations"
    assert body["amount"] == 2500.0
    assert body["submitted_by"] == president.id
    assert body["status"] == ExpenseStatus.PENDING.value
    assert body["approval_status"] == ExpenseApprovalStatus.PENDING.value


def test_create_expense_missing_budget_id(
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
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.post(
        "/api/expenses",
        json={
            "description": "Equipment",
            "amount": 5000,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: budget_id"


def test_create_expense_missing_description(
    client,
    auth_headers,
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
    headers = auth_headers(treasurer.email)
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": budget.id,
            "amount": 5000,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: description"

def test_create_expense_missing_amount(
    client,
    auth_headers,
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
    headers = auth_headers(treasurer.email)
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": budget.id,
            "description": "Equipment",
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: amount"

def test_create_expense_budget_not_found(
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
    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": 999999,
            "description": "Equipment",
            "amount": 5000,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Budget not found"


def test_create_expense_forbidden_for_member(
    client,
    auth_headers,
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
    headers = auth_headers(member.email)
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": budget.id,
            "description": "Equipment",
            "amount": 5000,
        },
        headers=headers,
    )

    assert response.status_code == 403


def test_create_expense_unauthorized(
    client,
):
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": 1,
            "description": "Equipment",
            "amount": 5000,
        },
    )
    assert response.status_code == 401


from unittest.mock import MagicMock

from sqlalchemy.exc import SQLAlchemyError


def test_create_expense_database_error(
    client,
    auth_headers,db_error,mock_resolve_club_id
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
    response = client.post(
        "/api/expenses",
        json={
            "budget_id": 1,
            "description": "Equipment",
            "amount": 5000,
        },
        headers=headers,
    )

    assert response.status_code == 500