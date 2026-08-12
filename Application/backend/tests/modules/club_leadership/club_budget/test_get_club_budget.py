from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.club_resources  as club_resource_module

def test_get_budgets_success(
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
    budget1 = BudgetFactory(
        club=club,
        creator=treasurer
    )
    budget2 = BudgetFactory(
        club=club,
        creator=treasurer
    )
    headers = auth_headers(treasurer.email)
    response = client.get(
        f"/api/budgets?club_id={club.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2
    ids = {budget["id"] for budget in body}
    assert ids == {
        str(budget1.id),
        str(budget2.id),
    }


def test_get_budgets_filters_by_club_id(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
    )
    club2 = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    treasurer = UserFactory(
        email="treasurer@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=treasurer,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.TREASURER,
    )
    budget1 = BudgetFactory(
        club=club1,
        creator=treasurer
    )
    budget2 = BudgetFactory(
        club=club2,
        creator=treasurer
    )
    headers = auth_headers(president.email)
    response = client.get(
        f"/api/budgets?club_id={club1.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == str(budget1.id)
    assert body[0]["club_id"] == club1.id
    assert body[0]["id"] != str(budget2.id)


def test_get_budgets_without_club_id_returns_all_budgets(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club1 = ClubFactory(
        university=university,
    )
    club2 = ClubFactory(
        university=university,
    )

    president = UserFactory(
        email="president@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=president,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )
    ClubMembershipFactory(
        user=president,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    budget1 = BudgetFactory(
        club=club1,
        creator=president
    )
    budget2 = BudgetFactory(
        club=club2,
        creator=president
    )

    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.get(
        "/api/budgets",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    ids = {budget["id"] for budget in body}
    assert str(budget1.id) in ids
    assert str(budget2.id) in ids


def test_get_budgets_empty_for_club(
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

    response = client.get(
        f"/api/budgets?club_id={club.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body == []


def test_get_budgets_forbidden_for_regular_member(
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
    headers = auth_headers(member.email)
    response = client.get(
        f"/api/budgets?club_id={club.id}",
        headers=headers,
    )
    assert response.status_code == 403


def test_get_budgets_unauthorized(
    client,
):
    response = client.get(
        "/api/budgets",
    )

    assert response.status_code == 401



def test_get_budgets_invalid_club_id(
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
    response = client.get(
        "/api/budgets?club_id=abc",
        headers=headers,
    )
    # Currently this may result in a 500 because int("abc")
    # raises ValueError.
    assert response.status_code == 500


import pytest
@pytest.mark.parametrize(
    "club_role",
    [
        ClubMemberRole.TREASURER,
        ClubMemberRole.PRESIDENT,
        ClubMemberRole.VICE_PRESIDENT,
    ],
)
def test_get_budgets_allowed_roles(
    client,
    auth_headers,
    club_role,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email=f"{club_role.value}@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=club_role,
    )
    budget = BudgetFactory(
        club=club,
        creator = UserFactory(role=UserRole.FACULTY_ADVISOR)
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/budgets?club_id={club.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == str(budget.id)

