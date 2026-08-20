from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.management.club_resources  as club_resource_module

def test_create_main_club_budget_success(
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

    payload = {
        "club_id": club.id,
        "title": "Annual Club Budget",
        "allocated_amount": 50000,
        "period_start": "2026-04-01",
        "period_end": "2027-03-31",
    }
    mock_resolve_club_id(treasurer)
    response = client.post(
        "/api/budgets",
        json=payload,
        headers=headers,
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["club_id"] == club.id
    assert body["committee_id"] is None
    assert body["parent_budget_id"] is None
    assert body["title"] == "Annual Club Budget"
    assert body["allocated_amount"] == 50000.0
    assert body["status"] == BudgetStatus.APPROVED.value
    assert body["created_by"] == treasurer.id



def test_create_main_club_budget_defaults_title(
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
    headers = auth_headers(president.email)
    mock_resolve_club_id(president)
    response = client.post(
        "/api/budgets",
        json={
            "club_id": club.id,
            "allocated_amount": 25000,
            "period_start": "2026-04-01",
            "period_end": "2027-03-31",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["title"] == "Main Club Budget"


def test_create_committee_budget_success(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
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
    parent_budget = BudgetFactory(
        club=club,
        creator=treasurer,
        committee=None,
        parent_budget=None,
        period_start=datetime(2026, 4, 1),
        period_end=datetime(2027, 3, 31),
    )

    headers = auth_headers(treasurer.email)
    mock_resolve_club_id(treasurer)
    response = client.post(
        "/api/budgets",
        json={
            "club_id": club.id,
            "committee_id": committee.id,
            "title": "Events Committee Budget",
            "allocated_amount": 15000,
        },
        headers=headers,
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["club_id"] == club.id
    assert body["committee_id"] == committee.id
    assert body["parent_budget_id"] == parent_budget.id
    assert body["title"] == "Events Committee Budget"
    assert body["allocated_amount"] == 15000.0
    assert body["period_start"] == "2026-04-01"
    assert body["period_end"] == "2027-03-31"
    assert body["status"] == BudgetStatus.APPROVED.value
    assert body["created_by"] == treasurer.id




def test_create_committee_budget_requires_main_budget(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    committee = CommitteeFactory(
        club=club,
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
        "/api/budgets",
        json={
            "club_id": club.id,
            "committee_id": committee.id,
            "title": "Committee Budget",
            "allocated_amount": 10000,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Main club budget not found. Create it first."
    )



def test_create_budget_missing_club_id(
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
        "/api/budgets",
        json={
            "allocated_amount": 10000,
        },
        headers=headers,
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: club_id"


def test_create_budget_missing_allocated_amount(
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
        "/api/budgets",
        json={
            "club_id": club.id,
        },
        headers=headers,
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: allocated_amount"


def test_create_main_budget_missing_period_start(
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
        "/api/budgets",
        json={
            "club_id": club.id,
            "allocated_amount": 10000,
            "period_end": "2027-03-31",
        },
        headers=headers,
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: period_start"


def test_create_main_budget_missing_period_end(
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
        "/api/budgets",
        json={
            "club_id": club.id,
            "allocated_amount": 10000,
            "period_start": "2026-04-01",
        },
        headers=headers,
    )

    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Missing field: period_end"


def test_create_budget_forbidden_for_unauthorized_club_role(
    client,
    auth_headers,
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
    response = client.post(
        "/api/budgets",
        json={
            "club_id": club.id,
            "allocated_amount": 10000,
            "period_start": "2026-04-01",
            "period_end": "2027-03-31",
        },
        headers=headers,
    )
    assert response.status_code == 403


def test_create_budget_unauthorized(
    client,
):
    response = client.post(
        "/api/budgets",
        json={
            "club_id": 1,
            "allocated_amount": 10000,
            "period_start": "2026-04-01",
            "period_end": "2027-03-31",
        },
    )

    assert response.status_code == 401