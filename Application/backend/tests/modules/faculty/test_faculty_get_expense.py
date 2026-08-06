from app.database.enums import *
from db_factory.factory import *


# -------------------------------------------------------------------
# Test: Successfully retrieve pending expenses (default status)
# -------------------------------------------------------------------
def test_get_faculty_expenses_success(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()
    expense_submitter = UserFactory()
    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    budget = BudgetFactory(
        club=club,
        creator=faculty_advisor_user,
        title="Main Budget",
    )

    ExpenseFactory(
        budget=budget,
        submitter=expense_submitter,
        approval_status=ExpenseStatus.PENDING,
    )

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/expenses",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["budget_title"] == "Main Budget"
    assert body[0]["approval_status"] == ExpenseStatus.PENDING.value


# -------------------------------------------------------------------
# Test: Retrieve approved expenses using query parameter
# -------------------------------------------------------------------
def test_get_faculty_expenses_by_status(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    university = UniversityFactory()
    expense_submitter = UserFactory()

    club = ClubFactory(
        university=university,
        faculty_advisor=faculty_advisor_user,
    )

    budget = BudgetFactory(
        club=club,
        creator=faculty_advisor_user,
        title="Main Budget"
    )

    ExpenseFactory(
        budget=budget,
        submitter=expense_submitter,
        approval_status=ExpenseStatus.APPROVED,
    )

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/expenses?status=APPROVED",
        headers=headers,
    )

    assert response.status_code == 200

    body = response.get_json()

    assert len(body) == 1
    assert body[0]["approval_status"] == ExpenseStatus.APPROVED.value


# -------------------------------------------------------------------
# Test: Advisor requesting another advisor's expenses
# -------------------------------------------------------------------
def test_get_faculty_expenses_forbidden(
    client,
    auth_headers,
    faculty_advisor_user
):
    headers = auth_headers(faculty_advisor_user.email)

    another_advisor = UserFactory(
        role=UserRole.FACULTY_ADVISOR,
    )

    response = client.get(
        f"/api/faculty/{another_advisor.id}/expenses",
        headers=headers,
    )

    assert response.status_code == 403
    assert "Forbidden" in response.get_json()["message"]


# -------------------------------------------------------------------
# Test: No expenses found
# -------------------------------------------------------------------
def test_get_faculty_expenses_empty(
    client,
    auth_headers,
    faculty_advisor_user,
):
    headers = auth_headers(faculty_advisor_user.email)

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/expenses",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == []


# -------------------------------------------------------------------
# Test: Unauthorized request
# -------------------------------------------------------------------
def test_get_faculty_expenses_unauthorized(
    client,
):
    response = client.get(
        "/api/faculty/1/expenses",
    )

    assert response.status_code == 401


# -------------------------------------------------------------------
# Test: Database exception
# -------------------------------------------------------------------
def test_get_faculty_expenses_database_error(
    client,
    auth_headers,
    faculty_advisor_user,
    db_error,
):
    import app.modules.faculty.routes as faculty_module
    db_error(faculty_module)

    headers = auth_headers(faculty_advisor_user.email)

    response = client.get(
        f"/api/faculty/{faculty_advisor_user.id}/expenses",
        headers=headers,
    )

    assert response.status_code == 500
    assert "Database Error" in response.get_json()["message"]