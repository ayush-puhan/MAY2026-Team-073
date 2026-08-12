from app.database.enums import (
    UserRole,
    TicketStatus
)
from db_factory.factory import (
    UserFactory,ClubFactory,EventFactory,UniversityFactory,SupportTicketFactory,AuditLogFactory
)

# getting audit log 
def test_get_audit_logs_success(
    client,
    auth_headers,
    system_admin_user
):
    user= UserFactory()
    university= UniversityFactory()
    al = AuditLogFactory(user=user,university_id=university.id,action='LOGIN')

    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/audit-logs",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["action"] == 'LOGIN'
    assert "entity_type" in data[0]
    assert "details" in data[0]



# No audit log 
def test_get_audit_logs_empty(client,auth_headers,system_admin_user):
    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/audit-logs",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.get_json() == []

# Unauthorized request
def test_get_audit_logs_without_token(client):
    response = client.get(
        "/api/admin/audit-logs"
    )
    assert response.status_code == 401


#4. Test limit parameter
def test_get_audit_logs_limit(client,auth_headers,system_admin_user):
    user= UserFactory()
    university= UniversityFactory()
    al1 = AuditLogFactory(user=user,university_id=university.id,action='LOGIN')
    al2 = AuditLogFactory(user=user,university_id=university.id,action='CREATE')
    al2 = AuditLogFactory(user=user,university_id=university.id,action='UPDATE')


    headers = auth_headers(system_admin_user.email)
    response = client.get(
        "/api/admin/audit-logs?limit=2",
        headers=headers,
    )
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2


# 5.Database exception
def test_get_audit_logs_database_error(client,auth_headers,system_admin_user,monkeypatch):

    headers = auth_headers(system_admin_user.email)
    def broken_session():
        raise Exception("Database failure")
    monkeypatch.setattr(
        "app.modules.system_admin.admin_routes.get_session",
        broken_session
    )
    response = client.get(
        "/api/admin/audit-logs",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database failure" in response.get_json()["message"]