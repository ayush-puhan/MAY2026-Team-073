from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.transfer_presidency  as tp_module

def test_get_my_tasks_success(
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
    event_creator=UserFactory(email="evcr@campus.edu",university=university)
    event = EventFactory(
        club=club,
        creator=event_creator
    )
    task = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership,
        assigner=event_creator
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/tasks?user_id={user.id}",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["id"] == task.id


def test_get_my_tasks_returns_only_assigned_tasks(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user1 = UserFactory(
        email="member1@campus.edu",
        university=university,
    )
    user2 = UserFactory(
        email="member2@campus.edu",
        university=university,
    )
    membership1 = ClubMembershipFactory(
        user=user1,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    membership2 = ClubMembershipFactory(
        user=user2,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )
    event_creator=UserFactory(email="evcr@campus.edu",university=university)
    event = EventFactory(
        club=club,
        creator=event_creator
    )

    task1 = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership1,
        assigner=event_creator
    )

    task2 = VolunteerAssignmentFactory(
        event=event,
        assignee_membership=membership2,
        assigner=event_creator
    )
    headers = auth_headers(user1.email)

    response = client.get(
        f"/api/clubs/{club.id}/tasks?user_id={user1.id}",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["id"] == task1.id
    assert body[0]["id"] != task2.id



def test_get_my_tasks_membership_not_found(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="nonmember@campus.edu",
        university=university,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/tasks?user_id={user.id}",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found"



def test_get_my_tasks_unapproved_membership(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    user = UserFactory(
        email="pending@campus.edu",
        university=university,
    )
    ClubMembershipFactory(
        user=user,
        club=club,
        status=MembershipStatus.PENDING,
        role_in_club=ClubMemberRole.MEMBER,
    )
    headers = auth_headers(user.email)
    response = client.get(
        f"/api/clubs/{club.id}/tasks?user_id={user.id}",
        headers=headers,
    )
    assert response.status_code == 404
    body = response.get_json()
    assert body["message"] == "Membership not found"


def test_get_all_club_tasks_success(
    client,
    auth_headers,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    vc = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=vc,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VOLUNTEER_COORDINATOR,
    )
    event1 = EventFactory(
        club=club,
        creator=UserFactory()
    )
    event2 = EventFactory(
        club=club,
        creator=UserFactory()
    )
    task1 = VolunteerAssignmentFactory(
        event=event1,
        assignee_membership=membership,
        assigner=event1.creator
    )
    task2 = VolunteerAssignmentFactory(
        event=event2,
        assignee_membership=membership,
        assigner=event2.creator
    )
    headers = auth_headers(vc.email)
    response = client.get(
        f"/api/clubs/{club.id}/tasks",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body, list)
    assert len(body) == 2
    task_ids = {task["id"] for task in body}
    assert task1.id in task_ids
    assert task2.id in task_ids



def test_get_all_club_tasks_excludes_other_club_tasks(
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
    vc = UserFactory(
        email="coordinator@campus.edu",
        university=university,
    )
    membership = ClubMembershipFactory(
        user=vc,
        club=club1,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VOLUNTEER_COORDINATOR,
    )
    event1 = EventFactory(
        club=club1,
        creator=UserFactory()
    )

    event2 = EventFactory(
        club=club2,
        creator=UserFactory()
    )

    task1 = VolunteerAssignmentFactory(
        event=event1,
        assignee_membership=membership,
        assigner=event1.creator
    )

    task2 = VolunteerAssignmentFactory(
        event=event2,
        assignee_membership=membership,
        assigner=event2.creator
    )

    headers = auth_headers(vc.email)
    response = client.get(
        f"/api/clubs/{club1.id}/tasks",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    assert body[0]["id"] == task1.id
    assert body[0]["id"] != task2.id



def test_get_my_tasks_unauthenticated(
    client,
):
    university = UniversityFactory()
    club = ClubFactory(
        university=university,
    )
    response = client.get(
        f"/api/clubs/{club.id}/tasks"
    )
    assert response.status_code == 401