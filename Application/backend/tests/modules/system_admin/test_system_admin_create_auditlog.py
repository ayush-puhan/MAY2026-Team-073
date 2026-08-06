from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)
from app.database.models import AuditLog


# 1. log successfull audit info
def test_create_audit_log_success(client,auth_headers,db_session):
    uni = UniversityFactory()
    admin_user = UserFactory(role=UserRole.SYSTEM_ADMIN,university=uni)

    headers = auth_headers(admin_user.email)
    response = client.post(
        "/api/admin/audit-logs",
        headers=headers,
        json={
            "action": "LOGIN",
            "entity_type": "ACCOUNT",
            "entity_id": 1,
            "details": "Loged in"
        },
    )
    body = response.get_json()
    print(body)
    
    assert response.status_code == 201

    assert body["message"] == "Audit log created successfully."
    assert body["audit_log_id"] is not None

    audit = db_session.query(AuditLog).get(body["audit_log_id"])

    assert audit is not None
    assert audit.action == "LOGIN"
    assert audit.entity_type == "ACCOUNT"
    assert audit.entity_id == 1

# 2. Missing Required field
def test_create_audit_log_missing_required_field(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    required_fields = ["action", "entity_type", "entity_id"]
    response = client.post(
        "/api/admin/audit-logs",
        headers=headers,
        json={}
    )

    assert response.status_code == 400
    assert f" is required." in response.get_json()["message"]


# 3.Unauthorized Request
def test_create_audit_log_without_token(client):
    response = client.post(
        "/api/admin/audit-logs",
        json={
            "action": "CREATE",
            "entity_type": "CLUB",
            "entity_id": 1,
        },
    )
    assert response.status_code == 401

# 4. Forbidden 
def test_create_audit_log_forbidden(client,auth_headers,student_user):
    headers = auth_headers(student_user.email)
    response = client.post(
        "/api/admin/audit-logs",
        headers=headers,
        json={
            "action": "CREATE",
            "entity_type": "CLUB",
            "entity_id": 1,
        },
    )

    assert response.status_code == 403

# 5. DataBase Exception
def test_create_audit_log_database_error(client,auth_headers,system_admin_user,monkeypatch):
    def broken_session():
        raise Exception("Database Error")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    
    headers = auth_headers(system_admin_user.email)
    response = client.post(
        "/api/admin/audit-logs",
        headers=headers,
        json={
            "action": "CREATE",
            "entity_type": "CLUB",
            "entity_id": 1,
        },
    )
    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]

    


