from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.transfer_presidency  as tp_module


def test_create_volunteer_task_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    coordinator = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    assignee = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=coordinator,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.EVENT_COORDINATOR,
    )
    assignee_membership = ClubMembershipFactory(
        user=assignee,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club,
        creator=coordinator
    )
    headers = auth_headers(coordinator.email)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={
            "event_id": event.id,
            "assignee_membership_id": assignee_membership.id,
            "task_description": "Arrange chairs for the event",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["event_id"] == event.id
    assert (
        body["assignee_membership_id"]
        == assignee_membership.id
    )
    assert (
        body["task_description"]
        == "Arrange chairs for the event"
    )



def test_create_volunteer_task_missing_body(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    user = UserFactory(
        email="coordinator@campus.edu",
    )
    club = ClubFactory(
        university=university,
    )
    ClubMembershipFactory(
            user=user,
            club=club,
            status=MembershipStatus.APPROVED,
            role_in_club=ClubMemberRole.EVENT_COORDINATOR,
        )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={}
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Request body is required"


def test_create_volunteer_task_missing_event_id(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    coordinator = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    assignee = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=coordinator,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.EVENT_COORDINATOR,
    )
    membership = ClubMembershipFactory(
        user=assignee,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(coordinator.email)
    mock_resolve_club_id(coordinator)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={
            "assignee_membership_id": membership.id,
            "task_description": "Arrange chairs",
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "event_id is required"



def test_create_volunteer_task_event_not_found(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    coordinator = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    assignee = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=coordinator,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.EVENT_COORDINATOR,
    )
    membership = ClubMembershipFactory(
        user=assignee,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(coordinator.email)
    mock_resolve_club_id(coordinator)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={
            "event_id": 999999,
            "assignee_membership_id": membership.id,
            "task_description": "Arrange chairs",
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Event not found"



def test_create_volunteer_task_membership_not_found(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    coordinator = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=coordinator,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.EVENT_COORDINATOR,
    )
    event = EventFactory(
        club=club,
        creator=coordinator
    )
    headers = auth_headers(coordinator.email)
    mock_resolve_club_id(coordinator)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={
            "event_id": event.id,
            "assignee_membership_id": 999999,
            "task_description": "Arrange chairs",
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Membership ID does not exist"




def test_create_volunteer_task_wrong_club(
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
    coordinator = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    assignee = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=coordinator,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.EVENT_COORDINATOR,
    )
    membership = ClubMembershipFactory(
        user=assignee,
        club=club2,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club1,
        creator=coordinator
    )
    headers = auth_headers(coordinator.email)
    response = client.post(
        "/api/volunteer-tasks",
        headers=headers,
        json={
            "event_id": event.id,
            "assignee_membership_id": membership.id,
            "task_description": "Arrange chairs",
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == (
        "Assignee does not belong to event club"
    )




def test_create_volunteer_task_unauthenticated(
    client,
):
    response = client.post(
        "/api/volunteer-tasks",
        json={
            "event_id": 1,
            "assignee_membership_id": 1,
            "task_description": "Arrange chairs",
        },
    )
    assert response.status_code == 401

















