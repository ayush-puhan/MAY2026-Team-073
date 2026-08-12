import bcrypt
from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import User,UniversityDomain,University

# -------------------------------------------------------------------
# Test: Successfully retrieve all universities
# -------------------------------------------------------------------
def test_get_universities_success(
    client,
    auth_headers,
    system_admin_user
):
    headers = auth_headers(system_admin_user.email)
    UniversityFactory(
        name="IIT Madras",
        short_name="IITM",
        domain="iitm.ac.in",
    )
    UniversityFactory(
        name="IIT Bombay",
        short_name="IITB",
        domain="iitb.ac.in",
    )
    response = client.get(
        "/api/admin/universities",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 2

    university = next(u for u in body if u["name"] == "IIT Madras")

    assert university["short_name"] == "IITM"
    assert university["domain"] == "iitm.ac.in"
    assert "id" in university
    assert "logo_url" in university
    assert "address" in university
    assert "website" in university
    assert "banner" in university
    assert "is_active" in university


# -------------------------------------------------------------------
# Test: No universities exist
# -------------------------------------------------------------------
def test_get_universities_empty(
    client,
    auth_headers,
    system_admin_user,
):
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/universities",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == []


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_universities_unauthorized(client):
    response = client.get("/api/admin/universities")
    assert response.status_code == 401

# -------------------------------------------------------------------
# Test: Forbidden request (non-admin)
# -------------------------------------------------------------------
def test_get_universities_forbidden(
    client,
    auth_headers,
    student_user,
):
    headers = auth_headers(student_user.email)
    response = client.get(
        "/api/admin/universities",
        headers=headers,
    )
    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_universities_database_error(
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

    response = client.get(
        "/api/admin/universities",
        headers=headers,
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: Successfully create a university
# -------------------------------------------------------------------
def test_create_university_success(client,auth_headers,system_admin_user,db_session,monkeypatch):
    headers = auth_headers(system_admin_user.email)

    # Avoid actually saving an image
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.save_base64_image",
        lambda img: "uploads/banner.png",
    )

    response = client.post(
        "/api/admin/universities",
        headers=headers,
        json={
            "name": "IIT Madras",
            "domain": "iitm.ac.in",
            "banner": "fake_base64",
            "is_active": True,
        },
    )

    assert response.status_code == 200
    assert "University created successfully" in response.get_json()["message"]

    university = (
        db_session.query(University)
        .filter_by(name="IIT Madras")
        .first()
    )

    assert university is not None
    assert university.domain == "iitm.ac.in"
    assert university.banner == "uploads/banner.png"
    assert university.is_active is True


# -------------------------------------------------------------------
# Test: Successfully create university with allowed domains
# -------------------------------------------------------------------
def test_create_university_with_allowed_domains(client,auth_headers,system_admin_user,db_session,monkeypatch):
    headers = auth_headers(system_admin_user.email)
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.save_base64_image",
        lambda img: "banner.png",
    )

    response = client.post(
        "/api/admin/universities",
        headers=headers,
        json={
            "name": "IIT Bombay",
            "domain": "iitb.ac.in",
            "is_active": True,
            "allowed_domains": [
                {"domain": "iitb.ac.in"},
                {"domain": "student.iitb.ac.in"},
            ],
        },
    )
    assert response.status_code == 200
    university = (
        db_session.query(University)
        .filter_by(name="IIT Bombay")
        .first()
    )

    domains = (
        db_session.query(UniversityDomain)
        .filter_by(university_id=university.id)
        .all()
    )
    assert len(domains) == 2


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_create_university_unauthorized(client):
    response = client.post(
        "/api/admin/universities",
        json={},
    )
    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Forbidden request
# -------------------------------------------------------------------
def test_create_university_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.post(
        "/api/admin/universities",
        headers=headers,
        json={},
    )
    assert response.status_code == 403


# -------------------------------------------------------------------
# Test: Image saving failure
# -------------------------------------------------------------------
def test_create_university_image_error(client,auth_headers,system_admin_user,monkeypatch,):
    headers = auth_headers(system_admin_user.email)
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.save_base64_image",
        lambda img: (_ for _ in ()).throw(Exception("Image upload failed")),
    )

    response = client.post(
        "/api/admin/universities",
        headers=headers,
        json={
            "name": "Test University",
            "domain": "test.edu",
            "banner": "fake_image",
            "is_active": True,
        },
    )
    assert response.status_code == 500
    assert "Image upload failed" in response.get_json()["message"]

# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_create_university_database_error(client,auth_headers,system_admin_user,monkeypatch,
):
    headers = auth_headers(system_admin_user.email)
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session,
    )
    response = client.post(
        "/api/admin/universities",
        headers=headers,
        json={
            "name": "ABC University",
            "domain": "abc.edu",
            "is_active": True,
        },
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]