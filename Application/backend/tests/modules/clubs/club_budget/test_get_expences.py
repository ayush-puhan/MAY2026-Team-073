from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_budget  as club_budget_module

def test_get_expenses_success(
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
    budget = BudgetFactory(
        club=club,
        creator=treasurer
    )

    expense1 = ExpenseFactory(
        budget=budget,
        submitter=member,
    )

    expense2 = ExpenseFactory(
        budget=budget,
        submitter=member,
    )

    headers = auth_headers(member.email)
    response = client.get(
        f"/api/expenses?budget_id={budget.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    ids = {expense["id"] for expense in body}
    assert ids == {
        expense1.id,
        expense2.id,
    }


def test_get_expenses_filters_by_budget_id(
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
    budget1 = BudgetFactory(
        club=club,
        creator=treasurer
    )
    budget2 = BudgetFactory(
        club=club,
        creator=treasurer
    )
    expense1 = ExpenseFactory(
        budget=budget1,
        submitter=member,
    )
    expense2 = ExpenseFactory(
        budget=budget2,
        submitter=member,
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/expenses?budget_id={budget1.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == expense1.id
    assert body[0]["id"] != expense2.id

def test_get_expenses_without_budget_id_returns_all(
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

    budget1 = BudgetFactory(club=club,creator=treasurer)
    budget2 = BudgetFactory(club=club,creator=treasurer)
    expense1 = ExpenseFactory(
        budget=budget1,
        submitter=member,
    )
    expense2 = ExpenseFactory(
        budget=budget2,
        submitter=member,
    )
    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.get(
        "/api/expenses",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    ids = {expense["id"] for expense in body}
    assert expense1.id in ids
    assert expense2.id in ids

def test_get_expenses_empty(
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
    budget = BudgetFactory(
        club=club,
        creator=treasurer
    )
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/expenses?budget_id={budget.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body == []

def test_get_expenses_forbidden_for_unauthorized_role(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    secretary = UserFactory(
        email="secretary@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=secretary,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.SECRETARY,
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
    headers = auth_headers(secretary.email)
    response = client.get(
        f"/api/expenses?budget_id={budget.id}",
        headers=headers,
    )
    assert response.status_code == 403


def test_get_expenses_unauthorized(
    client,
):
    response = client.get(
        "/api/expenses",
    )

    assert response.status_code == 401

def test_event_decision_database_error(
    client,
    auth_headers,
    db_error,
    mock_resolve_club_id
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

    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    db_error(club_budget_module)
    response = client.get(
        "/api/expenses",
        headers=headers
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]