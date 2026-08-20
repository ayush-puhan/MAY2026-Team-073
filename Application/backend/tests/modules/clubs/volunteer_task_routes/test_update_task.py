from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.clubs.members.transfer_presidency  as tp_module


def test_update_task_status_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator
    )
    headers = auth_headers(user.email)
    response = client.patch(
        f"/api/volunteer-tasks/{task.id}/status",
        headers=headers,
        json={
            "status": "completed",
        },
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["id"] == task.id
    assert body["status"] == "completed"


def test_update_task_status_missing_status(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator
    )
    headers = auth_headers(user.email)
    response = client.patch(
        f"/api/volunteer-tasks/{task.id}/status",
        headers=headers,
        json={},
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "status required"


def test_update_task_status_task_not_found(
    client,
    auth_headers,
    mock_resolve_club_id
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.patch(
        "/api/volunteer-tasks/999999/status",
        headers=headers,
        json={
            "status": "completed",
        },
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Task not found"




def test_update_task_status_other_users_task(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    task_owner = UserFactory(
        email="owner@campus.edu",
        university=university,
    )
    current_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    owner_membership = ClubMembershipFactory(
        user=task_owner,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=owner_membership,
        assigner=event.creator
    )
    headers = auth_headers(current_user.email)
    response = client.patch(
        f"/api/volunteer-tasks/{task.id}/status",
        headers=headers,
        json={
            "status": "completed",
        },
    )
    assert response.status_code == 403
    body = response.get_json()
    assert body["message"] == (
        "You can update only your task"
    )


def test_update_task_status_invalid_status(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    task_owner = UserFactory(
        email="owner@campus.edu",
        university=university,
    )
    current_user = UserFactory(
        email="member@campus.edu",
        university=university,
    )
    owner_membership = ClubMembershipFactory(
        user=task_owner,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    ClubMembershipFactory(
        user=current_user,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=owner_membership,
        assigner=event.creator
    )
    headers = auth_headers(task_owner.email)
    response = client.patch(
        f"/api/volunteer-tasks/{task.id}/status",
        headers=headers,
        json={
            "status": "invalid_status",
        },
    )
    assert response.status_code == 400
    body = response.get_json()
    assert body["message"] == "Invalid status"
