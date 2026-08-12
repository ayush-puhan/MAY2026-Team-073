from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_resources  as club_resource_module

def test_update_budget_allocated_amount_success(
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
        creator=treasurer,
        allocated_amount=50000,
    )

    headers = auth_headers(treasurer.email)
    response = client.patch(
        f"/api/budgets/{budget.id}",
        json={
            "allocated_amount": 75000,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == str(budget.id)
    assert body["club_id"] == club.id
    assert body["allocated_amount"] == 75000.0


def test_update_budget_by_president_success(
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
        creator=treasurer,
        allocated_amount=30000,
    )
    headers = auth_headers(president.email)
    response = client.patch(
        f"/api/budgets/{budget.id}",
        json={
            "allocated_amount": 45000,
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == str(budget.id)
    assert body["allocated_amount"] == 45000.0


def test_update_budget_not_found(
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
    headers = auth_headers(treasurer.email)
    response = client.patch(
        "/api/budgets/999999",
        json={
            "allocated_amount": 50000,
        },
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Budget not found"


def test_update_budget_without_allocated_amount(
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
        creator=treasurer,
        allocated_amount=50000,
    )
    headers = auth_headers(treasurer.email)
    response = client.patch(
        f"/api/budgets/{budget.id}",
        json={},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == str(budget.id)
    assert body["allocated_amount"] == 50000.0

def test_update_budget_forbidden_for_regular_member(
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
        creator=treasurer,
        allocated_amount=50000,
    )
    headers = auth_headers(member.email)
    response = client.patch(
        f"/api/budgets/{budget.id}",
        json={
            "allocated_amount": 75000,
        },
        headers=headers,
    )
    assert response.status_code == 403

def test_update_budget_unauthorized(
    client,
):
    response = client.patch(
        "/api/budgets/1",
        json={
            "allocated_amount": 75000,
        },
    )
    assert response.status_code == 401

def test_update_budget_persists_to_database(
    client,
    auth_headers,
    db_session,
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
        creator=treasurer,
        allocated_amount=50000,
    )
    budget_id = budget.id
    headers = auth_headers(treasurer.email)
    response = client.patch(
        f"/api/budgets/{budget_id}",
        json={
            "allocated_amount": 75000,
        },
        headers=headers,
    )
    assert response.status_code == 200
    db_session.expire_all()
    updated_budget = (
        db_session.query(Budget)
        .filter(Budget.id == budget_id)
        .first()
    )
    assert updated_budget is not None
    assert float(updated_budget.allocated_amount) == 75000.0