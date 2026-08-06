import bcrypt
from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import University, UniversityDomain


# -------------------------------------------------------------------
# Test: Successfully update university details
# -------------------------------------------------------------------
def test_update_university_success(
    client,
    auth_headers,
    system_admin_user,
    db_session,
):
    headers = auth_headers(system_admin_user.email)

    university = UniversityFactory(
        name="Old University",
        domain="old.edu",
        is_active=True,
    )

    response = client.patch(
        f"/api/admin/universities/{university.id}",
        headers=headers,
        json={
            "name": "New University",
            "domain": "new.edu",
            "is_active": False,
        },
    )

    assert response.status_code == 200
    assert response.get_json()["message"] == "University updated successfully"

    db_session.refresh(university)

    assert university.name == "New University"
    assert university.domain == "new.edu"
    assert university.is_active is False


# -------------------------------------------------------------------
# Test: Successfully update banner image
# -------------------------------------------------------------------
def test_update_university_banner(
    client,
    auth_headers,
    system_admin_user,
    db_session,
    monkeypatch,
):
    headers = auth_headers(system_admin_user.email)

    university = UniversityFactory(
        banner="uploads/old_banner.png",
    )
    deleted_files = []
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.save_base64_image",
        lambda img: "uploads/new_banner.png",
    )

    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.delete_uploaded_file",
        lambda path: deleted_files.append(path),
    )

    response = client.patch(
        f"/api/admin/universities/{university.id}",
        headers=headers,
        json={
            "name": university.name,
            "domain": university.domain,
            "is_active": True,
            "banner": "data:image/png;base64,fakeimage",
        },
    )
    assert response.status_code == 200
    db_session.refresh(university)

    assert university.banner == "uploads/new_banner.png"
    assert deleted_files == ["uploads/old_banner.png"]


# -------------------------------------------------------------------
# Test: Successfully add allowed domains
# -------------------------------------------------------------------
def test_update_university_allowed_domains(client,auth_headers,system_admin_user,db_session,):
    headers = auth_headers(system_admin_user.email)
    university = UniversityFactory()
    response = client.patch(
        f"/api/admin/universities/{university.id}",
        headers=headers,
        json={
            "name": university.name,
            "domain": university.domain,
            "is_active": True,
            "allowed_domains": [
                {"domain": "student.test.edu"},
                {"domain": "faculty.test.edu"},
            ],
        },
    )
    assert response.status_code == 200
    domains = (
        db_session.query(UniversityDomain)
        .filter_by(university_id=university.id)
        .all()
    )
    assert len(domains) == 2

# -------------------------------------------------------------------
# Test: University not found
# -------------------------------------------------------------------
def test_update_university_not_found(
    client,
    auth_headers,
    system_admin_user,
):
    headers = auth_headers(system_admin_user.email)
    response = client.patch(
        "/api/admin/universities/999999",
        headers=headers,
        json={
            "name": "ABC",
            "domain": "abc.edu",
            "is_active": True,
        },
    )
    assert response.status_code == 404
    assert response.get_json()["message"] == "University Not found."


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_update_university_unauthorized(client):
    response = client.patch(
        "/api/admin/universities/1",
        json={},
    )
    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Forbidden request
# -------------------------------------------------------------------
def test_update_university_forbidden(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)
    response = client.patch(
        "/api/admin/universities/1",
        headers=headers,
        json={},
    )
    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_update_university_database_error(
    client,
    auth_headers,
    system_admin_user,
    monkeypatch,
):
    headers = auth_headers(system_admin_user.email)
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session,
    )
    response = client.patch(
        "/api/admin/universities/1",
        headers=headers,
        json={
            "name": "ABC",
            "domain": "abc.edu",
            "is_active": True,
        },
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]