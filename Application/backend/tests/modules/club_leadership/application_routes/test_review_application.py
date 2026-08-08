from app.database.enums import *
from db_factory.factory import *
from app.database.models import *
import app.modules.club_leadership.application_routes  as club_application_module


# approve successfully
def test_review_application_approve_success(
    client,
    auth_headers,
    db_session,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory(email='pres@campus.edu')
    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant = UserFactory(email='applicant1@campus.edu')
    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": "approved",
            "review_comments": "Ooie Approved ho geya, laddu khilao garibbo",
        },
    )
    
    body = response.get_json()
    assert response.status_code == 200

    print(body)
    assert body["application"]["status"] == "approved"
    assert body["application"]["reviewed_by"] == reviewer.id

    membership = (
        db_session.query(ClubMembership)
        .filter(
            ClubMembership.user_id == applicant.id,
            ClubMembership.club_id == club.id,
        )
        .first()
    )

    assert membership is not None
    assert membership.status == MembershipStatus.APPROVED
    assert membership.role_in_club == ClubMemberRole.MEMBER
    assert membership.approved_by == reviewer.id


def test_review_application_reject_success(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant = UserFactory()

    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": MembershipStatus.REJECTED.value,
            "review_comments": "Insufficient experience.",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["message"] == "Application reviewed successfully."

    result = body["application"]

    assert result["id"] == application.id
    assert result["status"] == "rejected"
    assert result["reviewed_by"] == reviewer.id
    assert result["review_comments"] == "Insufficient experience."



#
def test_review_application_using_decision_field(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()
    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.VICE_PRESIDENT,
    )
    applicant = UserFactory()
    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "decision": MembershipStatus.REJECTED.value,
            "review_comments": "Rejected.",
        },
    )

    assert response.status_code == 200

    body = response.get_json()

    assert body["application"]["status"] == "rejected"



#
def test_review_application_no_body(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        "/api/club-applications/1/review",
        headers=headers,
        json={}
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Request body required."
    )


#
def test_review_application_missing_status(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        "/api/club-applications/1/review",
        headers=headers,
        json={
            "review_comments": "No decision provided.",
        },
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Status/decision is required."
    )


#
def test_review_application_invalid_status(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        "/api/club-applications/1/review",
        headers=headers,
        json={
            "status": "invalid_status",
        },
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Invalid application status."
    )


#
def test_review_application_not_found(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        "/api/club-applications/99999/review",
        headers=headers,
        json={
            "status": MembershipStatus.APPROVED.value,
        },
    )

    assert response.status_code == 404

    assert response.get_json()["message"] == (
        "Application not found."
    )



    #
def test_review_application_already_reviewed(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant = UserFactory()

    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.APPROVED,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": MembershipStatus.REJECTED.value,
        },
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "Application already reviewed."
    )



#
def test_review_application_user_already_member(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())

    reviewer = UserFactory()

    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant = UserFactory()

    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    # Applicant is already a member
    ClubMembershipFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": MembershipStatus.APPROVED.value,
        },
    )

    assert response.status_code == 400

    assert response.get_json()["message"] == (
        "User already has membership."
    )



#
def test_review_application_forbidden_for_member(
    client,
    auth_headers,
    mock_resolve_club_id
):
    club = ClubFactory(university=UniversityFactory())

    member = UserFactory()

    ClubMembershipFactory(
        user=member,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.MEMBER,
    )

    applicant = UserFactory()

    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(member.email)
    mock_resolve_club_id(member)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": MembershipStatus.APPROVED.value,
        },
    )

    assert response.status_code == 403


#
def test_review_application_unauthorized(client):
    response = client.patch(
        "/api/club-applications/1/review",
        json={
            "status": MembershipStatus.APPROVED.value,
        },
    )

    assert response.status_code == 401


# Database error handelling check
def test_get_database_error(
    client,
    auth_headers,
    db_error,
    mock_resolve_club_id
):
    import app.modules.club_leadership.application_routes  as club_application_module
    club = ClubFactory(university=UniversityFactory())
    reviewer = UserFactory(email='pres@campus.edu')
    ClubMembershipFactory(
        user=reviewer,
        club=club,
        status=MembershipStatus.APPROVED,
        role_in_club=ClubMemberRole.PRESIDENT,
    )

    applicant = UserFactory(email='applicant1@campus.edu')
    application = ClubJoinApplicationFactory(
        user=applicant,
        club=club,
        status=MembershipStatus.PENDING,
    )

    headers = auth_headers(reviewer.email)
    mock_resolve_club_id(reviewer)
    db_error(club_application_module)
    response = client.patch(
        f"/api/club-applications/{application.id}/review",
        headers=headers,
        json={
            "status": "approved",
            "review_comments": "Ooie Approved ho geya, laddu khilao garibbo",
        },
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]