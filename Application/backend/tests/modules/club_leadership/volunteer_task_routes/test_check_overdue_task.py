from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.transfer_presidency  as tp_module


def test_check_overdue_tasks_updates_overdue_task(
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
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() - timedelta(hours=1),
        status=VolunteerTaskStatus.ASSIGNED,
    )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.post(
        "/api/volunteer-tasks/check-overdue",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["updated"] == 1
    # Verify the task was changed to MISSED
    assert task.status == VolunteerTaskStatus.MISSED


def test_check_overdue_tasks_does_not_update_completed_task(
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
    event = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() - timedelta(hours=1),
        status=VolunteerTaskStatus.COMPLETED,
    )

    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.post(
        "/api/volunteer-tasks/check-overdue",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["updated"] == 0
    # Completed task must remain completed
    assert task.status == VolunteerTaskStatus.COMPLETED


def test_check_overdue_tasks_does_not_update_future_task(
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
    event = EventFactory(
        club=club,creator=UserFactory()
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() + timedelta(hours=1),
        status=VolunteerTaskStatus.ASSIGNED,
    )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.post(
        "/api/volunteer-tasks/check-overdue",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["updated"] == 0
    # Future task must remain unchanged
    assert task.status == VolunteerTaskStatus.ASSIGNED


def test_check_overdue_tasks_updates_multiple_tasks(
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
    event = EventFactory(
        club=club,creator=UserFactory()
    )
    overdue_task_1 = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() - timedelta(hours=2),
        status=VolunteerTaskStatus.ASSIGNED,
    )
    overdue_task_2 = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() - timedelta(hours=1),
        status=VolunteerTaskStatus.ASSIGNED,
    )
    future_task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event.creator,
        due_at=datetime.utcnow() + timedelta(hours=1),
        status=VolunteerTaskStatus.ASSIGNED,
    )
    headers = auth_headers(user.email)
    mock_resolve_club_id(user)
    response = client.post(
        "/api/volunteer-tasks/check-overdue",
        headers=headers,
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["updated"] == 2
    assert overdue_task_1.status == VolunteerTaskStatus.MISSED
    assert overdue_task_2.status == VolunteerTaskStatus.MISSED
    assert future_task.status == VolunteerTaskStatus.ASSIGNED


def test_check_overdue_tasks_unauthenticated(
    client,
):
    response = client.post(
        "/api/volunteer-tasks/check-overdue"
    )

    assert response.status_code == 401